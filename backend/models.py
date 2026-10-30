
from typing import Literal
from pydantic import BaseModel, Field


class Donation(BaseModel):
    company_name: str = Field(min_length=1)
    device_type: Literal["Laptop", "Desktop"]
    quantity: int = Field(gt=0)
    condition: Literal["Good", "Fair", "Poor"]
    uniform_models: bool
    pickup_cost: float = Field(ge=0)


class EvaluationSettings(BaseModel):
    sale_price: float = Field(default=140, ge=0)
    parts_cost: float = Field(default=25, ge=0)
    labour_hours: float = Field(default=1.5, gt=0)
    hourly_labour_value: float = Field(default=18, ge=0)

    # Actual expense and donor fee are separate
    collection_expense: float | None = Field(default=None, ge=0)
    pickup_fee_revenue: float = Field(default=0, ge=0)

    # Available capacity for one donation batch
    available_labour_hours: float = Field(default=40, ge=0)
    available_storage_slots: int = Field(default=50, ge=0)

    # Estimated usable-device rates
    conservative_rate: float = Field(default=0.40, ge=0, le=1)
    expected_rate: float | None = Field(default=None, ge=0, le=1)
    optimistic_rate: float = Field(default=0.95, ge=0, le=1)


class EvaluationRequest(BaseModel):
    donation: Donation
    settings: EvaluationSettings = Field(
        default_factory=EvaluationSettings
    )
