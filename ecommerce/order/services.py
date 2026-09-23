from django.db import transaction
from rest_framework.exceptions import ValidationError
from decimal import Decimal

from cart.models import Cart
from product.models import Product, ProductStatus
from utils.payment import PaymentService
from .models import Address, Order, OrderItem, OrderStatus, PaymentStatus


class CheckoutService:
    @staticmethod
    @transaction.atomic
    def process_checkout(user, address_id, payment_method='CREDIT_CARD'):
        """
        Executes atomic checkout process:
        1. Validates user cart & stock
        2. Snapshot address & line items
        3. Creates Order & OrderItems
        4. Decrements product inventory
        5. Clears shopping cart
        6. Processes initial payment state
        """
        cart = Cart.objects.filter(user=user).first()
        if not cart or not cart.items.exists():
            raise ValidationError("Your shopping cart is empty.")

        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            raise ValidationError("Invalid shipping address selected.")

        cart_items = cart.items.select_related('product').all()

        # Stock check
        for item in cart_items:
            if not item.product.is_active:
                raise ValidationError(f"Product '{item.product.name}' is no longer available.")
            if item.quantity > item.product.stock:
                raise ValidationError(f"Insufficient stock for '{item.product.name}'. Available: {item.product.stock}.")

        # Totals calculation
        subtotal = cart.subtotal
        tax_amount = cart.tax_estimate
        shipping_fee = Decimal('0.00') if subtotal >= Decimal('100.00') else Decimal('10.00')
        total_price = subtotal + tax_amount + shipping_fee

        # Create Order
        order = Order.objects.create(
            user=user,
            status=OrderStatus.PENDING,
            payment_status=PaymentStatus.UNPAID,
            payment_method=payment_method,
            shipping_address=address.to_dict(),
            total_price=total_price,
            tax_amount=tax_amount,
            shipping_fee=shipping_fee
        )

        # Create OrderItems & update product stock
        for item in cart_items:
            unit_price = item.unit_price
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                price=unit_price,
                quantity=item.quantity
            )

            # Inventory deduction
            product = item.product
            product.stock -= item.quantity
            if product.stock == 0:
                product.status = ProductStatus.OUT_OF_STOCK
            product.save(update_fields=['stock', 'status'])

        # Clear Cart
        cart.items.all().delete()

        # Process Payment via Abstraction Layer
        payment_res = PaymentService.process_payment(order, payment_method=payment_method)
        if payment_res.get('success'):
            order.payment_status = PaymentStatus.PAID
            order.status = OrderStatus.PROCESSING
            order.transaction_id = payment_res.get('transaction_id')
            order.save(update_fields=['payment_status', 'status', 'transaction_id'])

        return order
