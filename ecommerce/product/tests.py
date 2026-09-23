from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from .models import Category, Product, ProductImage, Review, ProductStatus

User = get_user_model()


class ProductCatalogTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Users
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='AdminPassword123!',
            first_name='Admin',
            last_name='User'
        )
        self.seller = User.objects.create_user(
            email='seller@example.com',
            password='SellerPassword123!',
            first_name='Seller',
            last_name='One',
            role='SELLER'
        )
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='CustomerPassword123!',
            first_name='Customer',
            last_name='One',
            role='CUSTOMER'
        )

        # Categories
        self.parent_cat = Category.objects.create(name='Electronics', description='Tech items')
        self.child_cat = Category.objects.create(name='Smartphones', parent=self.parent_cat)

        # Product
        self.product = Product.objects.create(
            name='iPhone 15 Pro',
            description='Flagship smartphone',
            price=999.99,
            brand='Apple',
            category=self.child_cat,
            stock=10,
            user=self.seller
        )

    def test_category_hierarchy_and_slug(self):
        self.assertEqual(self.parent_cat.slug, 'electronics')
        self.assertEqual(self.child_cat.parent, self.parent_cat)

    def test_product_auto_slug_and_sku(self):
        self.assertEqual(self.product.slug, 'iphone-15-pro')
        self.assertTrue(self.product.sku.startswith('SKU-'))

    def test_review_recalculates_product_ratings(self):
        # Customer 1 reviews
        Review.objects.create(
            product=self.product,
            user=self.customer,
            rating=5,
            comment='Outstanding phone!'
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.num_reviews, 1)
        self.assertEqual(float(self.product.ratings_avg), 5.0)

        # Customer 2 reviews
        customer2 = User.objects.create_user(
            email='customer2@example.com',
            password='Password123!',
            first_name='Second',
            last_name='Customer'
        )
        Review.objects.create(
            product=self.product,
            user=customer2,
            rating=3,
            comment='Average battery life.'
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.num_reviews, 2)
        self.assertEqual(float(self.product.ratings_avg), 4.0)

    def test_product_list_api_filtering(self):
        response = self.client.get('/api/v1/products/?brand=Apple&min_price=900')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_customer_cannot_create_product(self):
        self.client.force_authenticate(user=self.customer)
        data = {
            "name": "Unauthorized Laptop",
            "price": 500.00,
            "brand": "Generic",
            "stock": 5
        }
        response = self.client.post('/api/v1/products/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_seller_can_create_product(self):
        self.client.force_authenticate(user=self.seller)
        data = {
            "name": "MacBook Pro M3",
            "price": 1999.99,
            "brand": "Apple",
            "stock": 5,
            "category": self.parent_cat.id
        }
        response = self.client.post('/api/v1/products/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], "MacBook Pro M3")
