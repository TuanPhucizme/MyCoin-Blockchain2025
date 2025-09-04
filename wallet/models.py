from django.db import models
from django.utils import timezone

# block
class Block(models.Model):
    index = models.IntegerField()
    previous_hash = models.CharField(max_length=64)
    hash = models.CharField(max_length=64)
    nonce = models.IntegerField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Block #{self.index} - {self.hash}"

# Create your models here.
class Wallet(models.Model):
    address = models.CharField(max_length=64, unique=True)
    public_key = models.TextField()
    private_key = models.TextField()
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address

# giao dich
class Transaction(models.Model):
    sender = models.CharField(max_length=100)
    receiver = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    message = models.TextField(blank=True)
    timestamp = models.DateTimeField()
    previous_hash = models.CharField(max_length=64, default='0'*64)
    nonce = models.IntegerField(default=0)
    hash = models.CharField(max_length=64, default='0'*64)
    block = models.ForeignKey(Block, on_delete=models.SET_NULL, null=True, blank=True)
