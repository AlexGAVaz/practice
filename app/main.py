import os
from decimal import Decimal

from fastapi import Depends, FastAPI, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Transaction
from app.schemas import (
    LoginRequest,
    LoginResponse,
    SummaryResponse,
    TransactionCreate,
    TransactionRead,
)

app = FastAPI(title="Fintech MVP API", version="1.0.0")

API_TOKEN = os.getenv("API_TOKEN", "demo-token")
DEMO_USER = os.getenv("DEMO_USER", "demo")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "demo123")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


def check_auth(authorization: str = Header(default="")):
    expected = f"Bearer {API_TOKEN}"
    if authorization != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
        )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    if payload.username != DEMO_USER or payload.password != DEMO_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return LoginResponse(access_token=API_TOKEN)


@app.post(
    "/transactions",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_auth)],
)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    obj = Transaction(
        tx_type=payload.tx_type,
        amount=payload.amount,
        description=payload.description,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@app.get(
    "/transactions",
    response_model=list[TransactionRead],
    dependencies=[Depends(check_auth)],
)
def list_transactions(db: Session = Depends(get_db)):
    rows = db.execute(select(Transaction).order_by(Transaction.created_at.desc()))
    return rows.scalars().all()


@app.get(
    "/summary",
    response_model=SummaryResponse,
    dependencies=[Depends(check_auth)],
)
def summary(db: Session = Depends(get_db)):
    rows = db.execute(select(Transaction)).scalars().all()
    total_income = sum((r.amount for r in rows if r.tx_type == "income"), Decimal("0"))
    total_expense = sum((r.amount for r in rows if r.tx_type == "expense"), Decimal("0"))
    return SummaryResponse(
        total_income=total_income,
        total_expense=total_expense,
        balance=total_income - total_expense,
    )
