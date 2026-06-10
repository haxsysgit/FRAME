"""PostgreSQL compatibility hardening

Revision ID: a6f92b1d3e44
Revises: 7e2ab1f4d9c2
Create Date: 2026-04-06 07:25:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a6f92b1d3e44"
down_revision: Union[str, Sequence[str], None] = "7e2ab1f4d9c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_postgresql() -> bool:
    return op.get_context().dialect.name == "postgresql"


def _enum_labels(enum_name: str) -> set[str]:
    bind = op.get_bind()
    rows = bind.execute(
        sa.text(
            """
            SELECT e.enumlabel
            FROM pg_type t
            JOIN pg_enum e ON e.enumtypid = t.oid
            WHERE t.typname = :enum_name
            ORDER BY e.enumsortorder
            """
        ),
        {"enum_name": enum_name},
    )
    return {row[0] for row in rows}


def _column_udt_name(table_name: str, column_name: str) -> str | None:
    bind = op.get_bind()
    row = bind.execute(
        sa.text(
            """
            SELECT udt_name
            FROM information_schema.columns
            WHERE table_schema = current_schema()
              AND table_name = :table_name
              AND column_name = :column_name
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    ).first()
    return row[0] if row else None


def _constraint_exists(constraint_name: str) -> bool:
    bind = op.get_bind()
    row = bind.execute(
        sa.text("SELECT 1 FROM pg_constraint WHERE conname = :constraint_name"),
        {"constraint_name": constraint_name},
    ).first()
    return row is not None


def upgrade() -> None:
    """Upgrade schema."""
    if not _is_postgresql():
        return

    user_role_labels = _enum_labels("user_role")
    if "SALES" in user_role_labels and "STAFF" not in user_role_labels:
        op.execute("ALTER TYPE user_role RENAME VALUE 'SALES' TO 'STAFF'")

    if "DELETED" not in _enum_labels("productstatus"):
        op.execute("ALTER TYPE productstatus ADD VALUE 'DELETED'")

    if "DISPENSED" not in _enum_labels("invoicestatus"):
        op.execute("ALTER TYPE invoicestatus ADD VALUE 'DISPENSED'")

    op.execute(
        """
        DO $$
        BEGIN
          IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'stockadjustmentstatus') THEN
            CREATE TYPE stockadjustmentstatus AS ENUM ('PENDING', 'APPROVED', 'REJECTED');
          END IF;
        END
        $$;
        """
    )

    if _column_udt_name("stock_adjustments", "status") != "stockadjustmentstatus":
        op.execute(
            """
            ALTER TABLE stock_adjustments
            ALTER COLUMN status TYPE stockadjustmentstatus
            USING (
              CASE UPPER(COALESCE(status::text, 'APPROVED'))
                WHEN 'PENDING' THEN 'PENDING'::stockadjustmentstatus
                WHEN 'REJECTED' THEN 'REJECTED'::stockadjustmentstatus
                ELSE 'APPROVED'::stockadjustmentstatus
              END
            )
            """
        )
    op.execute("ALTER TABLE stock_adjustments ALTER COLUMN status SET DEFAULT 'APPROVED'")

    if not _constraint_exists("fk_stock_adjustments_approved_by_user_id_users"):
        op.create_foreign_key(
            "fk_stock_adjustments_approved_by_user_id_users",
            "stock_adjustments",
            "users",
            ["approved_by_user_id"],
            ["id"],
        )

    if _column_udt_name("invoice_items", "unit_price") != "numeric":
        op.execute(
            """
            ALTER TABLE invoice_items
            ALTER COLUMN unit_price TYPE NUMERIC(10,5)
            USING ROUND(unit_price::numeric, 5)
            """
        )
    if _column_udt_name("invoice_items", "line_total") != "numeric":
        op.execute(
            """
            ALTER TABLE invoice_items
            ALTER COLUMN line_total TYPE NUMERIC(10,5)
            USING ROUND(line_total::numeric, 5)
            """
        )
    if _column_udt_name("invoices", "total_amount") != "numeric":
        op.execute(
            """
            ALTER TABLE invoices
            ALTER COLUMN total_amount TYPE NUMERIC(10,5)
            USING ROUND(total_amount::numeric, 5)
            """
        )

    if _column_udt_name("audit_logs", "details") != "jsonb":
        op.execute(
            """
            CREATE OR REPLACE FUNCTION pharmax_safe_parse_jsonb(input_text text)
            RETURNS jsonb
            LANGUAGE plpgsql
            AS $$
            BEGIN
              IF input_text IS NULL OR btrim(input_text) = '' THEN
                RETURN NULL;
              END IF;
              BEGIN
                RETURN input_text::jsonb;
              EXCEPTION WHEN others THEN
                RETURN jsonb_build_object('raw', input_text);
              END;
            END;
            $$;
            """
        )
        op.execute(
            """
            ALTER TABLE audit_logs
            ALTER COLUMN details TYPE jsonb
            USING pharmax_safe_parse_jsonb(details)
            """
        )
        op.execute("DROP FUNCTION IF EXISTS pharmax_safe_parse_jsonb(text)")


def downgrade() -> None:
    """Downgrade schema."""
    if not _is_postgresql():
        return

    if _column_udt_name("audit_logs", "details") == "jsonb":
        op.execute(
            """
            ALTER TABLE audit_logs
            ALTER COLUMN details TYPE text
            USING CASE
              WHEN details IS NULL THEN NULL
              ELSE details::text
            END
            """
        )

    if _column_udt_name("invoice_items", "unit_price") == "numeric":
        op.execute(
            """
            ALTER TABLE invoice_items
            ALTER COLUMN unit_price TYPE double precision
            USING unit_price::double precision
            """
        )
    if _column_udt_name("invoice_items", "line_total") == "numeric":
        op.execute(
            """
            ALTER TABLE invoice_items
            ALTER COLUMN line_total TYPE double precision
            USING line_total::double precision
            """
        )
    if _column_udt_name("invoices", "total_amount") == "numeric":
        op.execute(
            """
            ALTER TABLE invoices
            ALTER COLUMN total_amount TYPE double precision
            USING total_amount::double precision
            """
        )

    if _constraint_exists("fk_stock_adjustments_approved_by_user_id_users"):
        op.drop_constraint("fk_stock_adjustments_approved_by_user_id_users", "stock_adjustments", type_="foreignkey")

    if _column_udt_name("stock_adjustments", "status") == "stockadjustmentstatus":
        op.execute(
            """
            ALTER TABLE stock_adjustments
            ALTER COLUMN status TYPE VARCHAR(20)
            USING status::text
            """
        )
