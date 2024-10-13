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

from notekeeper.settings import EMAIL_HOST_USER

class View:
    def signup(request):
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = False  # Деактивируем аккаунт до подтверждения email
                user.save()

                # Отправляем email с подтверждением
                current_site = get_current_site(request)
                mail_subject = 'Activate your account'
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                message = render_to_string('activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': uid,
                    'token': token,
                })
                send_mail(mail_subject, message, EMAIL_HOST_USER, [user.email])
                messages.info(request, 'Please confirm your email to complete registration.')
                return redirect('login')
        else:
            form = SignUpForm()
        return render(request, 'signup.html', {'form': form})


    def logout_view(request):
        logout(request)
        return redirect('login')


    def change_password(request):
        if request.method == 'POST':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, 'Your password was successfully updated!')

                refresh = RefreshToken.for_user(user)
                request.session['refresh'] = str(refresh)
                request.session['access'] = str(refresh.access_token)
                return redirect('notes')
        else:
            form = PasswordChangeForm(request.user)

        return render(request, 'change_password.html', {
            'form': form
        })

    def activate(request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.is_email_verified = True  # Обновляем статус верификации
            user.save()
            login(request, user)
            messages.success(request, 'Your account has been activated!')
            return redirect('home')
        else:
            messages.warning(request, 'Activation link is invalid!')
            return redirect('signup')
