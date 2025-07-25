import base64
import requests
from flask import jsonify
from datetime import datetime
from config import Config

def get_token():
    consumer_key = Config.CONSUMER_KEY
    consumer_secret = Config.CONSUMER_SECRET
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    response = requests.get(api_URL, auth=(consumer_key, consumer_secret))
    json_response = response.json()
    return json_response.get("access_token")

def initiate_stk_push(phone_number, amount):
    access_token = get_token()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((Config.BUSINESS_SHORTCODE + Config.PASSKEY + timestamp).encode()).decode()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": Config.BUSINESS_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": Config.BUSINESS_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": Config.CALLBACK_URL,
        "AccountReference": "ChamaManager",
        "TransactionDesc": "Contribution Payment"
    }

    response = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        headers=headers,
        json=payload
    )
    return response.json()
