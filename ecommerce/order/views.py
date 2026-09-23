from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema, extend_schema_view

from utils.responses import api_response
from utils.payment import PaymentService
from .models import Address, Order, OrderStatus, PaymentStatus
from .serializers import (
    AddressSerializer,
    OrderSerializer,
    CheckoutSerializer,
    OrderStatusUpdateSerializer
)
from .services import CheckoutService


@extend_schema_view(
    list=extend_schema(tags=['Addresses'], summary="List user addresses"),
    create=extend_schema(tags=['Addresses'], summary="Add new user address"),
    retrieve=extend_schema(tags=['Addresses'], summary="Get address details"),
    update=extend_schema(tags=['Addresses'], summary="Update address"),
    partial_update=extend_schema(tags=['Addresses'], summary="Partial update address"),
    destroy=extend_schema(tags=['Addresses'], summary="Delete address")
)
class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Checkout'], summary="Execute Checkout", request=CheckoutSerializer, responses={201: OrderSerializer})
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        address_id = serializer.validated_data['address_id']
        payment_method = serializer.validated_data['payment_method']

        order = CheckoutService.process_checkout(
            user=request.user,
            address_id=address_id,
            payment_method=payment_method
        )

        return api_response(
            success=True,
            message="Order placed successfully.",
            data=OrderSerializer(order).data,
            status_code=status.HTTP_201_CREATED
        )


@extend_schema_view(
    list=extend_schema(tags=['Orders'], summary="List orders (Customer sees own, Admin sees all)"),
    retrieve=extend_schema(tags=['Orders'], summary="Get order details")
)
class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Order.objects.all().select_related('user').prefetch_related('items')
        return Order.objects.filter(user=user).prefetch_related('items')

    @extend_schema(tags=['Orders'], summary="Cancel an existing order")
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()

        if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
            return api_response(
                success=False,
                message=f"Order cannot be cancelled in status '{order.get_status_display()}'.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Restore product stock
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                if item.product.stock > 0 and item.product.status == 'OUT_OF_STOCK':
                    item.product.status = 'PUBLISHED'
                item.product.save(update_fields=['stock', 'status'])

        # Refund if paid
        if order.payment_status == PaymentStatus.PAID:
            PaymentService.refund_payment(order)
            order.payment_status = PaymentStatus.REFUNDED

        order.status = OrderStatus.CANCELLED
        order.save(update_fields=['status', 'payment_status'])

        return api_response(
            success=True,
            message="Order cancelled successfully.",
            data=OrderSerializer(order).data
        )

    @extend_schema(tags=['Orders'], summary="Update order status (Admin only)", request=OrderStatusUpdateSerializer)
    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        order.status = new_status
        order.save(update_fields=['status'])

        return api_response(
            success=True,
            message=f"Order status updated to '{new_status}'.",
            data=OrderSerializer(order).data
        )
