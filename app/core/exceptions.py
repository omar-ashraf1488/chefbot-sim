"""Custom exception classes for API error handling."""


class APIException(Exception):
    """Base exception class for all API exceptions."""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(APIException):
    """Exception raised when a resource is not found."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ConflictError(APIException):
    """Exception raised when there's a resource conflict."""
    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status_code=409)


class BadRequestError(APIException):
    """Exception raised when request parameters are invalid."""
    
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, status_code=400)

