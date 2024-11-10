import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from chat import consumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat.settings')

ws_urlpatterns = [
    path("ws/<str:room_name>/", consumer.ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            ws_urlpatterns
        )
    )
})
