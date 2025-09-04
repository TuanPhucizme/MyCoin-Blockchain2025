import hashlib
import json
import time

def calculate_hash(index, sender, receiver, amount, message, timestamp, previous_hash, nonce):
    block_data = {
        'index': index,
        'sender': sender,
        'receiver': receiver,
        'amount': str(amount),
        'message': message,
        'timestamp': timestamp.isoformat(),
        'previous_hash': previous_hash,
        'nonce': nonce
    }
    encoded = json.dumps(block_data, sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()

def proof_of_work(index, sender, receiver, amount, message, timestamp, previous_hash, difficulty=4):
    nonce = 0
    start_time = time.time()
    while True:
        hash_result = calculate_hash(index, sender, receiver, amount, message, timestamp, previous_hash, nonce)
        # In quá trình thử nonce
        if nonce % 10000 == 0:  # in mỗi 10000 bước để tránh spam
            print(f" Trying nonce {nonce} → hash: {hash_result}")
        if hash_result.startswith('0' * difficulty):
            elapsed = time.time() - start_time
            print(f" Block mined!")
            print(f"   Nonce: {nonce}")
            print(f"   Hash: {hash_result}")
            print(f"   Time: {elapsed:.2f} seconds")
            return nonce, hash_result

        nonce += 1

def compute_hash(self):
    block_string = json.dumps(self.__dict__, sort_keys=True)
    return hashlib.sha256(block_string.encode()).hexdigest()
