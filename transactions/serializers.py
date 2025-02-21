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

    def validate(self, data):
        """
        Validates the uniqueness of the username and email fields.

        Args:
            data (dict): A dictionary containing user input data.

        Raises:
            serializers.ValidationError: If the username or email already 
                                          exists in the system.
        
        Returns:
            dict: The validated input data if no issues are found.
        """
        if User.objects.filter(username=data.get('username')).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        
        if User.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        
        return data

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
    class Meta:
        model = Account
        fields = ['id', 'user', 'balance']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'amount', 'timestamp']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
