from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from product.models import Product, Category, ProductStatus
from cart.models import Cart, CartItem
from .models import Address, Order, OrderItem, OrderStatus, PaymentStatus

User = get_user_model()


class OrderAndCheckoutTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='orderuser@example.com',
            password='Password123!',
            first_name='Order',
            last_name='Tester'
        )
        self.category = Category.objects.create(name='Laptops')
        self.product = Product.objects.create(
            name='Gaming Laptop M1',
            price=Decimal('1200.00'),
            stock=5,
            category=self.category
        )
        self.address = Address.objects.create(
            user=self.user,
            full_name='Order Tester',
            street_address='123 Tech Street',
            city='Riyadh',
            state='Riyadh',
            postal_code='12345',
            country='Saudi Arabia',
            phone_number='+966500000000',
            is_default=True
        )

    def test_address_creation_api(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/addresses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['city'], 'Riyadh')

    def test_atomic_checkout_success(self):
        self.client.force_authenticate(user=self.user)
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        checkout_data = {
            "address_id": self.address.id,
            "payment_method": "CREDIT_CARD"
        }
        response = self.client.post('/api/v1/checkout/', checkout_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
        # Verify Order & OrderItem created
        order_number = response.data['data']['order_number']
        order = Order.objects.get(order_number=order_number)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.payment_status, PaymentStatus.PAID)
        self.assertEqual(order.status, OrderStatus.PROCESSING)

        # Verify Product stock decremented (5 - 2 = 3)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

        # Verify Cart cleared
        self.assertEqual(cart.items.count(), 0)

    def test_checkout_empty_cart_fails(self):
        self.client.force_authenticate(user=self.user)
        checkout_data = {
            "address_id": self.address.id,
            "payment_method": "CREDIT_CARD"
        }
        response = self.client.post('/api/v1/checkout/', checkout_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_cancellation_restores_stock(self):
        self.client.force_authenticate(user=self.user)
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=3)

        response = self.client.post('/api/v1/checkout/', {
            "address_id": self.address.id,
            "payment_method": "CREDIT_CARD"
        }, format='json')
        order_id = response.data['data']['id']

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

        # Cancel Order
        cancel_res = self.client.post(f'/api/v1/orders/{order_id}/cancel/')
        self.assertEqual(cancel_res.status_code, status.HTTP_200_OK)
        self.assertEqual(cancel_res.data['data']['status'], OrderStatus.CANCELLED)
        self.assertEqual(cancel_res.data['data']['payment_status'], PaymentStatus.REFUNDED)

        # Stock restored to 5
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)
