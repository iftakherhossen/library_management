from django.shortcuts import render, redirect
from django.views.generic import FormView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login, logout 
from django.urls import reverse_lazy
from django.views import View
from .forms import UserRegistrationForm, UpdateUserProfileForm
from transactions.models import Transaction
from datetime import datetime
from django.db.models import Sum
from transactions.constants import BORROW, RETURN 

# Create your views here.
class UserRegistrationView(FormView):
    template_name = 'accounts/registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)
    
class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    def get_success_url(self):
        return reverse_lazy('home')
    
class UserLogOutView(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            logout(self.request)
        return reverse_lazy('home')

class UserAccountView(LoginRequiredMixin, ListView):
    template_name = 'accounts/profile.html'
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
        context = {}
        transactions = self.get_queryset()
        form = UpdateUserProfileForm(instance=self.request.user)
        borrow_count = transactions.filter(transaction_type=BORROW, returned=False).count()
        return_count = transactions.filter(transaction_type=BORROW, returned=True).count()
        context.update({
            'account': self.request.user.account,
            'transactions': transactions,
            'balance': self.balance,
            'borrow_count': borrow_count,
            'return_count': return_count,
            'form': form
        })
        
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

class UserAccountUpdateView(View):
    template_name = 'accounts/edit_profile.html'    

    def get(self, request):
        form = UpdateUserProfileForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UpdateUserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, self.template_name, {'form': form})
    
