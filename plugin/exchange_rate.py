from decimal import Decimal
import requests
from django.core.cache import cache
from django.views.decorators.cache import cache_page

# Cache exchange rates for 5 hours (18000 seconds)
CACHE_TIMEOUT = 18000

def fetch_exchange_rates():
    """Fetch exchange rates from API with caching."""
    cached_rates = cache.get('exchange_rates')
    if cached_rates:
        return cached_rates
    
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=5)
        response.raise_for_status()
        data = response.json()
        exchange_rates = {
            'INR': Decimal(data['rates']['INR']),
            'NGN': Decimal(data['rates']['NGN'])
        }
        cache.set('exchange_rates', exchange_rates, CACHE_TIMEOUT)
        return exchange_rates
    except Exception as e:
        print(f"Error fetching exchange rates: {e}")
        # Return fallback rates if API fails
        return {'INR': Decimal('83.0'), 'NGN': Decimal('410.0')}

exchange_rates = fetch_exchange_rates()

def get_usd_to_inr_rate():
    return exchange_rates['INR']

def get_usd_to_ngn_rate():
    return exchange_rates['NGN']

def convert_usd_to_inr(usd_amount):
    inr_rate = get_usd_to_inr_rate()
    return usd_amount * inr_rate

def convert_usd_to_kobo(usd_amount):
    ngn_rate = get_usd_to_ngn_rate()
    ngn_amount = usd_amount * ngn_rate
    return int(ngn_amount * 100)  # Convert NGN to Kobo

def convert_usd_to_ngn(usd_amount):
    ngn_rate = get_usd_to_ngn_rate()
    return usd_amount * ngn_rate

