from django.urls import path
from store import views

app_name = "store"

urlpatterns = [
    path("", views.index, name="index"),
    path("shop/", views.shop, name="shop"),
    path("category/<id>/", views.category, name="category"),
    path("detail/<slug>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart, name="cart"),
    path("create_order/", views.create_order, name="create_order"),
    path("checkout/<order_id>/", views.checkout, name="checkout"),
    path("coupon_apply/<order_id>/", views.coupon_apply, name="coupon_apply"),
    path("payment_status/<order_id>/", views.payment_status, name="payment_status"),

    path("filter_products/", views.filter_products, name="filter_products"),
    path("add_to_cart/", views.add_to_cart, name="add_to_cart"),
    path("update_cart_item/", views.update_cart_item, name="update_cart_item"),
    path("delete_cart_item/", views.delete_cart_item, name="delete_cart_item"),


    path("order_tracker_page/", views.order_tracker_page, name="order_tracker_page"),
    path("order_tracker_detail/<item_id>/", views.order_tracker_detail, name="order_tracker_detail"),

    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("faqs/", views.faqs, name="faqs"),
    path("privacy_policy/", views.privacy_policy, name="privacy_policy"),
    path("terms_conditions/", views.terms_conditions, name="terms_conditions"),
    path("fish_recipes/", views.fish_recipes, name="fish_recipes"),
    path("add_to_wishlist/", views.add_to_wishlist, name="add_to_wishlist"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("remove_from_wishlist/", views.remove_from_wishlist, name="remove_from_wishlist"),
    path("vendors/", views.vendors, name="vendors"),
]
