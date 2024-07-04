from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json
from asgiref.sync import async_to_sync

class TicketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.ticket_id = self.scope['url_route']['kwargs']['ticket_id']
        await self.channel_layer.group_add(
            f'ticket_{self.ticket_id}',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f'ticket_{self.ticket_id}',
            self.channel_name
        )

    async def receive(self, text_data):
        message = json.loads(text_data)
        # Broadcast message to all clients in the group
        await self.channel_layer.group_send(
            f'ticket_{self.ticket_id}',
            {
                'type': 'chat.message',
                'sender_id': self.scope['user'].id,
                'message': message['message']
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'sender_id': event['sender_id'],
            'message': event['message']
        }))

class LiveConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))