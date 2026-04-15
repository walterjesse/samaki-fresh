from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from decimal import Decimal
import requests
from plugin.service_fee import calculate_service_fee

from plugin.paginate_queryset import paginate_queryset
from store import models as store_models
from customer import models as customer_models
from vendor import models as vendor_models
from userauths import models as userauths_models
from customer.models import Wishlist
from plugin.tax_calculation import tax_calculation
from plugin.exchange_rate import convert_usd_to_inr, convert_usd_to_kobo, convert_usd_to_ngn

def clear_cart_items(request):
    try:
        cart_id = request.session['cart_id']
        store_models.Cart.objects.filter(cart_id=cart_id).delete()
    except:
        pass
    return

def index(request):
    from django.core.cache import cache
    from django.db.models import Prefetch, Count
    
    # Cache products and categories for 1 hour
    cache_key = 'homepage_products'
    products = cache.get(cache_key)
    if not products:
        products = store_models.Product.objects.filter(
            status="Published"
        ).select_related(
            'category', 'vendor'
        ).prefetch_related(
            'reviews'
        ).order_by('-date')[:12]
        cache.set(cache_key, products, 3600)
    
    categories = cache.get('all_categories')
    if not categories:
        categories = store_models.Category.objects.all()
        cache.set('all_categories', categories, 3600)
    
    context = {
        "products": products,
        "categories": categories,
    }
    return render(request, "store/index.html", context)

def shop(request):
    from django.db.models import Prefetch
    products_list = store_models.Product.objects.filter(
        status="Published"
    ).select_related(
        'category', 'vendor'
    ).prefetch_related(
        'reviews'
    ).order_by('-date')
    
    categories = store_models.Category.objects.all()
    colors = store_models.VariantItem.objects.filter(variant__name='Color').values('title', 'content').distinct()
    sizes = store_models.VariantItem.objects.filter(variant__name='Size').values('title', 'content').distinct()
    item_display = [
        {"id": "1", "value": 1},
        {"id": "2", "value": 2},
        {"id": "3", "value": 3},
        {"id": "40", "value": 40},
        {"id": "50", "value": 50},
        {"id": "100", "value": 100},
    ]

    ratings = [
        {"id": "1", "value": "★☆☆☆☆"},
        {"id": "2", "value": "★★☆☆☆"},
        {"id": "3", "value": "★★★☆☆"},
        {"id": "4", "value": "★★★★☆"},
        {"id": "5", "value": "★★★★★"},
    ]

    prices = [
        {"id": "lowest", "value": "Highest to Lowest"},
        {"id": "highest", "value": "Lowest to Highest"},
    ]


    print(sizes)

    products = paginate_queryset(request, products_list, 10)

    context = {
        "products": products,
        "products_list": products_list,
        "categories": categories,
         'colors': colors,
        'sizes': sizes,
        'item_display': item_display,
        'ratings': ratings,
        'prices': prices,
    }
    return render(request, "store/shop.html", context)

def category(request, id):
    category = store_models.Category.objects.get(id=id)
    products_list = store_models.Product.objects.filter(
        status="Published", category=category
    ).select_related(
        'category', 'vendor'
    ).prefetch_related(
        'reviews'
    ).order_by('-date')

    query = request.GET.get("q")
    if query:
        products_list = products_list.filter(name__icontains=query)

    products = paginate_queryset(request, products_list, 10)

    context = {
        "products": products,
        "products_list": products_list,
        "category": category,
    }
    return render(request, "store/category.html", context)

def vendors(request):
    vendors = userauths_models.Profile.objects.filter(user_type="Shop Owner")
    
    context = {
        "vendors": vendors
    }
    return render(request, "store/vendors.html", context)

def product_detail(request, slug):
    product = store_models.Product.objects.select_related(
        'category', 'vendor'
    ).prefetch_related(
        'reviews'
    ).get(status="Published", slug=slug)

    # Increment view count
    try:
        product.view_count += 1
        product.save(update_fields=['view_count'])
    except Exception:
        pass  # Don't block page load if view count fails

    product_stock_range = range(1, product.stock + 1)

    related_products = store_models.Product.objects.filter(
        category=product.category, status="Published"
    ).exclude(
        id=product.id
    ).select_related(
        'category', 'vendor'
    ).prefetch_related(
        'reviews'
    )[:6]

    context = {
        "product": product,
        "product_stock_range": product_stock_range,
        "related_products": related_products,
    }
    return render(request, "store/product_detail.html", context)

