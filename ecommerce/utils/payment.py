import uuid
from decimal import Decimal


class PaymentService:
    """
    Enterprise Payment Gateway Abstraction Service.
    Supports integration with Stripe, PayPal, and Cash on Delivery.
    """
    @staticmethod
    def process_payment(order, payment_method='CREDIT_CARD', payment_token=None):
        """
        Simulates payment processing with payment provider.
        """
        if payment_method == 'CASH_ON_DELIVERY':
            transaction_id = f"COD-{uuid.uuid4().hex[:10].upper()}"
            return {
                "success": True,
                "transaction_id": transaction_id,
                "message": "Order placed with Cash on Delivery."
            }

        # Mocking successful card/digital payment gateway execution
        transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        return {
            "success": True,
            "transaction_id": transaction_id,
            "amount": float(order.total_price),
            "currency": "USD",
            "message": "Payment processed successfully."
        }

    @staticmethod
    def refund_payment(order):
        """
        Simulates refund processing for cancelled orders.
        """
        refund_id = f"RFD-{uuid.uuid4().hex[:10].upper()}"
        return {
            "success": True,
            "refund_id": refund_id,
            "message": "Refund processed successfully."
        }
