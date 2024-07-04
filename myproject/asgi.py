import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from myapp.consumers import TicketConsumer, LiveConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('ws/ticket/<int:ticket_id>/', TicketConsumer.as_asgi()),
            path('ws/chat/<str:room_name>/', LiveConsumer.as_asgi()),
        ])
    ),
})
