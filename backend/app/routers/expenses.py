from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import require_module
from app.db.models.expenses import Expense
from app.db.models.properties import Property
from app.db.session import get_db
from app.schemas.expenses import ExpenseCreate, ExpenseRead, ExpenseUpdate

router = APIRouter(prefix="/api/expenses", tags=["expenses"])


def _enrich(expense: Expense) -> dict:
    return {
        **{c.name: getattr(expense, c.name) for c in Expense.__table__.columns},
        "property_name": expense.property.name if expense.property else None,
    }


@router.get("", response_model=List[ExpenseRead])
def list_expenses(db: Session = Depends(get_db), _=Depends(require_module("expenses"))):
    return [_enrich(e) for e in db.query(Expense).order_by(Expense.expense_date.desc(), Expense.id.desc()).all()]


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_module("expenses")),
):
    if payload.property_id and not db.query(Property).filter(Property.id == payload.property_id).first():
        raise HTTPException(status_code=404, detail="Property not found")
    expense = Expense(**payload.model_dump(), recorded_by_id=current_user.id)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return _enrich(expense)


@router.patch("/{expense_id}", response_model=ExpenseRead)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_module("expenses")),
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return _enrich(expense)
