"""
Utility functions and serializers for managing transactions and account balances.
Imports:
    - Decimal from `decimal`: For accurate representation of monetary values.
"""
from decimal import Decimal
from django.db.models import F
from django.core.cache import cache
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    """
    User Model containing email, first_name, last_name fields
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='transactions_user_groups',
        blank=True,
        help_text=('The groups this user belongs to. A user will get all permissions '
                   'granted to each of their groups.'),
        verbose_name=('groups'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='transactions_user_permissions',
        blank=True,
        help_text=('Specific permissions for this user.'),
        verbose_name=('user permissions'),
    )


class Account(models.Model):
    """
    Account Model for checking user details
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def get_balance(self):
        """
        Returns the account balance.
        """
        return self.balance

    def __str__(self):
        """
        Returns a string representation of the account.
        """
        # pylint: disable=no-member
        return f"Account of {self.user.username} with balance {self.balance}"

def clear_transaction_history_cache(user_id):
    """
    Clears the transaction history cache for a given user.
    """
    cache_key = f"transaction_history_{user_id}"
    cache.delete(cache_key)

class Transaction(models.Model):
    """
    Model representing a financial transaction.
    """
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the transaction.
        """
        return f"{self.transaction_type} of {self.amount}"

    def save(self, *args, **kwargs):
        """
        Validate and save the transaction.
        """
        account = self.user.account
        if self.transaction_type == 'withdrawal' and account.get_balance() < self.amount:
            raise ValueError('Insufficient funds.')

        if self.transaction_type == 'deposit' and account.get_balance() + self.amount > 500:
            raise ValueError('Account balance limit exceeded.')

        super().save(*args, **kwargs)

        balance_change = self.amount if self.transaction_type == 'deposit' else -self.amount
        account.balance = F('balance') + balance_change
        account.save()

        clear_transaction_history_cache(account.user.id)
