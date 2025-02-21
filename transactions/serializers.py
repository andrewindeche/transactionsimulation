from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Account, Transaction

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model that handles user creation, validation, and
    password handling. It ensures that the username and email are unique
    before creating a new user.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'password': {'write_only': True, 'required': True}
        }

    def validate(self, attrs):
        """
        Validates the uniqueness of the username and email fields.

        Args:
            attrs (dict): A dictionary containing user input data.

        Raises:
            serializers.ValidationError: If the username or email already 
                                          exists in the system.
        
        Returns:
            dict: The validated input data if no issues are found.
        """
        if User.objects.filter(username=attrs.get('username')).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        
        if User.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        
        return attrs

    def create(self, validated_data):
        """
        Creates a new user and an associated account.

        Args:
            validated_data (dict): A dictionary containing validated data.

        Returns:
            user (User): The newly created User object.
        """
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

