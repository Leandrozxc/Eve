from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser@example.com", email="testuser@example.com", password="password123")

    def test_login_page_renders(self):
        response = self.client.get(reverse('login:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login/login.html')

    def test_login_with_valid_credentials(self):
        response = self.client.post(reverse('login:login'), {
            'email': 'testuser@example.com',
            'password': 'password123',
        })
        self.assertRedirects(response, reverse('home:home'))

    def test_login_with_invalid_credentials(self):
        response = self.client.post(reverse('login:login'), {
            'email': 'testuser@example.com',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email address or password.')

    def test_logout_redirects_to_login(self):
        response = self.client.get(reverse('login:logout'))
        self.assertRedirects(response, reverse('login:login'))
