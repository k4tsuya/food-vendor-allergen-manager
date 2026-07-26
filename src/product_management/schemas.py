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
    category_key: str | None = None
    allergens: list[AllergenResponse]
    meat_types: list[MeatTypeResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ItemAllergenView(BaseModel):
    name: str
    allergens: list[str]
    
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class ItemCreate(BaseModel):
    name: str
    category_key: str | None = None
    allergen_codes: list[str] = []
    meat_type_codes: list[str] = []


class ItemUpdate(BaseModel):
    name: str
    category_key: str | None = None
    allergen_codes: list[str] = []
    meat_type_codes: list[str] = []


class ItemWriteResponse(BaseModel):
    item: ItemResponse
    warnings: list[str] = []
    
class AllergenCreate(BaseModel):
    code: str
    description_en: str
    description_nl: str


class AllergenUpdate(BaseModel):
    description_en: str
    description_nl: str


class MeatTypeCreate(BaseModel):
    code: str
    description_en: str
    description_nl: str


class MeatTypeUpdate(BaseModel):
    description_en: str
    description_nl: str
    
class CategoryResponse(BaseModel):
    id: int
    code: str
    description_en: str
    description_nl: str

    model_config = ConfigDict(from_attributes=True)


class CategoryCreate(BaseModel):
    code: str
    description_en: str
    description_nl: str


class CategoryUpdate(BaseModel):
    description_en: str
    description_nl: str
    

class SettingsResponse(BaseModel):
    item_label_en: str
    item_label_nl: str
    meat_tracking_enabled: bool

    model_config = ConfigDict(from_attributes=True)


class SettingsUpdate(BaseModel):
    item_label_en: str
    item_label_nl: str
    meat_tracking_enabled: bool