"""Tests for custom exception classes."""
from app.core.exceptions import (
    APIException,
    BadRequestError,
    ConflictError,
    NotFoundError,
)


def test_api_exception():
    """Test base APIException."""
    exc = APIException("Test message", 400)
    assert exc.message == "Test message"
    assert exc.status_code == 400
    assert str(exc) == "Test message"


def test_not_found_error():
    """Test NotFoundError exception."""
    exc = NotFoundError("User not found")
    assert exc.message == "User not found"
    assert exc.status_code == 404
    assert isinstance(exc, APIException)


def test_not_found_error_default_message():
    """Test NotFoundError with default message."""
    exc = NotFoundError()
    assert exc.message == "Resource not found"
    assert exc.status_code == 404


def test_conflict_error():
    """Test ConflictError exception."""
    exc = ConflictError("Email already exists")
    assert exc.message == "Email already exists"
    assert exc.status_code == 409
    assert isinstance(exc, APIException)


def test_conflict_error_default_message():
    """Test ConflictError with default message."""
    exc = ConflictError()
    assert exc.message == "Resource conflict"
    assert exc.status_code == 409


def test_bad_request_error():
    """Test BadRequestError exception."""
    exc = BadRequestError("Invalid input")
    assert exc.message == "Invalid input"
    assert exc.status_code == 400
    assert isinstance(exc, APIException)


def test_bad_request_error_default_message():
    """Test BadRequestError with default message."""
    exc = BadRequestError()
    assert exc.message == "Bad request"
    assert exc.status_code == 400

