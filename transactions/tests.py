from django.test import TestCase
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Transaction, Account

class TransactionTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.account = Account.objects.create(user=self.user, balance=500.00)

    def test_deposit_transaction(self):
        transaction = Transaction.objects.create(user=self.user, transaction_type='deposit', amount=100.00)
        self.assertEqual(self.user.account.get_balance(), 600.00)

    def test_withdrawal_transaction(self):
        transaction = Transaction.objects.create(user=self.user, transaction_type='withdrawal', amount=100.00)
        self.assertEqual(self.user.account.get_balance(), 400.00)

    def test_withdrawal_exceeds_balance(self):
        with self.assertRaises(ValueError):
            Transaction.objects.create(user=self.user, transaction_type='withdrawal', amount=600.00)

    def test_deposit_exceeds_limit(self):
        with self.assertRaises(ValueError):
            Transaction.objects.create(user=self.user, transaction_type='deposit', amount=600.00)
