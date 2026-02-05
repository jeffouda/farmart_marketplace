import requests
import base64
from datetime import datetime
from flask import current_app

# Access token

def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    consumer_key = current_app.config['MPESA_CONSUMER_KEY']
    consumer_secret = current_app.config['MPESA_CONSUMER_SECRET']
    
    try:
        response = requests.get(url, auth=(consumer_key, consumer_secret))
        response.raise_for_status()
        return response.json().get('access_token')
    except Exception as e:
        print(f"Error getting token: {e}")
        return None
    
def send_stk_push(phone_number, amount):
    access_token = get_access_token()
    if not access_token:
        return {"error": "Failed to authenticate with Safaricom"}

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    passkey = current_app.config['MPESA_PASSKEY']
    shortcode = current_app.config['MPESA_SHORTCODE']

    # Password = Base64(Shortcode + Passkey + Timestamp)
    password_str = shortcode + passkey + timestamp
    password = base64.b64encode(password_str.encode()).decode('utf-8')

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": current_app.config['MPESA_CALLBACK_URL'],
        "AccountReference": "FarmartPayment",
        "TransactionDesc": "Livestock Purchase"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}