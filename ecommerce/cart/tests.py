from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from product.models import Product, Category
from .models import Cart, CartItem, Wishlist, WishlistItem

User = get_user_model()


class CartAndWishlistTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='cartuser@example.com',
            password='Password123!',
            first_name='Cart',
            last_name='User'
        )
        self.category = Category.objects.create(name='Gadgets')
        self.product = Product.objects.create(
            name='Wireless Mouse',
            price=Decimal('50.00'),
            stock=10,
            category=self.category
        )

    def test_add_to_cart_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/v1/cart/', {
            "product_id": self.product.id,
            "quantity": 2
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['total_items'], 2)
        self.assertEqual(Decimal(str(response.data['data']['subtotal'])), Decimal('100.00'))
        self.assertEqual(Decimal(str(response.data['data']['grand_total'])), Decimal('105.00'))

    def test_add_to_cart_insufficient_stock(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/v1/cart/', {
            "product_id": self.product.id,
            "quantity": 15
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_update_cart_item_quantity(self):
        self.client.force_authenticate(user=self.user)
        cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(cart=cart, product=self.product, quantity=1)

        response = self.client.patch(f'/api/v1/cart/items/{item.id}/', {
            "quantity": 5
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['total_items'], 5)

    def test_wishlist_toggle(self):
        self.client.force_authenticate(user=self.user)

        # Toggle Add
        response1 = self.client.post('/api/v1/wishlist/toggle/', {
            "product_id": self.product.id
        }, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertTrue(response1.data['data']['added'])

        # Toggle Remove
        response2 = self.client.post('/api/v1/wishlist/toggle/', {
            "product_id": self.product.id
        }, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertFalse(response2.data['data']['added'])