def add_to_cart(request):
    # Get parameters from the request (ID, color, size, quantity, cart_id)
    id = request.POST.get("id") or request.POST.get("product_id")
    qty = request.POST.get("qty")
    color = request.POST.get("color", "")
    size = request.POST.get("size", "")
    cart_id = request.POST.get("cart_id") or request.session.get('cart_id')

    # Validate quantity input (prevent invalid values)
    try:
        qty = int(qty) if qty else 1
        if qty < 1 or qty > 1000:
            messages.error(request, "Quantity must be between 1 and 1000")
            return redirect("store:index")
    except (ValueError, TypeError):
        messages.error(request, "Invalid quantity entered")
        return redirect("store:index")

    # Sanitize string inputs to prevent XSS
    color = str(color).strip()[:100] if color else ""
    size = str(size).strip()[:100] if size else ""

    # Generate cart_id if not provided
    if not cart_id:
        import uuid
        cart_id = str(uuid.uuid4())

    request.session['cart_id'] = cart_id
    request.session.save()  # Ensure session is saved

    # Validate product ID is numeric
    try:
        id = int(id)
    except (ValueError, TypeError):
        messages.error(request, "Invalid product ID")
        return redirect("store:index")

    # Try to fetch the product, return an error if it doesn't exist
    try:
        product = store_models.Product.objects.get(id=id, status="Published")
    except store_models.Product.DoesNotExist:
        messages.error(request, "Product not found")
        return redirect("store:index")

    # Check if the item is already in the cart
    existing_cart_item = store_models.Cart.objects.filter(cart_id=cart_id, product=product).first()

    # Check if quantity that user is adding exceed item stock qty
    if qty > product.stock:
        messages.error(request, f"Only {product.stock} items available in stock")
        return redirect("store:product_detail", product.slug)

    # If the item is not in the cart, create a new cart entry
    if not existing_cart_item:
        cart = store_models.Cart()
        cart.product = product
        cart.qty = qty
        cart.price = product.price
        cart.color = color
        cart.size = size
        cart.sub_total = Decimal(product.price) * Decimal(qty)
        cart.shipping = Decimal(product.shipping) * Decimal(qty)
        cart.total = cart.sub_total + cart.shipping
        cart.user = request.user if request.user.is_authenticated else None
        cart.cart_id = cart_id
        cart.save()

        messages.success(request, "Item added to cart")
    else:
        # If the item exists in the cart, update the existing entry
        existing_cart_item.color = color
        existing_cart_item.size = size
        existing_cart_item.qty = int(existing_cart_item.qty) + int(qty)
        existing_cart_item.price = product.price
        existing_cart_item.sub_total = Decimal(product.price) * Decimal(existing_cart_item.qty)
        existing_cart_item.shipping = Decimal(product.shipping) * Decimal(existing_cart_item.qty)
        existing_cart_item.total = existing_cart_item.sub_total + existing_cart_item.shipping
        existing_cart_item.user = request.user if request.user.is_authenticated else None
        existing_cart_item.save()

        messages.success(request, "Item quantity updated in cart")

    return redirect("store:cart")

