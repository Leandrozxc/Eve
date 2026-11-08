from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_page_renders(self):
        response = self.client.get(reverse('register:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register/register.html')

    def test_register_creates_user_and_redirects(self):
        data = {
            'full_name': 'Test User',
            'email': 'testuser@example.com',
            'company': 'Eve Org',
            'password': 'password123',
            'confirm_password': 'password123',
        }
        response = self.client.post(reverse('register:register'), data)
        self.assertRedirects(response, reverse('login:login'))
        self.assertTrue(User.objects.filter(email='testuser@example.com').exists())
