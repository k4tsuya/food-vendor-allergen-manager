"""Security headers middleware."""

from fastapi import Request


async def add_security_headers(request: Request, call_next):
    """Add security headers to the response.

    Args:
        request: The incoming request.
        call_next: The next handler in the middleware chain.

    Returns:
        The response from the rest of the app, with security headers added.
    """
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    return response
