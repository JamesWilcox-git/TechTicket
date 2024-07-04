from channels.generic.websocket import AsyncWebsocketConsumer
import json

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
