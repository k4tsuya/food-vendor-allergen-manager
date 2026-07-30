"""Main module for the product management app."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.product_management.core.database import SessionLocal, engine
from src.product_management.core.logging_config import configure_logging
from src.product_management.core.security import limiter
from src.product_management.models import Base
from src.product_management.queries import get_settings
from src.product_management.routers import (
    allergens,
    auth,
    categories,
    config,
    data,
    health,
    items,
    meat_types,
)
from src.product_management.seed.insert_data import (
    load_admin,
    load_allergens,
    load_categories,
    load_items,
    load_meat_types,
)

configure_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        settings = get_settings(db)
        load_allergens(db)
        load_categories(db)
        if settings.meat_tracking_enabled:
            load_meat_types(db)
        load_items(db)
        load_admin(db)

    yield


app = FastAPI(title="Item Allergens API",
              lifespan=lifespan,
              swagger_ui_parameters={"defaultModelsExpandDepth": 0})


app.mount("/static", StaticFiles(directory="src/product_management/static"), name="static")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

app.include_router(items.router, tags=["Items"])
app.include_router(categories.router, tags=["Categories"])
app.include_router(allergens.router, tags=["Allergens"])
app.include_router(meat_types.router, tags=["Meat Types"])
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, tags=["Authentication"])
app.include_router(config.router, tags=["Settings"])
app.include_router(data.router, tags=["Backup &Restore"])
