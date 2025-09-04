from django.shortcuts import render, redirect
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from .models import Wallet, Transaction, Block
from .blockchain.POW import proof_of_work
from .blockchain.BLOCKCHAIN import Blockchain

from decimal import Decimal
import ecdsa
import secrets
import hashlib

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# ========== Trang chủ ==========
def home(request):
    wallet = None
    transactions = []

    wallet_id = request.session.get('wallet_id')
    if wallet_id:
        try:
            wallet = Wallet.objects.get(id=wallet_id)
            transactions = Transaction.objects.filter(
                Q(sender=wallet.address) | Q(receiver=wallet.address)
            ).order_by('-timestamp')
        except Wallet.DoesNotExist:
            pass

    return render(request, 'homepage.html', {
        'wallet': wallet,
        'transactions': transactions
    })


# ========== Tạo ví ==========
def generate_wallet():
    private_key = secrets.token_hex(32)
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    public_key = vk.to_string().hex()
    address = hashlib.sha256(bytes.fromhex(public_key)).hexdigest()[:40]
    return private_key, public_key, address


def create_wallet_view(request):
    if request.method == 'POST':
        priv, pub, addr = generate_wallet()
        wallet = Wallet.objects.create(address=addr, public_key=pub, private_key=priv, balance=1000)
        request.session['wallet_id'] = wallet.id
        request.session['wallet_address'] = addr
        return render(request, 'createdwallet.html', {'wallet': wallet})
    
    return render(request, 'createwallet.html')


# ========== Gửi giao dịch ==========
def send_transaction_view(request):
    if request.method == "POST":
        sender_address = request.session.get('wallet_address')
        receiver_address = request.POST['receiver']
        amount = Decimal(request.POST['amount'])
        message = request.POST.get('message', '')

        try:
            sender_wallet = Wallet.objects.get(address=sender_address)
            receiver_wallet = Wallet.objects.get(address=receiver_address)
        except Wallet.DoesNotExist:
            messages.error(request, "Không tìm thấy ví người gửi hoặc người nhận.")
            return redirect('send_transaction')

        if sender_wallet.balance < amount:
            messages.error(request, "Số dư không đủ.")
            return redirect('send_transaction')

        # Trừ tiền người gửi, cộng tiền người nhận
        sender_wallet.balance -= amount
        receiver_wallet.balance += amount
        sender_wallet.save()
        receiver_wallet.save()

        # Tạo giao dịch mới
        last_tx = Transaction.objects.order_by('-id').first()
        previous_hash = last_tx.hash if last_tx else '0'
        timestamp = timezone.now()
        index = last_tx.id + 1 if last_tx else 1

        nonce, tx_hash = proof_of_work(index, sender_address, receiver_address, amount, message, timestamp, previous_hash)

        tx = Transaction.objects.create(
            sender=sender_address,
            receiver=receiver_address,
            amount=amount,
            message=message,
            timestamp=timestamp,
            previous_hash=previous_hash,
            nonce=nonce,
            hash=tx_hash,
        )

        # Gửi sự kiện tới WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'wallet_{receiver_address}',
            {
                'type': 'send_transaction',
                'data': {
                    'sender': sender_address,
                    'amount': amount,
                    'message': message,
                }
            }
        )

        messages.success(request, "Giao dịch thành công và đã được xác minh bằng Proof of Work.")
        return redirect('transaction_receipt', transaction_id=tx.id)

    return render(request, 'send_transaction.html')


# ========== Biên lai giao dịch ==========
def transaction_receipt(request, transaction_id):
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        sender_wallet = Wallet.objects.get(address=transaction.sender)
        receiver_wallet = Wallet.objects.get(address=transaction.receiver)
    except (Transaction.DoesNotExist, Wallet.DoesNotExist):
        messages.error(request, "Không tìm thấy thông tin giao dịch.")
        return redirect('home')

    return render(request, 'transaction_receipt.html', {
        'transaction': transaction,
        'sender_wallet': sender_wallet,
        'receiver_wallet': receiver_wallet,
    })


# ========== Mine Block (Proof of Work) ==========
def mine_block_view(request):
    blockchain = Blockchain()
    mined_block = blockchain.mine_pending_transactions()

    if mined_block is None:
        messages.error(request, "Không có giao dịch nào để khai thác.")
        return redirect('home')

    block_obj = Block.objects.create(
        index=mined_block.index,
        timestamp=mined_block.timestamp,
        previous_hash=mined_block.previous_hash,
        hash=mined_block.hash,
        nonce=mined_block.nonce,
    )

    for tx in mined_block.transactions:
        try:
            tx_obj = Transaction.objects.get(hash=tx.hash)
            tx_obj.block = block_obj
            tx_obj.save()
        except Transaction.DoesNotExist:
            continue

    messages.success(request, f"Đã khai thác thành công block #{mined_block.index}.")
    return redirect('block_list')


# ========== Danh sách block ==========
def block_list_view(request):
    blocks = Block.objects.all().order_by("-index")
    return render(request, "block_list.html", {"blocks": blocks})
