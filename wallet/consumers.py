import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TransactionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Lấy txid (hoặc wallet address) từ URL
        self.txid = self.scope['url_route']['kwargs']['txid']
        self.room_group_name = f"transactions_{self.txid}"

        # Tham gia vào group tương ứng với txid
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        await self.send(text_data=json.dumps({
            "message": f"🔗 Connected to transaction {self.txid}"
        }))

    async def disconnect(self, close_code):
        # Rời khỏi group khi socket disconnect
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Nhận message từ client → echo lại (test)."""
        await self.send(text_data=json.dumps({
            "echo": text_data
        }))

    async def transaction_message(self, event):
        """Hàm này được gọi khi có message từ group."""
        await self.send(text_data=json.dumps(event["content"]))
