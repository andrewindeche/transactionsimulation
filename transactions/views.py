"""
Import for logging
"""
import logging

# Django imports
from django.db import transaction
from django.db.models import F, Q
from django.core.cache import cache
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist

# Third-party imports
from rest_framework import generics, status
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from transactions.tasks import process_transaction

# Local imports
from .serializers import UserSerializer, TransactionSerializer, AccountSerializer
from .throttles import SignupAttemptThrottle, LoginAttemptThrottle
from .models import User, Transaction, Account


logger = logging.getLogger(__name__)

class UserRegisterView(generics.CreateAPIView):
    """
    API view for registering a new user. Handles the creation of a new user
    by validating input and automatically creating an associated account.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    throttle_classes = [SignupAttemptThrottle,AnonRateThrottle]

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Handles user creation and associated account creation. This method is
        called when the serializer is valid and the user is ready to be created.

        Args:
            serializer (UserSerializer): The validated serializer containing
                                          the user data.

        Returns:
            None: Automatically handles user and account creation.
        """
        try:
            user = serializer.save()
            print(f"User created: {user.username}")

            if not Account.objects.filter(user=user).exists(): # pylint: disable=no-member
                Account.objects.create(user=user) # pylint: disable=no-member
                print(f"Account created for user: {user.username}") # pylint: disable=no-member
        except Exception as e:
            print(f"Error during user creation: {e}")
            raise ValidationError(f"Failed to create user: {str(e)}") from e


class UserLoginView(APIView):
    """
    View for user login, which authenticates the user and returns JWT tokens.
    """
    permission_classes = [AllowAny]
    throttle_classes = [LoginAttemptThrottle]

    def post(self, request):
        """
        Validates user credentials and 
        returns access and refresh tokens 
        on successful authentication.
        """
        username_or_email = request.data.get('username_or_email')
        password = request.data.get('password')
        if not username_or_email or not password:
            return Response(
                {'error': 'Username/Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = None
        try:
            user = User.objects.get(Q(username=username_or_email) | Q(email=username_or_email))
        except ObjectDoesNotExist:
            return Response(
                {'error': 'Invalid username/email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if check_password(password, user.password):
            if user.is_active:
                if isinstance(user, User):
                    print(f"User is instance of User model: {isinstance(user, User)}")
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    })
                else:
                    return Response(
                        {'error': 'User instance error'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            return Response(
                {'error': 'User account is inactive'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        else:
            print("Password does not match.")
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class AccountView(generics.RetrieveAPIView):
    """
    View to retrieve the authenticated user's account details.
    """
    permission_classes = [IsAuthenticated]
    queryset = Account.objects.all() # pylint: disable=no-member
    serializer_class = AccountSerializer

    # pylint: disable=no-member
    def get_object(self):
        """
        Retrieves the user's associated account.
        """
        try:
            return self.request.user.account
        except Account.DoesNotExist as exc:
            raise NotFound("Account not found.")from exc

class TransactionView(generics.CreateAPIView):
    """
    View to handle creating a transaction (either deposit or withdrawal).
    """
    permission_classes = [IsAuthenticated]
    queryset = Transaction.objects.all() # pylint: disable=no-member
    serializer_class = TransactionSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Handles user creation and associated account creation.
        """
        try:
           transaction_instance = serializer.save(user=self.request.user)

           print(f"Transaction created for user: {self.request.user.username}")

           validated = serializer.validated_data
           transaction_data = {
                k: v for k, v in validated.items() if k not in ['amount', 'transaction_type']
            }

            # Schedule async processing after commit
           transaction.on_commit(lambda: process_transaction.delay(
                self.request.user.id,
                validated['amount'],
                validated['transaction_type'],
                transaction_data
            ))

        except Exception as e:
            print(f"Error during transaction creation: {e}")
            raise ValidationError(f"Failed to create transaction: {str(e)}") from e

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
            logger.info("Returning cached transaction history for user %s", user.id)
            return cached_history

        queryset = Transaction.objects.filter(user=user) # pylint: disable=no-member
        serialized_data = TransactionSerializer(queryset, many=True).data # pylint: disable=no-member
        cache.set(cache_key, serialized_data, timeout=cache_timeout)
        logger.info("Cached transaction history for user %s", user.id)

        return queryset
