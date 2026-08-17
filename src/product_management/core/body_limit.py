"""Request body size limiting middleware."""

import os

from fastapi import Request
from fastapi.responses import JSONResponse

MAX_BODY_SIZE = int(os.getenv("MAX_BODY_SIZE_BYTES", 3 * 1024 * 1024))  # Default: 3MB


async def limit_body_size(request: Request, call_next):
    """Reject requests whose declared body size exceeds MAX_BODY_SIZE.

    Checks the Content-Length header before the body is processed, so
    an oversized request is rejected early rather than being read into
    memory first. The limit is configurable via MAX_BODY_SIZE_BYTES in
    .env (defaults to 3MB), since actual data size needs can vary per
    deployment — e.g. the logo upload alone allows up to 2MB, so this
    ceiling needs enough headroom above that.

    Doesn't protect against a request that lies about its Content-Length
    or omits it (e.g. chunked transfer encoding) — a known, accepted
    limitation given this app's actual traffic pattern (a single admin,
    no public write endpoints).

    Note: when this rejects a request whose body the browser is still
    actively uploading, browsers often report a generic network error
    to client-side JavaScript rather than delivering the 413 response
    cleanly — the connection closing mid-upload looks like a failure,
    not a clean HTTP response. The real fix is validating file/payload
    size client-side before the request is sent (as done for the
    data-import file picker), so oversized requests are never attempted
    in the first place; this backend check remains as a defense-in-depth
    backstop for direct API access that bypasses the frontend.

    Args:
        request: The incoming request.
        call_next: The next handler in the middleware chain.

    Returns:
        A 413 JSON response if the body is too large, otherwise the
        normal response from the rest of the app.
    """
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_BODY_SIZE:
        return JSONResponse(
            status_code=413, content={"detail": "Request body exceeds the maximum allowed size."}
        )

    return await call_next(request)
