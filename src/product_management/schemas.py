"""Module containing schemas for the item management app."""

from pydantic import BaseModel, ConfigDict

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
    allergens: list[AllergenResponse]
    meat_types: list[MeatTypeResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ItemAllergenView(BaseModel):
    name: str
    allergens: list[str]