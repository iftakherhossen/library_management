from django.db import models
from accounts.models import UserAccount
from books.models import Book
from .constants import TRANSACTION_TYPE

# Create your models here.
class Transaction(models.Model):
    account = models.ForeignKey(UserAccount, related_name='transactions', on_delete=models.CASCADE)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after_transaction = models.DecimalField(max_digits=12, decimal_places=2)
    book = models.ForeignKey(Book, related_name='Borrow', on_delete=models.CASCADE, null=True, blank=True)
    returned = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']