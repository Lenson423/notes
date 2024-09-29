import logging
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

class User:
    def createUser(self, username, password, request):
        try:
            self.user = authenticate(username=username, password=password)  # Adding into DB with users
            login(request, self.user)  # Adding into DB with sessions
            logging.info('User Created ' + username)
            return self.user
        except Exception as e:
            logging.error(e)

    def logout(self, request):
        try:
            logout(request)  # Delete from DB with sessions
            logging.info('User ' + self.user + ' Logged Out')
        except Exception as e:
            logging.error(e)

    def change_password(self, request):
        if request.method == 'POST':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Update users DB
                logging.info('Password Changed Successfully')
