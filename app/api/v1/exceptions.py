"""Exception handlers for API error responses."""
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import APIException, BadRequestError, ConflictError, NotFoundError

logger = logging.getLogger(__name__)


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle custom API exceptions."""
    logger.warning(f"API error: {exc.message} (status: {exc.status_code})")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "type": exc.__class__.__name__,
                "message": exc.message
            }
        }
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Handle SQLAlchemy IntegrityError (constraint violations)."""
    logger.error(f"Database integrity error: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=409,
        content={
            "success": False,
            "error": {
                "type": "ConflictError",
                "message": "Resource already exists or violates constraints"
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions (500 errors)."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "type": "InternalServerError",
                "message": "An unexpected error occurred"
            }
        }
    )

