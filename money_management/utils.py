import requests
import decimal
from cachetools import TTLCache, cached

API_KEY = 'a759491564d96e37b646ac05'
API_URL = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/'

cache = TTLCache(maxsize=100, ttl=3600)

@cached(cache)
def get_conversion_rate(from_currency, to_currency):
    try:
        response = requests.get(f'{API_URL}{from_currency}')
        response.raise_for_status()
        data = response.json()

        if 'error' in data:
            raise Exception('Error fetching conversion rate')

        rates = data['conversion_rates']
        if to_currency not in rates:
            raise Exception(f'Conversion rate for {to_currency} not found')

        return decimal.Decimal(rates[to_currency])
    except requests.RequestException as e:
        print(f"Request error: {e}")
        raise Exception('Error fetching conversion rate')
    except Exception as e:
        print(f"General error: {e}")
        raise Exception('Error fetching conversion rate')

def convert_currency(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount

    try:
        conversion_rate = get_conversion_rate(from_currency, to_currency)
        converted_amount = amount * conversion_rate
        return converted_amount.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_UP)
    except Exception as e:
        print(f"Conversion error: {e}")
        return amount
