"""Convert UUID string columns to native PostgreSQL UUID

Revision ID: 7e2ab1f4d9c2
Revises: 2fefb74fd050
Create Date: 2026-04-05 20:58:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "7e2ab1f4d9c2"
down_revision: Union[str, Sequence[str], None] = "2fefb74fd050"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


UUID_TYPE = postgresql.UUID(as_uuid=False)
VARCHAR36 = sa.String(length=36)


def _is_postgresql() -> bool:
    return op.get_context().dialect.name == "postgresql"


def _drop_foreign_keys_for_column(table_name: str, column_name: str) -> None:
    bind = op.get_bind()
    result = bind.execute(
        sa.text(
            """
            SELECT con.conname
            FROM pg_constraint con
            JOIN pg_class rel ON rel.oid = con.conrelid
            JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
            JOIN unnest(con.conkey) AS ck(attnum) ON TRUE
            JOIN pg_attribute att ON att.attrelid = rel.oid AND att.attnum = ck.attnum
            WHERE con.contype = 'f'
              AND nsp.nspname = current_schema()
              AND rel.relname = :table_name
              AND att.attname = :column_name
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    )
    for row in result:
        op.drop_constraint(row[0], table_name, type_="foreignkey")


def _drop_uuid_related_foreign_keys() -> None:
    fk_columns = [
        ("product_units", "product_id"),
        ("stock_adjustments", "product_id"),
        ("stock_adjustments", "created_by_user_id"),
        ("stock_adjustments", "approved_by_user_id"),
        ("invoices", "sold_by_id"),
        ("invoices", "finalized_by_id"),
        ("invoices", "dispensed_by_id"),
        ("invoice_items", "invoice_id"),
        ("invoice_items", "product_id"),
        ("invoice_items", "product_unit_id"),
        ("audit_logs", "user_id"),
    ]
    for table_name, column_name in fk_columns:
        _drop_foreign_keys_for_column(table_name, column_name)


def _alter_columns_to_uuid() -> None:
    op.alter_column(
        "users",
        "id",
        type_=UUID_TYPE,
        existing_type=VARCHAR36,
        postgresql_using="id::uuid",
    )
    op.alter_column(
        "products",
        "id",
        type_=UUID_TYPE,
        existing_type=VARCHAR36,
        postgresql_using="id::uuid",
    )
    op.alter_column(
        "product_units",
        "id",
        type_=UUID_TYPE,
        existing_type=VARCHAR36,
        postgresql_using="id::uuid",
    )
    op.alter_column(
        "product_units",
        "product_id",
        type_=UUID_TYPE,
        existing_type=VARCHAR36,
        postgresql_using="product_id::uuid",
    )
    op.alter_column(
        "stock_adjustments",
        "id",
        type_=UUID_TYPE,
        existing_type=VARCHAR36,
        postgresql_using="id::uuid",
    )
    op.alter_column(
        "stock_adjustments",
        "product_id",
        type_=UUID_TYPE,
        existing_type=VARCHAR36,
        postgresql_using="product_id::uuid",
    )
    op.alter_column(
        "stock_adjustments",
        "created_by_user_id",
        type_=UUID_TYPE,
        existing_type=VARCHAR36,
        postgresql_using="created_by_user_id::uuid",
    )
    op.alter_column(
        "stock_adjustments",
        "approved_by_user_id",
        type_=UUID_TYPE,
        existing_type=VARCHAR36,
        postgresql_using="approved_by_user_id::uuid",
    )
    op.alter_column(
        "invoices",
        "id",
        type_=UUID_TYPE,
        existing_type=VARCHAR36,
        postgresql_using="id::uuid",
    )
    op.alter_column(
        "invoices",
        "sold_by_id",
        type_=UUID_TYPE,
        existing_type=VARCHAR36,
        postgresql_using="sold_by_id::uuid",
    )
    op.alter_column(
        "invoices",
        "finalized_by_id",
        type_=UUID_TYPE,
        existing_type=VARCHAR36,
        postgresql_using="finalized_by_id::uuid",
    )
    op.alter_column(
        "invoices",
        "dispensed_by_id",
        type_=UUID_TYPE,
        existing_type=VARCHAR36,
        postgresql_using="dispensed_by_id::uuid",
    )
    op.alter_column(
        "invoice_items",
        "id",
        type_=UUID_TYPE,
        existing_type=VARCHAR36,
        postgresql_using="id::uuid",
    )
    op.alter_column(
        "invoice_items",
        "invoice_id",
        type_=UUID_TYPE,
        existing_type=VARCHAR36,
        postgresql_using="invoice_id::uuid",
    )
    op.alter_column(
        "invoice_items",
        "product_id",
        type_=UUID_TYPE,
        existing_type=VARCHAR36,
        postgresql_using="product_id::uuid",
    )
    op.alter_column(
        "invoice_items",
        "product_unit_id",
        type_=UUID_TYPE,
        existing_type=VARCHAR36,
        postgresql_using="product_unit_id::uuid",
    )
    op.alter_column(
        "audit_logs",
        "id",
        type_=UUID_TYPE,
        existing_type=VARCHAR36,
        postgresql_using="id::uuid",
    )
    op.alter_column(
        "audit_logs",
        "user_id",
        type_=UUID_TYPE,
        existing_type=VARCHAR36,
        postgresql_using="user_id::uuid",
    )


