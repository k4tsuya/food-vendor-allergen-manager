"""Module containing schemas for the item management app."""

from pydantic import BaseModel, ConfigDict


class ConfigResponse(BaseModel):
    item_label_en: str
    item_label_nl: str
    meat_tracking_enabled: bool
    category_labels: dict[str, dict[str, str]]


class AllergenResponse(BaseModel):
    id: int
    code: str
    description_en: str
    description_nl: str

    model_config = ConfigDict(from_attributes=True)


class MeatTypeResponse(BaseModel):
    id: int
    code: str
    description_en: str
    description_nl: str

    model_config = ConfigDict(from_attributes=True)


class ItemResponse(BaseModel):
    id: int
    name: str
    category_key: str | None = None
    allergens: list[AllergenResponse]
    meat_types: list[MeatTypeResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ItemAllergenView(BaseModel):
    name: str
    allergens: list[str]