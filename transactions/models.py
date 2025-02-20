from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='transactions_user_set', 
        blank=True,
        help_text=('The groups this user belongs to. A user will get all permissions '
                   'granted to each of their groups.'),
        verbose_name=('groups'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='transactions_user_set',
        blank=True,
        help_text=('Specific permissions for this user.'),
        verbose_name=('user permissions'),
    )
    
class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def get_balance(self):
        return self.balance

    def __str__(self):
        return f"Account of {self.user.username} with balance {self.balance}"
    
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.amount}"

    def save(self, *args, **kwargs):
        if self.transaction_type == 'withdrawal':
            if self.user.account.get_balance() - self.amount < 0:
                raise ValueError('Insufficient funds.')
        elif self.transaction_type == 'deposit':
            if self.user.account.get_balance() + self.amount > 500:
                raise ValueError('Account balance limit exceeded.')
        super().save(*args, **kwargs)
        self.user.account.balance = self.user.account.get_balance() + self.amount if self.transaction_type == 'deposit' else self.user.account.get_balance() - self.amount
        self.user.account.save()