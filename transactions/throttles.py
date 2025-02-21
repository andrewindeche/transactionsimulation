"""
This module contains the custom throttling classes for controlling 
rate limits on API views based on user actions.
"""
from rest_framework.throttling import UserRateThrottle

class LoginAttemptThrottle(UserRateThrottle):
    """
    Custom class to throttle login attempts
    """
    scope = 'login'
class SignupAttemptThrottle(UserRateThrottle):
    """
    Custom class to throttle signup attempts
    """
    scope = 'signup'
