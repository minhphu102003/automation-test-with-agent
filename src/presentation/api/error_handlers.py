from fastapi import Request, status
from fastapi.responses import JSONResponse
from src.domain.exceptions.base import AppBaseException
import traceback

async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler to ensure consistent JSON error responses.
    """
    if isinstance(exc, AppBaseException):
        # We know these are our domain exceptions
        print(f"--- [Domain Exception] {exc.message} ---")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "type": type(exc).__name__}
        )
    
    # Generic unhandled exceptions
    print(f"--- [Unhandled Exception] ---")
    traceback.print_exc()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": f"An unexpected error occurred: {str(exc)}",
            "type": type(exc).__name__
        }
    )
