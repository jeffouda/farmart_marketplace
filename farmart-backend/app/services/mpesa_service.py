class MpesaService:
    """
    Handles M-Pesa payment operations.
    Placeholder implementation so backend runs cleanly.
    """

    def initiate_payment(self, phone_number, amount, reference):
        return {
            "status": "success",
            "message": "M-Pesa payment initiated",
            "phone_number": phone_number,
            "amount": amount,
            "reference": reference,
        }

    def confirm_payment(self, transaction_id):
        return {
            "status": "success",
            "transaction_id": transaction_id,
        }


# Singleton instance (used across the app)
mpesa_service = MpesaService()
