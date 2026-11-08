from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class SettingsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser@example.com", password="password123")

    def test_unauthenticated_redirects_to_login(self):
        response = self.client.get(reverse('usersettings:settings'))
        self.assertRedirects(response, f"{reverse('login:login')}?next={reverse('usersettings:settings')}")

    def test_authenticated_settings_page_renders(self):
        self.client.login(username="testuser@example.com", password="password123")
        response = self.client.get(reverse('usersettings:settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usersettings/settings.html')
