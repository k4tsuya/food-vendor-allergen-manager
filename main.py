"""Main module for the product management app."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.product_management.routers import items, allergens, health, config, meat_types, auth
from src.product_management.seed.insert_data import load_allergens, load_meat_types, load_items, load_admin
from src.product_management.core.database import SessionLocal, engine
from src.product_management.core.config import ENABLE_MEAT_TRACKING
from src.product_management.models import Base
from src.product_management.routers import items, allergens, health, config, meat_types
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        load_allergens(db)
        if ENABLE_MEAT_TRACKING:
            load_meat_types(db)
        load_items(db)
        load_admin(db)
    yield


app = FastAPI(title="Snack Bar Product API", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="src/product_management/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router)
app.include_router(allergens.router)
app.include_router(health.router)
app.include_router(config.router)
app.include_router(meat_types.router)
app.include_router(auth.router)