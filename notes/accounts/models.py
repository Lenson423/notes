from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger(__name__)


# Create your models here.
class SignUpForm(UserCreationForm):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    first_name = forms.CharField(max_length=32)
    last_name = forms.CharField(max_length=32)
    email = forms.EmailField(max_length=64)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email',)

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        logger.debug("Initializing SignUpForm with args: %s, kwargs: %s", args, kwargs)

        self.fields['password1'].help_text = "Your password must contain at least 8 characters"
        self.fields['password2'].help_text = None
        logger.info("Password help text updated.")

    def save(self, commit=True):
        logger.info("Starting the save process for a new user.")
        try:
            user = super(SignUpForm, self).save(commit=False)
            user.first_name = self.cleaned_data["first_name"]
            user.last_name = self.cleaned_data["last_name"]
            user.email = self.cleaned_data["email"]
            logger.debug("User data - First Name: %s, Last Name: %s, Email: %s", user.first_name, user.last_name, user.email)
            if commit:
                user.is_active = False
                user.save()
                logger.info("New user created with username: %s", user.username)
            return user
        except Exception as e:
            logger.error("Error saving user: %s", str(e))
            raise
