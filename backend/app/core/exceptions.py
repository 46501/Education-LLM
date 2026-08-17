class AppError(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

class ResourceNotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, code="RESOURCE_NOT_FOUND", status_code=404)

class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, code="UNAUTHORIZED", status_code=401)

class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, code="FORBIDDEN", status_code=403)

class ValidationError(AppError):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, code="VALIDATION_ERROR", status_code=422)

class ConflictError(AppError):
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, code="CONFLICT", status_code=409)

class LLMServiceError(AppError):
    def __init__(self, message: str = "AI service is temporarily unavailable. Please try again."):
        super().__init__(message, code="AI_SERVICE_UNAVAILABLE", status_code=502)

class DatabaseError(AppError):
    def __init__(self, message: str = "Unable to process your request right now. Please try again."):
        super().__init__(message, code="DATABASE_ERROR", status_code=500)
