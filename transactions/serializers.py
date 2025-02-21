from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Account, Transaction

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'password': {'write_only': True, 'required': True}
        }

    def validate(self, attrs):
        if User.objects.filter(username=attrs.get('username')).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        if User.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        Account.objects.create(user=user)
        return user

class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer for the Account model, responsible for serializing 
    the account data including the associated user and balance.
    """
    class Meta:
        model = Account
        fields = ['id', 'user', 'balance']

class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Transaction model, responsible for serializing 
    transaction data, including transaction type, amount, and timestamp.
    It also validates that the transaction amount is greater than zero.
    """
    class Meta:
        """
        Meta class for defining the model and fields that are serialized by the AccountSerializer.
        """
        model = Transaction
        fields = ['id', 'transaction_type', 'amount', 'timestamp']

    def validate_amount(self, value):
        """
        Validates the amount for the transaction. Ensures that the amount
        is greater than zero. Raises a ValidationError if the condition is not met.
        """
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
