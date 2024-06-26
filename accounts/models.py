from django.db import models
from django.contrib.auth.models import User
from .constants import GENDER, ACCOUNT_TYPE

# Create your models here.
class UserAccount(models.Model):
    user = models.OneToOneField(User, related_name='account', on_delete=models.CASCADE)    
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE)
    account_no = models.IntegerField(unique=True)
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER)
    initial_deposit_date = models.DateField(auto_now=True)
    balance = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    
    def __str__(self):
        return str(self.account_no)