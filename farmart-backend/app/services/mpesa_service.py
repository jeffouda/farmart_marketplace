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
