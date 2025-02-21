
"""
Serializers for the transaction simulation application.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Account, Transaction

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model. This serializer handles the creation and validation 
    of user data, including necessary fields and constraints.
    """

    class Meta:
        """
        Meta class to define the model and fields to be serialized.
        """
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'password': {'write_only': True, 'required': True}
        }

    def validate_password(self, value):
        """
        Validate the provided password using Django's built-in validators.

        Args:
            value (str): The password to validate.

        Returns:
            str: The validated password.

        Raises:
            serializers.ValidationError: If the password does not meet the required criteria.
        """
        validate_password(value)
        return value

    def validate(self, attrs):
        """
        Validate the provided data to ensure that the username and email are unique.

        Args:
            attrs (dict): The data to validate.

        Returns:
            dict: The validated data.

        Raises:
            serializers.ValidationError: If the username or email already exists.
        """
        if User.objects.filter(username=attrs.get('username')).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        if User.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return attrs

    def create(self, validated_data):
        """
        Create a new user instance with the provided validated data.

        Args:
            validated_data (dict): The data to create a new user.

        Returns:
            User: The created user instance.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        Account.objects.create(user=user) # pylint: disable=no-member
        return user

class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer for the Account model, responsible for serializing 
    the account data including the associated user and balance.
    """
    class Meta:
        """
        The serialized fields include:
        - `id`: The unique identifier of the account.
        - `user`: The user associated with this account.
        - `balance`: The current balance of the account.
        model = Account
        fields = ['id', 'user', 'balance']
         """

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
