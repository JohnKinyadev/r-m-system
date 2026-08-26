from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.models.expenses import Expense, ExpenseCategory
from app.db.models.ledger_entries import LedgerEntry, LedgerEntryType
from app.db.models.maintenance_requests import MaintenancePriority, MaintenanceRequest, MaintenanceStatus
from app.db.models.notifications import Notification, NotificationType
from app.db.models.payments import Payment, PaymentMethod
from app.db.models.permissions import AVAILABLE_MODULES, WorkerPermission
from app.db.models.properties import Property
from app.db.models.property_assignments import PropertyAssignment
from app.db.models.roles import Role
from app.db.models.tenancies import Tenancy, TenancyStatus
from app.db.models.tenants import Tenant
from app.db.models.units import Unit, UnitStatus
from app.db.models.users import User


def seed_roles(db: Session) -> None:
    for name, desc in [
        ("landlord", "Full access to portfolio, financials, configuration, and users"),
        ("caretaker", "Operational access controlled by landlord permissions"),
    ]:
        if not db.query(Role).filter(Role.name == name).first():
            db.add(Role(name=name, description=desc))
    db.commit()


def seed_default_owner(db: Session) -> None:
    owner_role = db.query(Role).filter(Role.name == "landlord").first()
    if owner_role and not db.query(User).filter(User.email == "admin@rental.co.ke").first():
        db.add(User(
            full_name="Rental Admin",
            email="admin@rental.co.ke",
            hashed_password=hash_password("Password123"),
            role_id=owner_role.id,
        ))
        db.commit()


def seed_users(db: Session) -> None:
    caretaker_role = db.query(Role).filter(Role.name == "caretaker").first()
    users = [
        ("John Kamau", "john.kamau@rental.ke"),
        ("Mary Wanjiku", "mary.wanjiku@rental.ke"),
        ("Peter Ochieng", "peter.ochieng@rental.ke"),
    ]
    for full_name, email in users:
        if not db.query(User).filter(User.email == email).first():
            db.add(User(
                full_name=full_name,
                email=email,
                hashed_password=hash_password("Password123"),
                role_id=caretaker_role.id,
            ))
    db.commit()

    for user in db.query(User).join(Role).filter(Role.name == "caretaker").all():
        existing = {p.module for p in user.permissions}
        for module in AVAILABLE_MODULES:
            if module not in existing:
                db.add(WorkerPermission(user_id=user.id, module=module))
    db.commit()


def seed_properties(db: Session) -> None:
    rows = [
        ("GV", "Greenview Apartments", "Apartment Block", "Kilimani Road", "Nairobi"),
        ("SB", "Sunrise Bedsitters", "Bedsitter Court", "Thika Road", "Nairobi"),
        ("US", "Umoja Single Rooms", "Single Rooms", "Umoja Estate", "Nairobi"),
    ]
    for code, name, property_type, address, city in rows:
        if not db.query(Property).filter(Property.code == code).first():
            db.add(Property(code=code, name=name, property_type=property_type, address=address, city=city))
    db.commit()


def seed_units(db: Session) -> None:
    units = [
        ("GV", "A01", "1 Bedroom", 1, 1, "28000", "28000", UnitStatus.occupied),
        ("GV", "A02", "2 Bedroom", 2, 2, "42000", "42000", UnitStatus.occupied),
        ("GV", "A03", "Studio", 1, 1, "22000", "22000", UnitStatus.vacant),
        ("GV", "B01", "1 Bedroom", 1, 1, "30000", "30000", UnitStatus.maintenance),
        ("SB", "B01", "Bedsitter", 1, 1, "12000", "12000", UnitStatus.occupied),
        ("SB", "B02", "Bedsitter", 1, 1, "12000", "12000", UnitStatus.occupied),
        ("SB", "B03", "Bedsitter", 1, 1, "11500", "11500", UnitStatus.vacant),
        ("US", "01", "Single Room", 1, 1, "7500", "7500", UnitStatus.occupied),
        ("US", "02", "Single Room", 1, 1, "7500", "7500", UnitStatus.vacant),
    ]
    for code, number, unit_type, bedrooms, bathrooms, rent, deposit, status in units:
        prop = db.query(Property).filter(Property.code == code).first()
        if not prop:
            continue
        exists = db.query(Unit).filter(Unit.property_id == prop.id, Unit.unit_number == number).first()
        if not exists:
            db.add(Unit(
                property_id=prop.id,
                unit_number=number,
                unit_type=unit_type,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                monthly_rent=Decimal(rent),
                deposit_amount=Decimal(deposit),
                rent_due_day=5,
                status=status,
            ))
    db.commit()


