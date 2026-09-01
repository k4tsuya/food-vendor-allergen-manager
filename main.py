"""Main module for the product management app."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.trustedhost import TrustedHostMiddleware

from src.product_management.core.backup import start_backup_scheduler
from src.product_management.core.body_limit import limit_body_size
from src.product_management.core.database import SessionLocal, engine
from src.product_management.core.logging_config import configure_logging
from src.product_management.core.security import limiter
from src.product_management.core.security_headers import add_security_headers
from src.product_management.models import Base
from src.product_management.queries import get_settings
from src.product_management.routers import (
    admins,
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
    """Run startup seeding and start the backup scheduler; shut down cleanly on exit."""
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        settings = get_settings(db)
        load_allergens(db)
        load_categories(db)
        if settings.meat_tracking_enabled:
            load_meat_types(db)
        load_items(db)
        load_admin(db)

    scheduler = start_backup_scheduler()

    yield

    scheduler.shutdown()


app = FastAPI(
    title="Item Allergens API",
    lifespan=lifespan,
    swagger_ui_parameters={"defaultModelsExpandDepth": 0},
)


app.mount("/static", StaticFiles(directory="src/product_management/static"), name="static")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.middleware("http")(limit_body_size)
app.middleware("http")(add_security_headers)

trusted_hosts = [
    host.strip() for host in os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1,testserver").split(",")
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=trusted_hosts,
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
app.include_router(admins.router, tags=["Admin Management"])
