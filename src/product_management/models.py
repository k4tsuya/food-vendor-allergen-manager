"""Module containing models for the item management app."""

from sqlalchemy import Column, ForeignKey, Numeric, String, Table
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

from src.product_management.core.database import engine, SessionLocal

class Base(DeclarativeBase):
    pass


item_allergen = Table(
    "item_allergen",
    Base.metadata,
    Column("item_id", ForeignKey("items.id"), primary_key=True),
    Column("allergen_id", ForeignKey("allergens.id"), primary_key=True),
)

item_meat_type = Table(
    "item_meat_type",
    Base.metadata,
    Column("item_id", ForeignKey("items.id"), primary_key=True),
    Column("meat_type_id", ForeignKey("meat_types.id"), primary_key=True),
)


class Allergen(Base):
    __tablename__ = "allergens"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description_en: Mapped[str] = mapped_column(String(200), nullable=False)
    description_nl: Mapped[str] = mapped_column(String(200), nullable=False)

    items: Mapped[list["Item"]] = relationship(
        secondary=item_allergen,
        back_populates="allergens",
    )


class MeatType(Base):
    __tablename__ = "meat_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description_en: Mapped[str] = mapped_column(String(200), nullable=False)
    description_nl: Mapped[str] = mapped_column(String(200), nullable=False)

    items: Mapped[list["Item"]] = relationship(
        secondary=item_meat_type,
        back_populates="meat_types",
    )


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category_key: Mapped[str] = mapped_column(String(100), nullable=True)
    
    
    allergens: Mapped[list[Allergen]] = relationship(
        secondary=item_allergen,
        back_populates="items",
    )
    meat_types: Mapped[list["MeatType"]] = relationship(
        secondary=item_meat_type,
        back_populates="items",
    )

class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description_en: Mapped[str] = mapped_column(String(200), nullable=False)
    description_nl: Mapped[str] = mapped_column(String(200), nullable=False)