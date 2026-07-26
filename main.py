"""Main module for the product management app."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.product_management.routers import items, allergens, health, config, meat_types, auth
from src.product_management.seed.insert_data import load_allergens, load_meat_types, load_items, load_admin, load_categories
from src.product_management.core.database import SessionLocal, engine
from src.product_management.models import Base
from src.product_management.routers import items, allergens, health, config, meat_types, auth, categories
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.product_management.queries import get_settings
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from src.product_management.core.security import limiter


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


app = FastAPI(title="Snack Bar Product API", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="src/product_management/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(items.router)
app.include_router(allergens.router)
app.include_router(health.router)
app.include_router(config.router)
app.include_router(meat_types.router)
app.include_router(auth.router)
app.include_router(categories.router)