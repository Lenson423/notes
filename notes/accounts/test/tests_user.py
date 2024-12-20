from unittest import mock
from django.test import TestCase
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth.forms import PasswordChangeForm

from .. import User

class UserTests(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = DjangoUser.objects.create_user(username=self.username, password=self.password)
        self.user_class = User()

    @mock.patch('your_app.models.login')
    @mock.patch('your_app.models.authenticate')
    def test_create_user(self, mock_authenticate, mock_login):
        mock_authenticate.return_value = self.user

        request = mock.Mock()
        user = self.user_class.create_user(self.username, self.password, request)
        mock_authenticate.assert_called_once_with(username=self.username, password=self.password)
        mock_login.assert_called_once_with(request, self.user)
        self.assertEqual(user, self.user)

    @mock.patch('your_app.models.logout')
    def test_logout(self, mock_logout):
        self.client.login(username=self.username, password=self.password)

        # Вызываем логаут
        request = mock.Mock()
        self.user_class.user = self.username
        self.user_class.logout(request)
        mock_logout.assert_called_once_with(request)

    @mock.patch('your_app.models.update_session_auth_hash')
    def test_change_password(self, mock_update_session_auth_hash):
        self.client.login(username=self.username, password=self.password)

        new_password = 'new_password'
        form_data = {
            'old_password': self.password,
            'new_password1': new_password,
            'new_password2': new_password,
        }

        request = mock.Mock(method='POST', user=self.user)
        request.POST = form_data

        form = PasswordChangeForm(self.user, form_data)
        if form.is_valid():
            form.save()

        self.user_class.change_password(request)
        mock_update_session_auth_hash.assert_called_once_with(request, self.user)

    def test_logging_output(self):
        with self.assertLogs('your_app', level='INFO') as log:
            request = mock.Mock()
            self.user_class.create_user(self.username, self.password, request)
            self.assertIn('User Created ' + self.username, log.output[0])
