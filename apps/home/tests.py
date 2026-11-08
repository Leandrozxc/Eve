from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser@example.com", password="password123")

    def test_unauthenticated_redirects_to_login(self):
        response = self.client.get(reverse('home:home'))
        self.assertRedirects(response, f"{reverse('login:login')}?next={reverse('home:home')}")

    def test_home_page_renders_for_authenticated_user(self):
        self.client.login(username="testuser@example.com", password="password123")
        response = self.client.get(reverse('home:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/home.html')
        self.assertContains(response, 'Welcome')
        self.assertContains(response, 'Shift Scheduling')
