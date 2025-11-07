# transactions/tasks.py
from celery import shared_task
from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from .models import Transaction, Account
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task(bind=True)
def process_transaction(self, user_id, amount, transaction_type, transaction_data):
    """Simulates processing a transaction for a user."""
    try:
        user = User.objects.get(id=user_id)
        with transaction.atomic():
            account = Account.objects.select_for_update().get(user=user)

            if transaction_type == 'withdrawal':
                if account.balance < amount:
                    raise ValidationError("Insufficient balance for withdrawal.")
                account.balance = F('balance') - amount
            else:
                account.balance = F('balance') + amount
            account.save()

            Transaction.objects.create(user=user, amount=amount, transaction_type=transaction_type, **transaction_data)
        return "Transaction successful"
    except Exception as e:
        raise self.retry(exc=e, countdown=10, max_retries=3)