def cart(request):
    if "cart_id" in request.session:
        cart_id = request.session['cart_id']
    else:
        cart_id = None

    items = store_models.Cart.objects.filter(cart_id=cart_id)
    cart_sub_total = sum([(item.sub_total or Decimal('0')) for item in items])
    cart_shipping_total = sum([(item.shipping or Decimal('0')) for item in items])
    # For demo, use 'India' as default country for tax; in real use, get from user/address
    country = None
    if items and hasattr(items[0], 'user') and items[0].user and hasattr(items[0].user, 'address_set'):
        address = items[0].user.address_set.first()
        if address:
            country = getattr(address, 'country', None)
    if not country:
        country = 'India'
    from plugin.tax_calculation import tax_calculation
    from plugin.service_fee import calculate_service_fee
    cart_tax = Decimal(str(tax_calculation(country, cart_sub_total)))
    pre_fee_total = cart_sub_total + cart_shipping_total + cart_tax
    cart_service_fee = Decimal(str(calculate_service_fee(pre_fee_total)))
    cart_total = pre_fee_total + cart_service_fee

    try:
        addresses = customer_models.Address.objects.filter(user=request.user)
    except:
        addresses = None

    if not items:
        messages.warning(request, "No item in cart")
        return redirect("store:index")

    context = {
        "cart_items": items,
        "cart_sub_total": cart_sub_total,
        "cart_shipping_total": cart_shipping_total,
        "cart_tax": cart_tax,
        "cart_service_fee": cart_service_fee,
        "cart_total": cart_total,
        "discount": 0,
        "final_total": cart_total,
        "addresses": addresses,
    }
    return render(request, "store/cart.html", context)

def update_cart_item(request):
    if request.method == "POST":
        cart_item_id = request.POST.get("cart_item_id")
        action = request.POST.get("action")

        # Validate input
        if not cart_item_id or not action:
            messages.error(request, "Invalid request")
            return redirect("store:cart")
        
        # Validate action is one of allowed values
        if action not in ["increase", "decrease"]:
            messages.error(request, "Invalid action")
            return redirect("store:cart")
        
        # Validate cart_item_id is numeric
        try:
            cart_item_id = int(cart_item_id)
        except (ValueError, TypeError):
            messages.error(request, "Invalid cart item")
            return redirect("store:cart")

        try:
            # Ensure user can only modify their own cart items
            cart_id = request.session.get('cart_id')
            if not cart_id:
                messages.error(request, "Cart session not found")
                return redirect("store:cart")
            
            cart_item = store_models.Cart.objects.get(id=cart_item_id, cart_id=cart_id)
            product = cart_item.product

            if action == "increase":
                if cart_item.qty < product.stock:
                    cart_item.qty += 1
                    cart_item.sub_total = Decimal(str(product.price)) * Decimal(str(cart_item.qty))
                    cart_item.shipping = Decimal(str(product.shipping)) * Decimal(str(cart_item.qty))
                    cart_item.total = cart_item.sub_total + cart_item.shipping
                    cart_item.save()
                else:
                    messages.warning(request, "Maximum stock reached")
            elif action == "decrease":
                if cart_item.qty > 1:
                    cart_item.qty -= 1
                    cart_item.sub_total = Decimal(str(product.price)) * Decimal(str(cart_item.qty))
                    cart_item.shipping = Decimal(str(product.shipping)) * Decimal(str(cart_item.qty))
                    cart_item.total = cart_item.sub_total + cart_item.shipping
                    cart_item.save()
                else:
                    messages.warning(request, "Minimum quantity is 1")

            messages.success(request, "Cart updated")
        except store_models.Cart.DoesNotExist:
            messages.error(request, "Cart item not found")

        return redirect("store:cart")

    return redirect("store:cart")

def delete_cart_item(request):
    if request.method == "POST":
        cart_item_id = request.POST.get("cart_item_id")

        if not cart_item_id:
            messages.error(request, "Invalid cart item")
            return redirect("store:cart")

        try:
            cart_item = store_models.Cart.objects.get(id=cart_item_id)
            cart_item.delete()
            messages.success(request, "Item removed from cart")
        except store_models.Cart.DoesNotExist:
            messages.error(request, "Cart item not found")

        return redirect("store:cart")

    return redirect("store:cart")

