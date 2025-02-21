from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .models import User, Transaction, Account
from .serializers import UserSerializer, TransactionSerializer, AccountSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)

# Create your views here.
class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def perform_create(self, serializer):
        if User.objects.filter(username=serializer.validated_data['username']).exists():
            raise ValidationError("A user with this username already exists.")
        serializer.save()

class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
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
        return self.request.user.account

class TransactionView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
      
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