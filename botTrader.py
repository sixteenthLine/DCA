import time
import hashlib
import hmac
import requests

API_KEY = ''
SECRET_KEY = ''

BASE_URL = 'https://contract.mexc.com/api/v1'

def generate_signature(params, secret):
    query_string = '&'.join([f"{key}={value}" for key, value in sorted(params.items())])
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def get_futures_balance():
    endpoint = '/account/balance'
    params = {
        'api_key': API_KEY,
        'timestamp': int(time.time() * 1000),  
    }

    params['sign'] = generate_signature(params, SECRET_KEY)

    try:
        response = requests.get(BASE_URL + endpoint, params=params)
        response.raise_for_status()  
        data = response.json()
        if data.get('code') == 200:  
            return data['data']  
        else:
            print(f"Ошибка: {data.get('msg')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None

balance = get_futures_balance()
if balance:
    print("Фьючерсный баланс:", balance)
