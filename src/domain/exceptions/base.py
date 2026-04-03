class AppBaseException(Exception):
    """Base exception for all application errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class DomainException(AppBaseException):
    """Exception for business rule violations."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message, status_code)

class AutomationError(AppBaseException):
    """Exception for browser automation failures."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message, status_code)

class NotFoundException(DomainException):
    """Exception for missing resources."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)
