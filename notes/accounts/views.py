from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken

from .models import SignUpForm
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from notekeeper.settings import EMAIL_HOST_USER


class View:
    def signup(self):
        if self.method == 'POST':
            form = SignUpForm(self.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = False  # Деактивируем аккаунт до подтверждения email
                user.save()

                # Отправляем email с подтверждением
                current_site = get_current_site(self)
                mail_subject = _('Activate your account')
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                message = render_to_string('activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': uid,
                    'token': token,
                })
                send_mail(mail_subject, message, EMAIL_HOST_USER, [user.email])
                messages.info(self, _('Please confirm your email to complete registration.'))
                return redirect('login')
        else:
            form = SignUpForm()
        return render(self, 'signup.html', {'form': form})

    def logout_view(self):
        logout(self)
        return redirect('login')

    def change_password(self):
        if self.method == 'POST':
            form = PasswordChangeForm(self.user, self.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(self, user)  # Important!
                messages.success(self, _('Your password was successfully updated!'))

                refresh = RefreshToken.for_user(user)
                self.session['refresh'] = str(refresh)
                self.session['access'] = str(refresh.access_token)
                return redirect('notes')
        else:
            form = PasswordChangeForm(self.user)

        return render(self, 'change_password.html', {
            'form': form
        })

    def activate(self, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.is_email_verified = True  # Обновляем статус верификации
            user.save()
            login(self, user)
            messages.success(self, _('Your account has been activated!'))
            return redirect('home')
        else:
            messages.warning(self, _('Activation link is invalid!'))
            return redirect('signup')
