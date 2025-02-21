"""
This module contains URL patterns for user registration, login,
account management, transaction management, and transaction history views.
"""
from django.urls import path
from .views import (
    UserRegisterView,
    UserLoginView,
    AccountView,
    TransactionView,
    TransactionHistoryView
)

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('account/', AccountView.as_view(), name='account'),
    path('transaction/', TransactionView.as_view(), name='transaction'),
    path('transactions/', TransactionHistoryView.as_view(), name='transaction_history'),
]
