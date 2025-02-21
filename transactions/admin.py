from django.contrib import admin
from .models import Transaction, Account, User

# Register your models here.
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Transaction Model to display,search users and transactions
    """
    list_display = ('user', 'transaction_type', 'amount', 'timestamp')
    search_fields = ('user__username', 'transaction_type')
    list_filter = ('transaction_type', 'timestamp')

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """
    Account Model to list user and balance fields
    """
    list_display = ('user', 'balance')
    search_fields = ('user__username',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Custom User model to list user fields
    """
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email')
