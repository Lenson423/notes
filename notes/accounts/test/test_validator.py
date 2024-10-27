from django.test import TestCase
from django.contrib.auth.models import User
from ..models import SignUpForm


class SignUpFormTestCase(TestCase):
    def setUp(self):
        self.valid_data = {
            'username': 'testuser',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com'
        }

        self.invalid_data = {
            'username': 'testuser',
            'password1': 'testpassword123',
            'password2': 'differentpassword',
            'first_name': '',
            'last_name': '',
            'email': 'invalid-email'
        }

    def test_form_is_valid_with_valid_data(self):
        form = SignUpForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), "The form should be valid with correct data.")

    def test_form_is_invalid_with_invalid_data(self):
        form = SignUpForm(data=self.invalid_data)
        self.assertFalse(form.is_valid(), "The form should be invalid with incorrect data.")
        self.assertIn('first_name', form.errors, "Form should have a first_name error.")
        self.assertIn('last_name', form.errors, "Form should have a last_name error.")
        self.assertIn('email', form.errors, "Form should have an email error.")

    def test_user_creation_with_valid_data(self):
        form = SignUpForm(data=self.valid_data)
        if form.is_valid():
            user = form.save()
            self.assertIsInstance(user, User, "A User instance should be created.")
            self.assertFalse(user.is_active, "User should be inactive until verified.")
            self.assertEqual(user.first_name, 'Test', "First name should match.")
            self.assertEqual(user.last_name, 'User', "Last name should match.")
            self.assertEqual(user.email, 'testuser@example.com', "Email should match.")
            self.assertEqual(user.username, 'testuser', "Username should match.")
