# main.py or src/api/dependencies.py
import secrets  # For secure comparison

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from src.core.config import settings

API_KEY_NAME = "X-API-Key"
api_key_header_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


# The dependency function to verify the API key
async def get_api_key(api_key_header: str | None = Security(api_key_header_scheme)):
    """
    Retrieves the API key from the X-API-Key header and validates it.

    Raises:
        HTTPException (403 Forbidden): If the API key is missing or invalid.
    """
    if not settings.API_KEY:
        # This case means the server itself is misconfigured
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: API Key not set.",
        )

    if api_key_header is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated: Missing API Key",
        )

    # Use secrets.compare_digest for secure comparison to mitigate timing attacks
    is_valid = secrets.compare_digest(api_key_header, settings.API_KEY)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated: Invalid API Key",
        )
    # If valid, the function returns None implicitly, fulfilling the dependency
    # You could also return the key if needed downstream: return api_key_header
