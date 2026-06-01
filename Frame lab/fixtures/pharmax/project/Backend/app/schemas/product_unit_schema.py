from pydantic import BaseModel, Field

from example_projects.pharmax.Backend.app.models.product_unit_table import BaseUnit


class CreateProductUnit(BaseModel):
    name: BaseUnit
    price_per_unit: float = Field(gt=0)
    multiplier_to_base: int = Field(ge=1)


class ReadProductUnit(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    name: BaseUnit
    price_per_unit: float
    multiplier_to_base: int


class UpdateProductUnit(BaseModel):
    price_per_unit: float | None = Field(default=None, gt=0)
    multiplier_to_base: int | None = Field(default=None, ge=1)