def seed_tenants(db: Session) -> None:
    rows = [
        ("Jane Wanjiku", "0712345678", "jane.wanjiku@example.com", "34567890"),
        ("Daniel Otieno", "0722111444", "daniel.otieno@example.com", "28765431"),
        ("Amina Hassan", "0700555444", "amina.hassan@example.com", "11223344"),
        ("Brian Mwangi", "0799888777", "brian.mwangi@example.com", "99887766"),
        ("Faith Njeri", "0744555666", "faith.njeri@example.com", "66778899"),
    ]
    for full_name, phone, email, national_id in rows:
        if not db.query(Tenant).filter(Tenant.email == email).first():
            db.add(Tenant(
                full_name=full_name,
                phone=phone,
                email=email,
                national_id=national_id,
                emergency_contact="Emergency contact on file",
            ))
    db.commit()


def _unit(db: Session, property_code: str, unit_number: str) -> Unit | None:
    return (
        db.query(Unit)
        .join(Property)
        .filter(Property.code == property_code, Unit.unit_number == unit_number)
        .first()
    )


def _tenant(db: Session, email: str) -> Tenant | None:
    return db.query(Tenant).filter(Tenant.email == email).first()


def seed_tenancies_and_ledger(db: Session) -> None:
    owner = db.query(User).filter(User.email == "admin@rental.co.ke").first()
    start = date.today().replace(day=1)
    rows = [
        ("jane.wanjiku@example.com", "GV", "A01", "28000", "28000", "800", "10000", "partial rent payment"),
        ("daniel.otieno@example.com", "GV", "A02", "42000", "42000", "1200", "43200", "full month payment"),
        ("amina.hassan@example.com", "SB", "B01", "12000", "12000", "700", "0", "awaiting payment"),
        ("brian.mwangi@example.com", "SB", "B02", "12000", "12000", "600", "12600", "full month payment"),
        ("faith.njeri@example.com", "US", "01", "7500", "7500", "300", "5000", "partial rent payment"),
    ]
    for email, code, number, rent, deposit, water, paid, note in rows:
        tenant = _tenant(db, email)
        unit = _unit(db, code, number)
        if not tenant or not unit:
            continue
        tenancy = (
            db.query(Tenancy)
            .filter(Tenancy.tenant_id == tenant.id, Tenancy.unit_id == unit.id, Tenancy.status == TenancyStatus.active)
            .first()
        )
        if not tenancy:
            tenancy = Tenancy(
                tenant_id=tenant.id,
                unit_id=unit.id,
                start_date=start - timedelta(days=60),
                monthly_rent=Decimal(rent),
                deposit_amount=Decimal(deposit),
                rent_due_day=5,
                status=TenancyStatus.active,
                notes=note,
            )
            db.add(tenancy)
            unit.status = UnitStatus.occupied
            db.commit()
            db.refresh(tenancy)

        if not db.query(LedgerEntry).filter(LedgerEntry.tenancy_id == tenancy.id).first():
            db.add(LedgerEntry(
                tenancy_id=tenancy.id,
                entry_date=start,
                description=f"{start:%B %Y} rent",
                entry_type=LedgerEntryType.rent,
                debit=Decimal(rent),
                created_by_id=owner.id if owner else None,
            ))
            db.add(LedgerEntry(
                tenancy_id=tenancy.id,
                entry_date=start,
                description=f"{start:%B %Y} water charge",
                entry_type=LedgerEntryType.water,
                debit=Decimal(water),
                created_by_id=owner.id if owner else None,
            ))
            if Decimal(paid) > 0:
                reference = f"MPESA-{tenancy.id:04d}"
                db.add(Payment(
                    tenancy_id=tenancy.id,
                    amount=Decimal(paid),
                    payment_date=start + timedelta(days=2),
                    method=PaymentMethod.mpesa,
                    reference=reference,
                    payer_phone=tenant.phone,
                    received_by_id=owner.id if owner else None,
                    notes=note,
                ))
                db.add(LedgerEntry(
                    tenancy_id=tenancy.id,
                    entry_date=start + timedelta(days=2),
                    description=f"Payment received from {tenant.full_name}",
                    entry_type=LedgerEntryType.payment,
                    credit=Decimal(paid),
                    reference=reference,
                    created_by_id=owner.id if owner else None,
                ))
    db.commit()