def create_order(request):
    if request.method != "POST":
        return redirect("store:cart")

    payment_method = request.POST.get("payment_method", "mpesa")
    if payment_method not in ["mpesa", "cod"]:
        payment_method = "mpesa"

    address_id = request.POST.get("address")
    if not address_id:
        messages.warning(request, "Please select an address to continue")
        return redirect("store:cart")

    address = customer_models.Address.objects.filter(user=request.user, id=address_id).first()
    if not address:
        messages.error(request, "Selected address not found")
        return redirect("store:cart")

    cart_id = request.session.get("cart_id")
    if not cart_id:
        messages.warning(request, "Your cart is empty")
        return redirect("store:cart")

    items = store_models.Cart.objects.filter(cart_id=cart_id)
    if not items.exists():
        messages.warning(request, "Your cart is empty")
        return redirect("store:cart")

    # Recalculate everything from cart items to avoid stale/incorrect totals.
    cart_sub_total = sum((item.sub_total or Decimal("0.00")) for item in items)
    # Shipping rule selected: sum per-product shipping from cart items.
    cart_shipping_total = sum((item.shipping or Decimal("0.00")) for item in items)

    order = store_models.Order()
    order.sub_total = cart_sub_total
    order.customer = request.user
    order.address = address
    order.shipping = cart_shipping_total
    order.tax = Decimal(str(tax_calculation(address.country, cart_sub_total)))
    pre_fee_total = order.sub_total + order.shipping + order.tax
    order.service_fee = Decimal(str(calculate_service_fee(pre_fee_total)))
    order.total = pre_fee_total + order.service_fee
    order.initial_total = order.total
    order.payment_method = payment_method
    order.save()

    for i in items:
        line_sub_total = i.sub_total or (Decimal(i.price or 0) * Decimal(i.qty or 0))
        line_shipping = i.shipping or Decimal("0.00")
        line_tax = Decimal(str(tax_calculation(address.country, line_sub_total)))
        line_total = line_sub_total + line_shipping + line_tax

        store_models.OrderItem.objects.create(
            order=order,
            product=i.product,
            qty=i.qty,
            color=i.color,
            size=i.size,
            price=i.price,
            sub_total=line_sub_total,
            shipping=line_shipping,
            tax=line_tax,
            total=line_total,
            initial_total=line_total,
            vendor=i.product.vendor
        )

        if i.product.vendor:
            order.vendors.add(i.product.vendor)

    return redirect("store:checkout", order.order_id)

def coupon_apply(request, order_id):
    print("Order Id ========", order_id)
    
    try:
        order = store_models.Order.objects.get(order_id=order_id)
        order_items = store_models.OrderItem.objects.filter(order=order)
    except store_models.Order.DoesNotExist:
        messages.error(request, "Order not found")
        return redirect("store:cart")

    if request.method == 'POST':
        coupon_code = request.POST.get("coupon_code")
        
        if not coupon_code:
            messages.error(request, "No coupon entered")
            return redirect("store:checkout", order.order_id)
            
        try:
            coupon = store_models.Coupon.objects.get(code=coupon_code)
        except store_models.Coupon.DoesNotExist:
            messages.error(request, "Coupon does not exist")
            return redirect("store:checkout", order.order_id)
        
        if coupon in order.coupons.all():
            messages.warning(request, "Coupon already activated")
            return redirect("store:checkout", order.order_id)
        else:
            # Assuming coupon applies to specific vendor items, not globally
            total_discount = 0
            for item in order_items:
                if coupon.vendor == item.product.vendor and coupon not in item.coupon.all():
                    item_discount = item.total * coupon.discount / 100  # Discount for this item
                    total_discount += item_discount

                    item.coupon.add(coupon) 
                    item.total -= item_discount
                    item.saved += item_discount
                    item.save()

            # Apply total discount to the order after processing all items
            if total_discount > 0:
                order.coupons.add(coupon)
                order.total -= total_discount
                order.sub_total -= total_discount
                order.saved += total_discount
                order.save()
        
        messages.success(request, "Coupon Activated")
        return redirect("store:checkout", order.order_id)

def checkout(request, order_id):
    order = store_models.Order.objects.get(order_id=order_id)

    context = {
        "order": order,
    }

    return render(request, "store/checkout.html", context)

def payment_status(request, order_id):
    order = store_models.Order.objects.get(order_id=order_id)
    payment_status = request.GET.get("payment_status")

    context = {
        "order": order,
        "payment_status": payment_status
    }
    return render(request, "store/payment_status.html", context)

