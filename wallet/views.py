from django.shortcuts import render, redirect
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
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
    # Nếu là GET request, chỉ hiển thị trang tạo ví ban đầu
    if request.method == 'GET':
        return render(request, 'createwallet.html')

    # Nếu là POST request (được gọi từ AJAX)
    if request.method == 'POST':
        priv, pub, addr = generate_wallet()
        wallet = Wallet.objects.create(address=addr, public_key=pub, private_key=priv, balance=1000)
        
        # Lưu wallet vào session để người dùng được "đăng nhập" ngay lập tức
        request.session['wallet_id'] = wallet.id
        request.session['wallet_address'] = addr

        # Chuẩn bị dữ liệu để trả về cho JavaScript
        wallet_data = {
            'address': wallet.address,
            'public_key': wallet.public_key,
            'private_key': wallet.private_key, # Chỉ gửi private key MỘT LẦN này thôi
        }
        
        return JsonResponse({'success': True, 'wallet': wallet_data})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# ========== Gửi giao dịch ==========
def send_transaction_view(request):
    # Bước 1: Xác thực người dùng và lấy ví của họ
    # Logic này phải được thực hiện cho cả GET và POST request
    try:
        current_wallet = Wallet.objects.get(address=request.session.get('wallet_address'))
    except Wallet.DoesNotExist:
        messages.error(request, "Bạn cần tạo hoặc đăng nhập vào ví để thực hiện giao dịch.")
        return redirect('create_wallet')

    # Bước 2: Xử lý khi người dùng gửi form (POST request)
    if request.method == "POST":
        receiver_address = request.POST.get('receiver')
        message = request.POST.get('message', '')
        
        # --- Bắt đầu khối try-except để xử lý lỗi đầu vào ---
        try:
            amount = Decimal(request.POST.get('amount'))
            receiver_wallet = Wallet.objects.get(address=receiver_address)
            # sender_wallet chính là current_wallet đã lấy ở trên
            sender_wallet = current_wallet

        except Wallet.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Địa chỉ người nhận không tồn tại.'})
        except (ValueError, TypeError, Decimal.InvalidOperation):
            return JsonResponse({'success': False, 'error': 'Số tiền không hợp lệ.'})
        # --- Kết thúc khối try-except ---

        # --- Kiểm tra các quy tắc nghiệp vụ ---
        if sender_wallet.address == receiver_wallet.address:
            return JsonResponse({'success': False, 'error': 'Bạn không thể gửi tiền cho chính mình.'})

        if sender_wallet.balance < amount:
            error_message = f"Số dư không đủ. Bạn chỉ có {sender_wallet.balance} MYC."
            return JsonResponse({'success': False, 'error': error_message})
        
        if amount <= 0:
            return JsonResponse({'success': False, 'error': 'Số tiền phải lớn hơn 0.'})
        
        # 1. Cập nhật số dư
        sender_wallet.balance -= amount
        receiver_wallet.balance += amount
        sender_wallet.save()
        receiver_wallet.save()

        # 2. Tạo đối tượng giao dịch và thực hiện PoW
        # (Giữ nguyên toàn bộ logic mining của bạn)
        last_tx = Transaction.objects.order_by('-id').first()
        previous_hash = last_tx.hash if last_tx else '0'
        timestamp = timezone.now()
        index = last_tx.id + 1 if last_tx else 1
        nonce, tx_hash = proof_of_work(index, sender_wallet.address, receiver_wallet.address, amount, message, timestamp, previous_hash)
        tx = Transaction.objects.create(
            sender=sender_wallet.address,
            receiver=receiver_wallet.address,
            amount=amount,
            message=message,
            timestamp=timestamp,
            previous_hash=previous_hash,
            nonce=nonce,
            hash=tx_hash,
        )
        
        # 3. Gửi thông báo WebSocket đến người nhận
        channel_layer = get_channel_layer()
        detail_url = request.build_absolute_uri(reverse('transaction_detail', kwargs={'transaction_id': tx.id}))
        message_data = {
            'type': 'wallet_update',
            'balance': str(receiver_wallet.balance),
            'transaction': {
                'sender': tx.sender,
                'receiver': tx.receiver,
                'amount': str(tx.amount),
                'timestamp': tx.timestamp.isoformat(),
                'message': tx.message,
                'detail_url': detail_url,
            }
        }
        async_to_sync(channel_layer.group_send)(
            f"wallet_{receiver_address}",
            {'type': 'wallet.update', 'message': message_data}
        )

        # 4. Trả về kết quả thành công cho AJAX
        redirect_url = reverse('transaction_receipt', kwargs={'transaction_id': tx.id})
        return JsonResponse({'success': True, 'redirect_url': redirect_url})
        # --- Kết thúc xử lý POST ---

    # Bước 3: Nếu là GET request, chỉ render template
    # Context được tạo ở đây, bên ngoài khối 'if request.method == "POST"'
    context = {
        'wallet': current_wallet
    }
    return render(request, 'send_transaction.html', context)

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

def transaction_detail_view(request, transaction_id):
    """
    Hiển thị thông tin chi tiết của một giao dịch duy nhất.
    """
    # get_object_or_404 là một cách gọn gàng để lấy object hoặc trả về lỗi 404 nếu không tìm thấy
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    context = {
        'transaction': transaction
    }
    return render(request, 'transaction_detail.html', context)

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
