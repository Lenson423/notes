import logging
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Model
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger(__name__)


class User(Model):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create_user(self, username, password, request):
        try:
            self.user = authenticate(username=username, password=password)  # Adding into DB with users
            login(request, self.user)  # Adding into DB with sessions
            logger.info('User Created ' + username)
            return self.user
        except Exception as e:
            logging.error(e)

    def logout(self, request):
        try:
            logout(request)  # Delete from DB with sessions
            logger.info('User %s logged out successfully', request.user)
        except Exception as e:
            logger.error("Error during logout for user '%s': %s", request.user, str(e))

    def change_password(self, request):
        if request.method == 'POST':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Update users DB
                logging.info('Password Changed Successfully')
                logger.info('Password changed successfully for user: %s', request.user.username)
            else:
                logger.warning('Password change form is invalid for user: %s', request.user.username)
        else:
            logger.warning('Invalid request method for password change: %s', request.method)
