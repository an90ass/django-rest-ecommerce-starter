from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class CustomUserModelTest(TestCase):
    def test_create_user_success(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPassword123!',
            first_name='John',
            last_name='Doe'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.full_name, 'John Doe')
        self.assertEqual(user.role, 'CUSTOMER')
        self.assertTrue(user.check_password('TestPassword123!'))

    def test_create_superuser_success(self):
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='AdminPassword123!',
            first_name='Admin',
            last_name='User'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.role, 'ADMIN')


class AccountAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/v1/auth/register/'
        self.login_url = '/api/v1/auth/login/'
        self.me_url = '/api/v1/auth/me/'

    def test_register_user_api(self):
        data = {
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!",
            "first_name": "Alice",
            "last_name": "Smith",
            "role": "CUSTOMER"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['email'], "newuser@example.com")

    def test_login_user_api(self):
        user = User.objects.create_user(
            email='login@example.com',
            password='LoginPassword123!',
            first_name='Bob',
            last_name='Marley'
        )
        response = self.client.post(self.login_url, {
            "email": "login@example.com",
            "password": "LoginPassword123!"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])

    def test_get_user_profile_api(self):
        user = User.objects.create_user(
            email='profile@example.com',
            password='ProfilePassword123!',
            first_name='Charlie',
            last_name='Brown'
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['email'], 'profile@example.com')
