from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db.models.expenses import Expense
from app.db.models.ledger_entries import LedgerEntry
from app.db.models.maintenance_requests import MaintenanceRequest, MaintenanceStatus
from app.db.models.payments import Payment, PaymentStatus
from app.db.models.properties import Property
from app.db.models.tenancies import Tenancy, TenancyStatus
from app.db.models.tenants import Tenant, TenantStatus
from app.db.models.units import Unit, UnitStatus
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _money(value) -> Decimal:
    return value or Decimal("0")


@router.get("/dashboard")
def dashboard_summary(db: Session = Depends(get_db), _=Depends(get_current_user)):
    today = date.today()
    month = today.month
    year = today.year

    active_tenancies = db.query(Tenancy).filter(Tenancy.status.in_([TenancyStatus.active, TenancyStatus.notice_given])).all()
    expected_rent = sum((t.monthly_rent for t in active_tenancies), Decimal("0"))
    collected = _money(
        db.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(
            Payment.status == PaymentStatus.confirmed,
            func.extract("month", Payment.payment_date) == month,
            func.extract("year", Payment.payment_date) == year,
        )
        .scalar()
    )
    expenses = _money(
        db.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(
            func.extract("month", Expense.expense_date) == month,
            func.extract("year", Expense.expense_date) == year,
        )
        .scalar()
    )

    balances = []
    for tenancy in active_tenancies:
        balance = _money(
            db.query(func.coalesce(func.sum(LedgerEntry.debit - LedgerEntry.credit), 0))
            .filter(LedgerEntry.tenancy_id == tenancy.id)
            .scalar()
        )
        balances.append((tenancy, balance))

    outstanding = sum((balance for _, balance in balances if balance > 0), Decimal("0"))
    overdue = [
        {"tenant": t.tenant.full_name, "unit": t.unit.unit_number, "balance": balance}
        for t, balance in balances
        if balance > 0 and t.rent_due_day < today.day
    ]
    partial = [
        {"tenant": t.tenant.full_name, "unit": t.unit.unit_number, "balance": balance}
        for t, balance in balances
        if balance > 0
    ]

    property_count = db.query(Property).count()
    unit_count = db.query(Unit).count()
    occupied_units = db.query(Unit).filter(Unit.status.in_([UnitStatus.occupied, UnitStatus.notice_given])).count()
    vacant_units = db.query(Unit).filter(Unit.status == UnitStatus.vacant).count()
    open_maintenance = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.status.in_([MaintenanceStatus.open, MaintenanceStatus.assigned, MaintenanceStatus.in_progress])
    ).count()
    expiring_soon = db.query(Tenancy).filter(
        Tenancy.status == TenancyStatus.active,
        Tenancy.end_date != None,
        Tenancy.end_date >= today,
        Tenancy.end_date <= today + timedelta(days=30),
    ).count()
    collection_rate = round(float((collected / expected_rent) * 100), 1) if expected_rent else 0

    return {
        "period": today.strftime("%B %Y"),
        "expected_rent": expected_rent,
        "collected_rent": collected,
        "outstanding_rent": outstanding,
        "expenses": expenses,
        "net_income": collected - expenses,
        "collection_rate": collection_rate,
        "properties": property_count,
        "units": unit_count,
        "occupied_units": occupied_units,
        "vacant_units": vacant_units,
        "active_tenants": db.query(Tenant).filter(Tenant.status == TenantStatus.active).count(),
        "overdue_tenants": len(overdue),
        "open_maintenance": open_maintenance,
        "leases_expiring_soon": expiring_soon,
        "needs_attention": [
            {"label": "Tenants overdue", "count": len(overdue), "severity": "red"},
            {"label": "Partial or outstanding balances", "count": len(partial), "severity": "amber"},
            {"label": "Open maintenance requests", "count": open_maintenance, "severity": "orange"},
            {"label": "Vacant units", "count": vacant_units, "severity": "blue"},
            {"label": "Leases expiring soon", "count": expiring_soon, "severity": "yellow"},
        ],
    }


@router.get("/arrears")
def arrears_report(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = []
    tenancies = db.query(Tenancy).filter(Tenancy.status.in_([TenancyStatus.active, TenancyStatus.notice_given])).all()
    for tenancy in tenancies:
        balance = _money(
            db.query(func.coalesce(func.sum(LedgerEntry.debit - LedgerEntry.credit), 0))
            .filter(LedgerEntry.tenancy_id == tenancy.id)
            .scalar()
        )
        if balance > 0:
            rows.append({
                "tenancy_id": tenancy.id,
                "tenant": tenancy.tenant.full_name,
                "property": tenancy.unit.property.name,
                "unit": tenancy.unit.unit_number,
                "balance": balance,
                "rent_due_day": tenancy.rent_due_day,
            })
    return sorted(rows, key=lambda r: r["balance"], reverse=True)


@router.get("/property-performance")
def property_performance_report(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = (
        db.query(
            Property.id,
            Property.name,
            func.count(Unit.id).label("units"),
            func.sum(Unit.monthly_rent).label("monthly_rent"),
        )
        .outerjoin(Unit, Unit.property_id == Property.id)
        .group_by(Property.id, Property.name)
        .all()
    )
    return [
        {
            "property_id": row.id,
            "property": row.name,
            "units": row.units,
            "monthly_rent": row.monthly_rent or 0,
        }
        for row in rows
    ]