def filter_products(request):
    products = store_models.Product.objects.all()

    # Get filters from the AJAX request
    categories = request.GET.getlist('categories[]')
    rating = request.GET.getlist('rating[]')
    sizes = request.GET.getlist('sizes[]')
    colors = request.GET.getlist('colors[]')
    price_order = request.GET.get('prices')
    search_filter = request.GET.get('searchFilter')
    display = request.GET.get('display')

    print("categories =======", categories)
    print("rating =======", rating)
    print("sizes =======", sizes)
    print("colors =======", colors)
    print("price_order =======", price_order)
    print("search_filter =======", search_filter)
    print("display =======", display)

   
    # Apply category filtering
    if categories:
        products = products.filter(category__id__in=categories)

    # Apply rating filtering
    if rating:
        products = products.filter(reviews__rating__in=rating).distinct()

    

    # Apply size filtering
    if sizes:
        products = products.filter(variant__variant_items__content__in=sizes).distinct()

    # Apply color filtering
    if colors:
        products = products.filter(variant__variant_items__content__in=colors).distinct()

    # Apply price ordering
    if price_order == 'lowest':
        products = products.order_by('-price')
    elif price_order == 'highest':
        products = products.order_by('price')

    # Apply search filter
    if search_filter:
        products = products.filter(name__icontains=search_filter)

    if display:
        products = products.filter()[:int(display)]


    # Render the filtered products as HTML using render_to_string
    html = render_to_string('partials/_store.html', {'products': products})

    return JsonResponse({'html': html, 'product_count': products.count()})

def order_tracker_page(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        return redirect("store:order_tracker_detail", item_id)
    
    return render(request, "store/order_tracker_page.html")

def order_tracker_detail(request, item_id):
    try:
        item = store_models.OrderItem.objects.filter(models.Q(item_id=item_id) | models.Q(tracking_id=item_id)).first()
    except:
        item = None
        messages.error(request, "Order not found!")
        return redirect("store:order_tracker_page")
    
    context = {
        "item": item,
    }
    return render(request, "store/order_tracker.html", context)

def about(request):
    return render(request, "pages/about.html")

def contact(request):
    if request.method == "POST":
        # Input validation for contact form
        full_name = str(request.POST.get("full_name", "")).strip()[:200]
        email = str(request.POST.get("email", "")).strip()[:254]
        subject = str(request.POST.get("subject", "")).strip()[:200]
        message = str(request.POST.get("message", "")).strip()[:5000]
        
        # Validate required fields
        if not full_name or not email or not subject or not message:
            messages.error(request, "All fields are required")
            return render(request, "pages/contact.html")
        
        # Basic email validation
        if "@" not in email or "." not in email:
            messages.error(request, "Please enter a valid email address")
            return render(request, "pages/contact.html")

        try:
            userauths_models.ContactMessage.objects.create(
                full_name=full_name,
                email=email,
                subject=subject,
                message=message
            )
        except Exception as e:
            messages.error(request, "Failed to send message. Please try again.")
            return render(request, "pages/contact.html")
        messages.success(request, "Message sent successfully!")
        return redirect("store:index")

    return render(request, "pages/contact.html")


def add_to_wishlist(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login to add items to wishlist")
        return redirect("userauths:sign-in")

    product_id = request.GET.get("product_id")
    if not product_id:
        messages.error(request, "Invalid product ID.")
        return redirect("store:index")

    try:
        product = store_models.Product.objects.get(id=product_id)
    except store_models.Product.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect("store:index")

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    if created:
        messages.success(request, "Added to wishlist")
    else:
        messages.info(request, "Already in wishlist")

    # Redirect to product detail page
    return redirect("store:product_detail", product.slug)


def wishlist(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login to view wishlist")
        return redirect("userauths:sign-in")
    
    wishlist_items = Wishlist.objects.filter(user=request.user)
    
    context = {
        "wishlist_items": wishlist_items
    }
    return render(request, "store/wishlist.html", context)


def remove_from_wishlist(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login to manage wishlist")
        return redirect("userauths:sign-in")
    
    wishlist_id = request.GET.get("wishlist_id")
    wishlist_item = Wishlist.objects.get(id=wishlist_id, user=request.user)
    wishlist_item.delete()
    messages.success(request, "Removed from wishlist")
    
    return redirect("store:wishlist")

def faqs(request):
    return render(request, "pages/faqs.html")

def privacy_policy(request):
    return render(request, "pages/privacy_policy.html")

def terms_conditions(request):
    return render(request, "pages/terms_conditions.html")

def fish_recipes(request):
    return render(request, "pages/fish_recipes.html")