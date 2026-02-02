"""
M-Pesa Service
Logic for interacting with Safaricom Daraja API
"""

import requests
import base64
from datetime import datetime
from flask import current_app


class MpesaService:
    """Service class for M-Pesa Daraja API integration."""

    BASE_URL = "https://api.safaricom.co.ke"
    OAUTH_URL = f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    STK_PUSH_URL = f"{BASE_URL}/mpesa/stkpush/v1/processrequest"
    STK_QUERY_URL = f"{BASE_URL}/mpesa/stkpushquery/v1/query"
    B2C_URL = f"{BASE_URL}/mpesa/b2c/v1/singlepayment/send"

    @classmethod
    def _get_access_token(cls):
        """Get OAuth access token."""
        from app import config

        consumer_key = config.MPESA_CONSUMER_KEY
        consumer_secret = config.MPESA_CONSUMER_SECRET

        auth_string = base64.b64encode(
            f"{consumer_key}:{consumer_secret}".encode()
        ).decode()

        headers = {"Authorization": f"Basic {auth_string}"}
        response = requests.get(cls.OAUTH_URL, headers=headers)

        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            raise Exception(f"Failed to get access token: {response.text}")

    @classmethod
    def _get_headers(cls):
        """Get headers with access token."""
        access_token = cls._get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    @classmethod
    def initiate_stk_push(
        cls, phone_number, amount, account_reference, transaction_desc
    ):
        """
        Initiate M-Pesa STK Push.

        Args:
            phone_number: Customer phone number
            amount: Amount to charge
            account_reference: Account reference
            transaction_desc: Transaction description

        Returns:
            dict: API response
        """
        from app import config

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(
            f"{config.MPESA_BUSINESS_SHORT_CODE}{config.MPESA_PASSKEY}{timestamp}".encode()
        ).decode()

        headers = cls._get_headers()

        payload = {
            "BusinessShortCode": config.MPESA_BUSINESS_SHORT_CODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": config.MPESA_BUSINESS_SHORT_CODE,
            "PhoneNumber": phone_number,
            "CallBackURL": config.MPESA_CALLBACK_URL,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc,
        }

        response = requests.post(cls.STK_PUSH_URL, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"STK Push failed: {response.text}")

    @classmethod
    def query_stk_status(cls, checkout_request_id):
        """Query STK Push status."""
        from app import config

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(
            f"{config.MPESA_BUSINESS_SHORT_CODE}{config.MPESA_PASSKEY}{timestamp}".encode()
        ).decode()

        headers = cls._get_headers()

        payload = {
            "BusinessShortCode": config.MPESA_BUSINESS_SHORT_CODE,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id,
        }

        response = requests.post(cls.STK_QUERY_URL, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"STK Query failed: {response.text}")

    @classmethod
    def send_b2c_payment(cls, phone_number, amount, occasion="Payout"):
        """Send B2C payment to customer (farmer payouts)."""
        from app import config

        headers = cls._get_headers()

        payload = {
            "InitiatorName": config.MPESA_INITIATOR_NAME,
            "SecurityCredential": config.MPESA_SECURITY_CREDENTIAL,
            "CommandID": "BusinessPayment",
            "Amount": amount,
            "PartyA": config.MPESA_BUSINESS_SHORT_CODE,
            "PartyB": phone_number,
            "Remarks": "FarmAT Payout",
            "QueueTimeOutURL": f"{config.MPESA_CALLBACK_URL}/b2c/timeout",
            "ResultURL": f"{config.MPESA_CALLBACK_URL}/b2c/result",
            "Occasion": occasion,
        }

        response = requests.post(cls.B2C_URL, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"B2C payment failed: {response.text}")
