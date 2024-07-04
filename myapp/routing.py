from django.urls import re_path
from .consumers import TicketConsumer, LiveConsumer

websocket_urlpatterns = [
    re_path(r'ws/ticket/(?P<ticket_id>\d+)/$', TicketConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_name>\w+)/$', LiveConsumer.as_asgi()),
]
