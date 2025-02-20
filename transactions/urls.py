# transactions/urls.py

from django.urls import path
from .views import UserRegisterView, UserLoginView, AccountView, TransactionView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('account/', AccountView.as_view(), name='account'),
    path('transaction/', TransactionView.as_view(), name='transaction'),
]
