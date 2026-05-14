"""
Custom exception classes for the application.
"""


class LeadFlowException(Exception):
    """Base exception for LeadFlow application."""
    pass


class ValidationError(LeadFlowException):
    """Raised when input validation fails."""
    pass


class NotFoundError(LeadFlowException):
    """Raised when a requested resource is not found."""
    pass


class DatabaseError(LeadFlowException):
    """Raised when a database operation fails."""
    pass


class AuthenticationError(LeadFlowException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(LeadFlowException):
    """Raised when user lacks permission."""
    pass


class AIServiceError(LeadFlowException):
    """Raised when AI service call fails."""
    pass


class ExternalServiceError(LeadFlowException):
    """Raised when external service (Tavily, Groq, Gemini) fails."""
    pass


class DuplicateResourceError(LeadFlowException):
    """Raised when attempting to create duplicate resource (e.g., duplicate email)."""
    pass


class InvalidStateError(LeadFlowException):
    """Raised when operation invalid for current resource state."""
    pass
