from rest_framework import serializers
from .models import Address, Order, OrderItem, PaymentMethod, OrderStatus


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            'id', 'address_type', 'full_name', 'street_address',
            'city', 'state', 'postal_code', 'country', 'phone_number',
            'is_default', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'price', 'quantity', 'line_total')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'user_email', 'status', 'payment_status',
            'payment_method', 'shipping_address', 'total_price', 'tax_amount',
            'shipping_fee', 'transaction_id', 'items', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'order_number', 'user_email', 'created_at', 'updated_at')


class CheckoutSerializer(serializers.Serializer):
    address_id = serializers.IntegerField(required=True)
    payment_method = serializers.ChoiceField(choices=PaymentMethod.choices, default=PaymentMethod.CREDIT_CARD)


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=OrderStatus.choices, required=True)
