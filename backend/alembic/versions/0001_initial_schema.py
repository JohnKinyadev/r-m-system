"""initial rental management schema

Revision ID: 0001
Revises:
Create Date: 2026-08-26
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    property_status = sa.Enum("active", "inactive", "maintenance", name="propertystatus")
    unit_status = sa.Enum(
        "vacant", "reserved", "occupied", "notice_given", "maintenance", "unavailable",
        name="unitstatus",
    )
    tenant_status = sa.Enum("active", "notice", "former", name="tenantstatus")
    tenancy_status = sa.Enum(
        "pending", "active", "notice_given", "ended", "terminated",
        name="tenancystatus",
    )
    ledger_entry_type = sa.Enum(
        "rent", "water", "electricity", "penalty", "deposit", "payment",
        "adjustment", "reversal", "credit",
        name="ledgerentrytype",
    )
    payment_method = sa.Enum("cash", "mpesa", "bank_transfer", "card", "other", name="paymentmethod")
    payment_status = sa.Enum("pending", "confirmed", "reversed", "failed", name="paymentstatus")
    maintenance_status = sa.Enum(
        "open", "assigned", "in_progress", "resolved", "cancelled",
        name="maintenancestatus",
    )
    maintenance_priority = sa.Enum("low", "normal", "high", "urgent", name="maintenancepriority")
    expense_category = sa.Enum(
        "repairs", "caretaker", "water", "electricity", "security", "garbage", "tax", "other",
        name="expensecategory",
    )
    notification_type = sa.Enum(
        "rent_due", "rent_overdue", "payment_received", "maintenance_update",
        "lease_expiring", "vacancy", "general",
        name="notificationtype",
    )

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
        sa.Column("description", sa.String(255), nullable=True),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "worker_permissions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("module", sa.String(50), nullable=False),
        sa.UniqueConstraint("user_id", "module", name="uq_worker_module"),
    )

    op.create_table(
        "properties",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("property_type", sa.String(80), nullable=False),
        sa.Column("address", sa.String(255), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("status", property_status, nullable=False, server_default="active"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_properties_code", "properties", ["code"], unique=True)

    op.create_table(
        "units",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("property_id", sa.Integer(), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("unit_number", sa.String(50), nullable=False),
        sa.Column("unit_type", sa.String(80), nullable=False),
        sa.Column("floor", sa.String(50), nullable=True),
        sa.Column("bedrooms", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("bathrooms", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("monthly_rent", sa.Numeric(12, 2), nullable=False),
        sa.Column("deposit_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("rent_due_day", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("status", unit_status, nullable=False, server_default="vacant"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("property_id", "unit_number", name="uq_property_unit"),
    )
    op.create_index("ix_units_property_id", "units", ["property_id"])

    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("phone", sa.String(50), nullable=False),
        sa.Column("email", sa.String(255), nullable=True, unique=True),
        sa.Column("national_id", sa.String(80), nullable=True),
        sa.Column("emergency_contact", sa.String(150), nullable=True),
        sa.Column("status", tenant_status, nullable=False, server_default="active"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_tenants_email", "tenants", ["email"], unique=True)
    op.create_index("ix_tenants_phone", "tenants", ["phone"])

    op.create_table(
        "tenancies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("unit_id", sa.Integer(), sa.ForeignKey("units.id"), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("move_out_date", sa.Date(), nullable=True),
        sa.Column("monthly_rent", sa.Numeric(12, 2), nullable=False),
        sa.Column("deposit_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("rent_due_day", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("status", tenancy_status, nullable=False, server_default="active"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_tenancies_tenant_id", "tenancies", ["tenant_id"])
    op.create_index("ix_tenancies_unit_id", "tenancies", ["unit_id"])

    op.create_table(
        "unit_rent_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("unit_id", sa.Integer(), sa.ForeignKey("units.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rent_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("changed_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_unit_rent_history_unit_id", "unit_rent_history", ["unit_id"])

    op.create_table(
        "ledger_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenancy_id", sa.Integer(), sa.ForeignKey("tenancies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("entry_type", ledger_entry_type, nullable=False),
        sa.Column("debit", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("credit", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("reference", sa.String(120), nullable=True),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ledger_entries_tenancy_id", "ledger_entries", ["tenancy_id"])
    op.create_index("ix_ledger_entries_entry_date", "ledger_entries", ["entry_date"])

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenancy_id", sa.Integer(), sa.ForeignKey("tenancies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("method", payment_method, nullable=False, server_default="cash"),
        sa.Column("status", payment_status, nullable=False, server_default="confirmed"),
        sa.Column("reference", sa.String(120), nullable=True),
        sa.Column("provider_transaction_id", sa.String(120), nullable=True),
        sa.Column("payer_phone", sa.String(50), nullable=True),
        sa.Column("received_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_payments_tenancy_id", "payments", ["tenancy_id"])
    op.create_index("ix_payments_payment_date", "payments", ["payment_date"])

    op.create_table(
        "maintenance_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("property_id", sa.Integer(), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("unit_id", sa.Integer(), sa.ForeignKey("units.id"), nullable=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=True),
        sa.Column("assigned_to_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("priority", maintenance_priority, nullable=False, server_default="normal"),
        sa.Column("status", maintenance_status, nullable=False, server_default="open"),
        sa.Column("reported_date", sa.Date(), nullable=False),
        sa.Column("resolved_date", sa.Date(), nullable=True),
        sa.Column("cost", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_maintenance_requests_property_id", "maintenance_requests", ["property_id"])
    op.create_index("ix_maintenance_requests_unit_id", "maintenance_requests", ["unit_id"])
    op.create_index("ix_maintenance_requests_tenant_id", "maintenance_requests", ["tenant_id"])
    op.create_index("ix_maintenance_requests_assigned_to_id", "maintenance_requests", ["assigned_to_id"])

    op.create_table(
        "expenses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("property_id", sa.Integer(), sa.ForeignKey("properties.id"), nullable=True),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("category", expense_category, nullable=False, server_default="other"),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("recorded_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_expenses_property_id", "expenses", ["property_id"])
    op.create_index("ix_expenses_expense_date", "expenses", ["expense_date"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", notification_type, nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("related_entity_type", sa.String(80), nullable=True),
        sa.Column("related_entity_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(120), nullable=False),
        sa.Column("entity_type", sa.String(80), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("old_value", sa.JSON(), nullable=True),
        sa.Column("new_value", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])

    op.create_table(
        "property_assignments",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("property_id", sa.Integer(), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("caretaker_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("property_id", "caretaker_id", name="uq_property_caretaker"),
    )


def downgrade() -> None:
    op.drop_table("property_assignments")
    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs")
    op.drop_index("ix_audit_logs_user_id", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_table("notifications")
    op.drop_index("ix_expenses_expense_date", table_name="expenses")
    op.drop_index("ix_expenses_property_id", table_name="expenses")
    op.drop_table("expenses")
    op.drop_index("ix_maintenance_requests_assigned_to_id", table_name="maintenance_requests")
    op.drop_index("ix_maintenance_requests_tenant_id", table_name="maintenance_requests")
    op.drop_index("ix_maintenance_requests_unit_id", table_name="maintenance_requests")
    op.drop_index("ix_maintenance_requests_property_id", table_name="maintenance_requests")
    op.drop_table("maintenance_requests")
    op.drop_index("ix_payments_payment_date", table_name="payments")
    op.drop_index("ix_payments_tenancy_id", table_name="payments")
    op.drop_table("payments")
    op.drop_index("ix_ledger_entries_entry_date", table_name="ledger_entries")
    op.drop_index("ix_ledger_entries_tenancy_id", table_name="ledger_entries")
    op.drop_table("ledger_entries")
    op.drop_index("ix_unit_rent_history_unit_id", table_name="unit_rent_history")
    op.drop_table("unit_rent_history")
    op.drop_index("ix_tenancies_unit_id", table_name="tenancies")
    op.drop_index("ix_tenancies_tenant_id", table_name="tenancies")
    op.drop_table("tenancies")
    op.drop_index("ix_tenants_phone", table_name="tenants")
    op.drop_index("ix_tenants_email", table_name="tenants")
    op.drop_table("tenants")
    op.drop_index("ix_units_property_id", table_name="units")
    op.drop_table("units")
    op.drop_index("ix_properties_code", table_name="properties")
    op.drop_table("properties")
    op.drop_table("worker_permissions")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_table("roles")

    for enum_name in [
        "notificationtype",
        "expensecategory",
        "maintenancepriority",
        "maintenancestatus",
        "paymentstatus",
        "paymentmethod",
        "ledgerentrytype",
        "tenancystatus",
        "tenantstatus",
        "unitstatus",
        "propertystatus",
    ]:
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
