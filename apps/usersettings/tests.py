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

    def test_user_creation_signal_creates_usersettings(self):
        self.assertTrue(hasattr(self.user, 'usersettings'))
        self.assertFalse(self.user.usersettings.dark_mode)

    def test_toggle_theme_requires_login(self):
        response = self.client.post(reverse('usersettings:toggle_theme'))
        self.assertEqual(response.status_code, 302)

    def test_toggle_theme_requires_post(self):
        self.client.login(username="testuser@example.com", password="password123")
        response = self.client.get(reverse('usersettings:toggle_theme'))
        self.assertEqual(response.status_code, 405)

    def test_toggle_theme_flips_mode(self):
        self.client.login(username="testuser@example.com", password="password123")
        self.assertFalse(self.user.usersettings.dark_mode)

        # Toggle to dark
        response = self.client.post(reverse('usersettings:toggle_theme'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['dark_mode'])
        self.assertEqual(data['theme'], 'dark')
        self.user.usersettings.refresh_from_db()
        self.assertTrue(self.user.usersettings.dark_mode)

        # Toggle back to light
        response = self.client.post(reverse('usersettings:toggle_theme'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['dark_mode'])
        self.assertEqual(data['theme'], 'light')
        self.user.usersettings.refresh_from_db()
        self.assertFalse(self.user.usersettings.dark_mode)

    def test_toggle_theme_explicit_json_body(self):
        self.client.login(username="testuser@example.com", password="password123")
        
        # Explicit dark
        response = self.client.post(
            reverse('usersettings:toggle_theme'),
            data={'theme': 'dark'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['dark_mode'])

        # Explicit light
        response = self.client.post(
            reverse('usersettings:toggle_theme'),
            data={'theme': 'light'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['dark_mode'])
