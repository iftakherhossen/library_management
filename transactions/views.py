from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Transaction
from .forms import DepositForm, BorrowForm
from books.models import Book
from datetime import datetime
from django.db.models import Sum
from django.views import View
from .constants import DEPOSIT, BORROW, RETURN

# Create your views here.
def SendTransactionEmail(user, amount, key):
    mail_subject = key + ' Confirmation'
    template = 'transactions/email_template.html'
        
    message = render_to_string(template, {
        'user': user,
        'amount': amount,
        'balance': user.account.balance,
        'key': key
    })
    send_email = EmailMultiAlternatives(mail_subject, '', to=[user.email])
    send_email.attach_alternative(message, 'text/html')
    send_email.send()

class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    key = ''
    success_url = reverse_lazy('profile')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            'key': self.key
        })
        return context
    
class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit Money'
    key = 'Deposit'
    
    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial
    
    def form_valid(self, form):  
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance += amount
        account.save(
            update_fields = ['balance']
        )
        messages.success(self.request, f"$ {'{:,.2f}'.format(float(amount))} Deposited Successfully!")
        SendTransactionEmail(self.request.user, amount, 'Deposit')
        return super().form_valid(form)
    
class BorrowBookView(TransactionCreateMixin):
    template_name = 'transactions/borrow_book.html'
    form_class = BorrowForm
    title = 'Borrow Book'
    key = 'Borrow'
    success_url = reverse_lazy('profile')
    
    def get_initial(self):
        initial = {'transaction_type': BORROW}
        return initial
    
    def get_book(self):
        book_slug = self.kwargs['book_slug']
        return get_object_or_404(Book, slug=book_slug)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account,
            'book': self.get_book()
        })
        return kwargs
    
    def form_valid(self, form):       
        book = self.get_book()
        account = self.request.user.account
        amount = book.borrowing_price
        account.balance -= amount
        account.save(
            update_fields = ['balance']
        )
        messages.success(self.request, f"The '{book.title}' book has been borrowed successfully!")
        SendTransactionEmail(self.request.user, amount, 'Borrow')
        return super().form_valid(form)
    
class ReturnBookView(LoginRequiredMixin, View):
    def post(self, request, book_slug, transaction_id):
        book = get_object_or_404(Book, slug=book_slug)
        transaction = Transaction.objects.filter(
            id=transaction_id,
            book=book,
            account=request.user.account,
            transaction_type=BORROW,
            returned=False
        ).first()

        if transaction:
            account = request.user.account
            account.balance += book.borrowing_price             
            account.save(update_fields=['balance'])
            
            transaction.returned = True           
            transaction.save(update_fields=['returned'])

            Transaction.objects.create(
                account=account,
                amount=book.borrowing_price,
                transaction_type=RETURN,
                balance_after_transaction=account.balance,
                book=book,
                returned=True,
            )

            messages.success(request, f"The book '{book.title}' has been successfully returned!")
            SendTransactionEmail(request.user, book.borrowing_price, 'Return')

        return redirect('/accounts/profile/')    
    
class TransactionStatementView(LoginRequiredMixin, ListView):
    template_name = 'transactions/statements.html'
    model = Transaction
    balance = 0
    
    def get_queryset(self):
        queryset= super().get_queryset().filter(
            account = self.request.user.account
        )
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            queryset = queryset.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)
            self.balance = Transaction.objects.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance
            
        queryset = queryset.order_by('-timestamp')
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account
        })
        return context
