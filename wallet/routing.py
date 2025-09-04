from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/transactions/(?P<wallet_address>\w+)/$', consumers.TransactionConsumer.as_asgi()),
]
