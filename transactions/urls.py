from django.urls import path
from .views import DepositMoneyView, TransactionStatementView

urlpatterns = [
    path('deposit/', DepositMoneyView.as_view(), name='deposit'),
    path('statements/', TransactionStatementView.as_view(), name='statements'),
]