def _alter_columns_to_varchar() -> None:
    op.alter_column(
        "users",
        "id",
        type_=VARCHAR36,
        existing_type=UUID_TYPE,
        postgresql_using="id::text",
    )
    op.alter_column(
        "products",
        "id",
        type_=VARCHAR36,
        existing_type=UUID_TYPE,
        postgresql_using="id::text",
    )
    op.alter_column(
        "product_units",
        "id",
        type_=VARCHAR36,
        existing_type=UUID_TYPE,
        postgresql_using="id::text",
    )
    op.alter_column(
        "product_units",
        "product_id",
        type_=VARCHAR36,
        existing_type=UUID_TYPE,
        postgresql_using="product_id::text",
    )
    op.alter_column(
        "stock_adjustments",
        "id",
        type_=VARCHAR36,
        existing_type=UUID_TYPE,
        postgresql_using="id::text",
    )
    op.alter_column(
        "stock_adjustments",
        "product_id",
        type_=VARCHAR36,
        existing_type=UUID_TYPE,
        postgresql_using="product_id::text",
    )
    op.alter_column(
        "stock_adjustments",
        "created_by_user_id",
        type_=VARCHAR36,
        existing_type=UUID_TYPE,
        postgresql_using="created_by_user_id::text",
    )
    op.alter_column(
        "stock_adjustments",
        "approved_by_user_id",
        type_=VARCHAR36,
        existing_type=UUID_TYPE,
        postgresql_using="approved_by_user_id::text",
    )
    op.alter_column(
        "invoices",
        "id",
        type_=VARCHAR36,
        existing_type=UUID_TYPE,
        postgresql_using="id::text",
    )
    op.alter_column(
        "invoices",
        "sold_by_id",
        type_=VARCHAR36,
        existing_type=UUID_TYPE,
        postgresql_using="sold_by_id::text",
    )
    op.alter_column(
        "invoices",
        "finalized_by_id",
        type_=VARCHAR36,
        existing_type=UUID_TYPE,
        postgresql_using="finalized_by_id::text",
    )
    op.alter_column(
        "invoices",
        "dispensed_by_id",
        type_=VARCHAR36,
        existing_type=UUID_TYPE,
        postgresql_using="dispensed_by_id::text",
    )
    op.alter_column(
        "invoice_items",
        "id",
        type_=VARCHAR36,
        existing_type=UUID_TYPE,
        postgresql_using="id::text",
    )
    op.alter_column(
        "invoice_items",
        "invoice_id",
        type_=VARCHAR36,
        existing_type=UUID_TYPE,
        postgresql_using="invoice_id::text",
    )
    op.alter_column(
        "invoice_items",
        "product_id",
        type_=VARCHAR36,
        existing_type=UUID_TYPE,
        postgresql_using="product_id::text",
    )
    op.alter_column(
        "invoice_items",
        "product_unit_id",
        type_=VARCHAR36,
        existing_type=UUID_TYPE,
        postgresql_using="product_unit_id::text",
    )
    op.alter_column(
        "audit_logs",
        "id",
        type_=VARCHAR36,
        existing_type=UUID_TYPE,
        postgresql_using="id::text",
    )
    op.alter_column(
        "audit_logs",
        "user_id",
        type_=VARCHAR36,
        existing_type=UUID_TYPE,
        postgresql_using="user_id::text",
    )


def _create_core_foreign_keys() -> None:
    op.create_foreign_key(
        "fk_product_units_product_id_products",
        "product_units",
        "products",
        ["product_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_stock_adjustments_product_id_products",
        "stock_adjustments",
        "products",
        ["product_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_stock_adjustments_created_by_user_id_users",
        "stock_adjustments",
        "users",
        ["created_by_user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_stock_adjustments_approved_by_user_id_users",
        "stock_adjustments",
        "users",
        ["approved_by_user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_invoices_sold_by_id_users",
        "invoices",
        "users",
        ["sold_by_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_invoices_finalized_by_id_users",
        "invoices",
        "users",
        ["finalized_by_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_invoices_dispensed_by_id_users",
        "invoices",
        "users",
        ["dispensed_by_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_invoice_items_invoice_id_invoices",
        "invoice_items",
        "invoices",
        ["invoice_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_invoice_items_product_id_products",
        "invoice_items",
        "products",
        ["product_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_invoice_items_product_unit_id_product_units",
        "invoice_items",
        "product_units",
        ["product_unit_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_audit_logs_user_id_users",
        "audit_logs",
        "users",
        ["user_id"],
        ["id"],
    )


def _drop_named_uuid_foreign_keys() -> None:
    for name, table_name in [
        ("fk_product_units_product_id_products", "product_units"),
        ("fk_stock_adjustments_product_id_products", "stock_adjustments"),
        ("fk_stock_adjustments_created_by_user_id_users", "stock_adjustments"),
        ("fk_stock_adjustments_approved_by_user_id_users", "stock_adjustments"),
        ("fk_invoices_sold_by_id_users", "invoices"),
        ("fk_invoices_finalized_by_id_users", "invoices"),
        ("fk_invoices_dispensed_by_id_users", "invoices"),
        ("fk_invoice_items_invoice_id_invoices", "invoice_items"),
        ("fk_invoice_items_product_id_products", "invoice_items"),
        ("fk_invoice_items_product_unit_id_product_units", "invoice_items"),
        ("fk_audit_logs_user_id_users", "audit_logs"),
    ]:
        op.drop_constraint(name, table_name, type_="foreignkey")


def upgrade() -> None:
    """Upgrade schema."""
    if not _is_postgresql():
        return

    _drop_uuid_related_foreign_keys()
    _alter_columns_to_uuid()
    _create_core_foreign_keys()


def downgrade() -> None:
    """Downgrade schema."""
    if not _is_postgresql():
        return

    _drop_named_uuid_foreign_keys()
    _alter_columns_to_varchar()
    _create_core_foreign_keys()
