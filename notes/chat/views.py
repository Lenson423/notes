from django.shortcuts import render
from .models import Message


def index(request):
    return render(request, 'core/base.html')


def room(request, room_name):
    username = request.GET.get('username', 'Guest')
    messages = Message.objects.filter(room=room_name)[0:25]
    return render(request, 'core/room.html', {'room_name': room_name, 'username': username, 'messages': messages})
