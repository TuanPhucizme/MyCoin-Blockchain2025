import hashlib
import json
import time

from django.http import JsonResponse

from .POW import proof_of_work 

class Block:
    def __init__(self, index, transactions, previous_hash, timestamp=None, nonce=0):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.time()
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_data = json.dumps({
            'index': self.index,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
        }, sort_keys=True).encode()
        return hashlib.sha256(block_data).hexdigest()

    def mine_block(request):
        # Dữ liệu giả lập hoặc lấy từ transaction đang chờ
        index = request.data.get('index', 0)
        sender = request.data.get('sender', "Alice")
        receiver = request.data.get('receiver', "Bob")
        amount = request.data.get('amount', 50)
        message = request.data.get('message', "Thanks!")
        timestamp = request.data.get('timestamp', time.time())
        previous_hash = Blockchain.get_latest_block().hash
        difficulty = 4

        nonce, hash_result = proof_of_work(index, sender, receiver, amount, message, timestamp, previous_hash, difficulty)

        # Sau khi mine xong, bạn có thể tạo block mới và lưu lại:
        new_block = Block.objects.create(
            index=index,
            sender=sender,
            receiver=receiver,
            amount=amount,
            message=message,
            timestamp=timestamp,
            previous_hash=previous_hash,
            nonce=nonce,
            hash=hash_result
        )

        return JsonResponse({'message': 'Block mined!', 'nonce': nonce, 'hash': hash_result})


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4  # Số lượng số 0 cần thiết trong hash
        self.pending_transactions = []

    def create_genesis_block(self):
        return Block(0, [], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self):
        if not self.pending_transactions:
            return None  # hoặc raise exception

        new_block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions,
            timestamp=str(time.time()),
            previous_hash=self.get_latest_block().hash
        )

        new_block.hash = self.proof_of_work(new_block)
        self.chain.append(new_block)
        self.pending_transactions = []

        return new_block

