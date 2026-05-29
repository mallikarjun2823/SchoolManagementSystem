from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AuthEndpointTests(APITestCase):
    def test_register_with_valid_data_returns_tokens(self):
        url = reverse('register')
        data = {
            'username': 'student1',
            'email': 'student1@example.com',
            'password': 'StrongPass123!',
            'role': 'student',
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['username'], 'student1')

    def test_register_with_invalid_role_returns_400(self):
        url = reverse('register')
        data = {
            'username': 'badrole',
            'email': 'badrole@example.com',
            'password': 'StrongPass123!',
            'role': 'unknown',
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('role', response.data)

    def test_register_with_duplicate_username_returns_400(self):
        url = reverse('register')
        self.client.post(url, {
            'username': 'dupuser',
            'email': 'dup@example.com',
            'password': 'StrongPass123!',
            'role': 'student',
        }, format='json')

        response = self.client.post(url, {
            'username': 'dupuser',
            'email': 'dup2@example.com',
            'password': 'StrongPass123!',
            'role': 'student',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_login_with_valid_credentials_returns_tokens(self):
        self.client.post(reverse('register'), {
            'username': 'loginuser',
            'email': 'login@example.com',
            'password': 'StrongPass123!',
            'role': 'student',
        }, format='json')

        response = self.client.post(reverse('login'), {
            'username': 'loginuser',
            'password': 'StrongPass123!',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_wrong_password_returns_400(self):
        self.client.post(reverse('register'), {
            'username': 'wrongpass',
            'email': 'wrongpass@example.com',
            'password': 'StrongPass123!',
            'role': 'student',
        }, format='json')

        response = self.client.post(reverse('login'), {
            'username': 'wrongpass',
            'password': 'WrongPass123!',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_login_with_missing_fields_returns_400(self):
        response = self.client.post(reverse('login'), {
            'username': 'missing',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
