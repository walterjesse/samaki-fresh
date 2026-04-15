
from plugin.countries import countries
from django.core.cache import cache

# Cache tax rates for 24 hours
CACHE_TIMEOUT = 86400

def tax_calculation(country, order_total):
    """Calculate tax with caching for improved performance."""
    cache_key = f'tax_{country}_{order_total}'
    cached_tax = cache.get(cache_key)
    
    if cached_tax is not None:
        return cached_tax
    
    tax_rate = 0
    
    for c in countries():
        if country == c['country']:
            tax_rate += int(float(c['tax_rate'])) / 100 * float(order_total)
            break
    
    cache.set(cache_key, tax_rate, CACHE_TIMEOUT)
    return tax_rate
    