# Standard library imports
import logging

# Django imports
from django.db import transaction
from django.db.models import F, Q
from django.core.cache import cache
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist

# Third-party imports
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import AnonRateThrottle

# Local imports
from .serializers import UserSerializer, TransactionSerializer, AccountSerializer
from .throttles import SignupAttemptThrottle, LoginAttemptThrottle
from .models import User, Transaction, Account


logger = logging.getLogger(__name__)

class UserRegisterView(generics.CreateAPIView):
    """
    View to register a new user. It validates input, creates the user, 
    and creates an associated account.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    throttle_classes = [SignupAttemptThrottle, AnonRateThrottle]

    def perform_create(self, serializer):
        user = serializer.save()
        if User.objects.filter(username=serializer.validated_data['username']).exists():
            raise ValidationError("A user with this username already exists.")      
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        if not email:
            raise ValidationError({"email": "Email is required."})
        if not password:
            raise ValidationError({"password": "Password is required."})

        Account.objects.create(user=user)

class UserLoginView(APIView):
    """
    View for user login, which authenticates the user and returns JWT tokens.
    """
    permission_classes = [AllowAny]
    throttle_classes = [LoginAttemptThrottle]

    def post(self, request):
        """
        Validates user credentials and returns access and refresh tokens on successful authentication.
        """
        username_or_email = request.data.get('username_or_email')
        password = request.data.get('password')

        if not username_or_email or not password:
            return Response({'error': 'Username/Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(Q(username=username_or_email) | Q(email=username_or_email))
        except ObjectDoesNotExist:
            return Response({'error': 'Invalid username/email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            if user.is_active:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            return Response({'error': 'User account is inactive'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class AccountView(generics.RetrieveAPIView):
    """
    View to retrieve the authenticated user's account details.
    """
    permission_classes = [IsAuthenticated]
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_object(self):
        """
        Retrieves the user's associated account.
        """
        try:
            return self.request.user.account
        except Account.DoesNotExist:
            raise NotFound("Account not found.")

class TransactionView(generics.CreateAPIView):
    """
    View to handle creating a transaction (either deposit or withdrawal).
    """
    permission_classes = [IsAuthenticated]
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def perform_create(self, serializer):
        """
        Performs the transaction, adjusting account balance.
        """
        user = self.request.user
        account = Account.objects.select_for_update().get(user=user)

        with transaction.atomic():
            amount = serializer.validated_data['amount']
            if serializer.validated_data['transaction_type'] == 'withdrawal':
                if account.balance < amount:
                    raise serializers.ValidationError("Insufficient balance for withdrawal.")
                account.balance = F('balance') - amount
            else:
                account.balance = F('balance') + amount
            account.save()

            serializer.save(user=user)

class TransactionHistoryView(generics.ListAPIView):
    """
    View to retrieve the authenticated user's transaction history.
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieves the user's transaction history, using cache for performance.
        """
        user = self.request.user
        cache_key = f"transaction_history_{user.id}"
        cache_timeout = 60 * 15

        cached_history = cache.get(cache_key)
        if cached_history:
            logger.info(f"Returning cached transaction history for user {user.id}")
            return cached_history

        queryset = Transaction.objects.filter(user=user)
        serialized_data = TransactionSerializer(queryset, many=True).data
        cache.set(cache_key, serialized_data, timeout=cache_timeout)
        logger.info(f"Cached transaction history for user {user.id}")

        return queryset
