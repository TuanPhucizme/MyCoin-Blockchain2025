# blockchain/urls.py

from django.contrib import admin
from django.urls import path, include # Đảm bảo có 'include'

urlpatterns = [
    # URL cho trang admin
    path('admin/', admin.site.urls),
    
    # Tất cả các URL còn lại sẽ được xử lý bởi file urls.py của app 'wallet'
    path('', include('wallet.urls')),
]