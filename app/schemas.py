from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TransactionCreate(BaseModel):
    tx_type: Literal["income", "expense"]
    amount: Decimal = Field(gt=0)
    description: str | None = None


class TransactionRead(BaseModel):
    id: int
    tx_type: str
    amount: Decimal
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SummaryResponse(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
