from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .models import User, Transaction, Account
from rest_framework.permissions import AllowAny
from django.db.models import F
from .serializers import UserSerializer, TransactionSerializer, AccountSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import AnonRateThrottle
from .throttles import SignupAttemptThrottle 
from .throttles import LoginAttemptThrottle 
import logging

logger = logging.getLogger(__name__)

# Create your views here.
class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    throttle_classes = [SignupAttemptThrottle, AnonRateThrottle]
    
    def perform_create(self, serializer):
        if User.objects.filter(username=serializer.validated_data['username']).exists():
            raise ValidationError("A user with this username already exists.")
        
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        
        if not email:
            raise ValidationError({"email": "Email is required."})
        if not password:
            raise ValidationError({"password": "Password is required."})
        serializer.save()

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginAttemptThrottle]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            else:
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
        account = Account.objects.select_for_update().get(user=user)  # Lock the account row

        with transaction.atomic():
            amount = serializer.validated_data['amount']

            if serializer.validated_data['transaction_type'] == 'withdrawal':
                if account.balance < amount:
                    raise serializers.ValidationError("Insufficient balance for withdrawal.")
                account.balance = F('balance') - amount 
            else:  # 'deposit'
                account.balance = F('balance') + amount
            
            account.save() 

            # Save the transaction
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