import json
from channels.generic.websocket import AsyncWebsocketConsumer

# Tên class nên là WalletConsumer vì nó xử lý các cập nhật liên quan đến Wallet
class TransactionConsumer(AsyncWebsocketConsumer):
    
    # 1. HÀM CONNECT: Được gọi khi JavaScript kết nối tới
    async def connect(self):
        """
        Được gọi khi một client (trình duyệt) cố gắng kết nối WebSocket.
        """
        # Lấy địa chỉ ví từ URL mà JavaScript đã gọi
        # Ví dụ: /ws/transactions/059d302edf1440b554aee69467c61abdccfcb84c/
        self.wallet_address = self.scope['url_route']['kwargs']['wallet_address']
        
        # Tạo một tên group duy nhất cho mỗi ví để lắng nghe tin tức.
        # Chỉ những tin nhắn được gửi đến group này mới được xử lý.
        self.room_group_name = f'wallet_{self.wallet_address}'

        # Tham gia vào group.
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Chấp nhận kết nối WebSocket. Nếu không gọi hàm này, kết nối sẽ bị từ chối.
        await self.accept()
        print(f"✅ WebSocket connected for wallet: {self.wallet_address}") # Thêm log để debug

    # 2. HÀM DISCONNECT: Được gọi khi client đóng kết nối
    async def disconnect(self, close_code):
        """
        Được gọi khi kết nối WebSocket bị đóng.
        Dọn dẹp bằng cách rời khỏi group.
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"❌ WebSocket disconnected for wallet: {self.wallet_address}") # Thêm log để debug

    # 3. HÀM XỬ LÝ SỰ KIỆN TÙY CHỈNH: Được gọi từ backend (views.py)
    async def wallet_update(self, event):
        """
        Hàm này được gọi khi có một tin nhắn được gửi đến group từ backend
        với `type` là 'wallet.update'.
        Nó sẽ lấy nội dung tin nhắn và gửi xuống cho client.
        """
        # Dữ liệu được truyền từ views.py nằm trong event['message']
        message_to_send = event['message']

        # Gửi dữ liệu xuống cho client (trình duyệt)
        await self.send(text_data=json.dumps(message_to_send))
        print(f"Sent update to wallet: {self.wallet_address}") # Thêm log để debug