from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/transactions/<str:wallet_address>/', consumers.TransactionConsumer.as_asgi()),
]
