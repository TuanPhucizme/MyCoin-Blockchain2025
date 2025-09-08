# wallet/urls.py

from django.urls import path
from . import views # Import views từ chính app này

urlpatterns = [
    # Khi người dùng truy cập vào trang gốc, nó sẽ gọi view 'home'
    path('', views.home, name='home'),
    
    # Các URL khác của ứng dụng wallet
    path('create_wallet/', views.create_wallet_view, name='create_wallet'),
    path('send_transaction/', views.send_transaction_view, name='send_transaction'),
    path('transaction_receipt/<int:transaction_id>/', views.transaction_receipt, name='transaction_receipt'),
    path('transaction/<int:transaction_id>/', views.transaction_detail_view, name='transaction_detail'),
]