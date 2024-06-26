from django import forms
from .models import Transaction
        
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type']
        
    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()
        
    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()
        
class DepositForm(TransactionForm):
    def clean_amount(self):
        min_deposit_amount = 100
        amount = self.cleaned_data.get('amount')
        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f"You need to deposit at least $ {min_deposit_amount}"
            )
        return amount
    
class BorrowForm(forms.ModelForm):            
    class Meta:
        model = Transaction
        fields = ['transaction_type']
        
    def __init__(self, *args, **kwargs):        
        self.account = kwargs.pop('account')
        self.book = kwargs.pop('book')
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()
        # self.fields['amount'].initial = self.book.borrowing_price
        # self.fields['amount'].widget = forms.HiddenInput()
        
    def clean_amount(self):        
        account = self.account
        balance = account.balance
        amount = self.book.borrowing_price
        if amount > balance:
            raise forms.ValidationError(
                f"You have insufficient balance to borrow a book!"
            )
        return amount
    
    def save(self, commit=True):
        self.instance.book = self.book
        self.instance.account = self.account
        self.instance.amount = self.book.borrowing_price
        self.instance.balance_after_transaction = self.account.balance
        return super().save()
