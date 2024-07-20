import requests
import decimal

API_KEY = 'a759491564d96e37b646ac05'
API_URL = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/'

def get_conversion_rate(from_currency, to_currency):
    response = requests.get(f'{API_URL}{from_currency}')
    data = response.json()

    if response.status_code != 200 or 'error' in data:
        raise Exception('Error fetching conversion rate')

    rates = data['conversion_rates']
    if to_currency not in rates:
        raise Exception(f'Conversion rate for {to_currency} not found')

    return decimal.Decimal(rates[to_currency])

def convert_currency(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount

    conversion_rate = get_conversion_rate(from_currency, to_currency)
    converted_amount = amount * conversion_rate
    return converted_amount.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_UP)
