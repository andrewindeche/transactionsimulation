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
    