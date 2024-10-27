from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from jwt.utils import force_bytes
from rest_framework_simplejwt.tokens import RefreshToken

from .models import SignUpForm

class UserViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.change_password_url = reverse('change_password')
        self.activation_url = reverse('activate', kwargs={'uidb64': '', 'token': ''})

    def test_signup_creates_user_and_sends_activation_email(self):
        response = self.client.post(self.signup_url, {
            'username': 'testuser',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com'
        })

        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertFalse(user.is_active)

        self.assertRedirects(response, self.login_url)

    def test_logout_view(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('logout_view'))

        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertRedirects(response, self.login_url)

    def test_change_password(self):
        user = User.objects.create_user(username='testuser', password='testpassword123')
        self.client.login(username='testuser', password='testpassword123')

        response = self.client.post(self.change_password_url, {
            'old_password': 'testpassword123',
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123'
        })

        user.refresh_from_db()
        self.assertTrue(user.check_password('newpassword123'))
        self.assertRedirects(response, reverse('notes'))

    def test_activate_account(self):
        user = User.objects.create_user(username='testuser', password='testpassword123', is_active=False)
        user.save()

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        self.activation_url = reverse('activate', kwargs={'uidb64': uid, 'token': token})

        response = self.client.get(self.activation_url)

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertRedirects(response, reverse('home'))

    def test_invalid_activation_link(self):
        response = self.client.get(self.activation_url.replace('token', 'invalid_token'))
        self.assertContains(response, 'Activation link is invalid!')
        self.assertRedirects(response, self.signup_url)
