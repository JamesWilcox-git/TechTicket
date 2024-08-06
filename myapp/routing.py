from django.urls import path
from .consumers import TicketConsumer, LiveConsumer

websocket_urlpatterns = [
    path(r'ws/ticket/(?P<ticket_id>\d+)/$', TicketConsumer.as_asgi()),
    path(r'ws/chat/(?P<room_name>\w+)/$', LiveConsumer.as_asgi()),
]
