from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from rest_framework.permissions import AllowAny
from django.db.models import F,Q
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound
from django.core.cache import cache
from .serializers import UserSerializer, TransactionSerializer, AccountSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import AnonRateThrottle
from .throttles import SignupAttemptThrottle, LoginAttemptThrottle
from .models import User, Transaction, Account
import logging

logger = logging.getLogger(__name__)

# Create your views here.
class UserRegisterView(generics.CreateAPIView):
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
    A view for User logins
    """
    permission_classes = [AllowAny]
    throttle_classes = [LoginAttemptThrottle]

    def post(self, request):
        """
        Validate and Retrieve user by either username or email on POST
        """
        username_or_email = request.data.get('username_or_email')
        password = request.data.get('password')

        if not username_or_email or not password:
            return Response({'error': 'Username/Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        User = get_user_model()
        try:
            user = User.objects.get(Q(username=username_or_email) | Q(email=username_or_email))
        except User.DoesNotExist:
            return Response({'error': 'Invalid username/email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(request, username=user.username, password=password)
        logger.error(f"Authentication failed for username: {user.username}")
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
    permission_classes = [IsAuthenticated]
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_object(self):
        try:
            return self.request.user.account
        except Account.DoesNotExist:
            raise NotFound("Account not found.")


class TransactionView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def perform_create(self, serializer):
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
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        cache_key = f"transaction_history_{user.id}"
        cache_timeout = 60 * 15

        cached_history = cache.get(cache_key)
        if cached_history:
            logger.info(f"Returning cached transaction history for user {user.id}")
            return cached_history

        queryset = Transaction.objects.filter(user=user)
        serialized_data = TransactionSerializer(queryset, many=True).data
        cache.set(cache_key, queryset, timeout=cache_timeout)
        logger.info(f"Cached transaction history for user {user.id}")

        return queryset