def seed_maintenance(db: Session) -> None:
    rows = [
        ("GV", "B01", None, "Repaint after plumbing repair", MaintenancePriority.normal, MaintenanceStatus.in_progress, "9500"),
        ("SB", "B01", "amina.hassan@example.com", "Kitchen tap leaking", MaintenancePriority.high, MaintenanceStatus.open, "0"),
        ("US", "01", "faith.njeri@example.com", "Window latch replacement", MaintenancePriority.low, MaintenanceStatus.resolved, "1200"),
    ]
    for code, unit_number, tenant_email, title, priority, item_status, cost in rows:
        prop = db.query(Property).filter(Property.code == code).first()
        unit = _unit(db, code, unit_number)
        tenant = _tenant(db, tenant_email) if tenant_email else None
        if prop and not db.query(MaintenanceRequest).filter(MaintenanceRequest.title == title).first():
            db.add(MaintenanceRequest(
                property_id=prop.id,
                unit_id=unit.id if unit else None,
                tenant_id=tenant.id if tenant else None,
                title=title,
                description="Seeded operational maintenance item",
                priority=priority,
                status=item_status,
                reported_date=date.today() - timedelta(days=3),
                resolved_date=date.today() - timedelta(days=1) if item_status == MaintenanceStatus.resolved else None,
                cost=Decimal(cost),
            ))
    db.commit()


def seed_expenses(db: Session) -> None:
    rows = [
        ("GV", ExpenseCategory.repairs, "Plumbing and paint work", "9500"),
        ("SB", ExpenseCategory.water, "Shared water bill", "8200"),
        ("US", ExpenseCategory.security, "Night guard contribution", "5000"),
        (None, ExpenseCategory.caretaker, "Caretaker allowance", "20000"),
    ]
    for code, category, description, amount in rows:
        prop = db.query(Property).filter(Property.code == code).first() if code else None
        exists = db.query(Expense).filter(Expense.description == description).first()
        if not exists:
            db.add(Expense(
                property_id=prop.id if prop else None,
                expense_date=date.today().replace(day=10),
                category=category,
                amount=Decimal(amount),
                description=description,
            ))
    db.commit()


def seed_notifications(db: Session) -> None:
    owner = db.query(User).filter(User.email == "admin@rental.co.ke").first()
    if not owner:
        return
    rows = [
        (NotificationType.rent_overdue, "Rent overdue", "Amina Hassan has an outstanding balance for Unit B01."),
        (NotificationType.maintenance_update, "Maintenance needs review", "Kitchen tap leaking is still open at Sunrise Bedsitters."),
        (NotificationType.vacancy, "Vacant units", "Three units are vacant across the portfolio."),
    ]
    for notification_type, title, message in rows:
        if not db.query(Notification).filter(Notification.user_id == owner.id, Notification.title == title).first():
            db.add(Notification(user_id=owner.id, type=notification_type, title=title, message=message))
    db.commit()


def seed_property_assignments(db: Session) -> None:
    john = db.query(User).filter(User.email == "john.kamau@rental.ke").first()
    greenview = db.query(Property).filter(Property.code == "GV").first()
    if john and greenview and not db.query(PropertyAssignment).filter(
        PropertyAssignment.property_id == greenview.id,
        PropertyAssignment.caretaker_id == john.id,
    ).first():
        db.add(PropertyAssignment(property_id=greenview.id, caretaker_id=john.id))
        db.commit()


def init_db(db: Session) -> None:
    seed_roles(db)
    seed_default_owner(db)
    seed_users(db)
    seed_properties(db)
    seed_units(db)
    seed_tenants(db)
    seed_tenancies_and_ledger(db)
    seed_maintenance(db)
    seed_expenses(db)
    seed_notifications(db)
    seed_property_assignments(db)
