"""empty message

Revision ID: 669f53395b24
Revises: e7b857ef51f8
Create Date: 2025-11-29 19:59:05.636507

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '669f53395b24'
down_revision: Union[str, Sequence[str], None] = 'e7b857ef51f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    # --------------------------------------------------------
    # 1. Drop service_accounts table (replaced by principals)
    # --------------------------------------------------------
    op.execute("DROP INDEX IF EXISTS idx_sa_tenant;")
    op.execute("DROP TABLE IF EXISTS service_accounts;")

    # --------------------------------------------------------
    # 2. Create unified principals table (users + services + root)
    # --------------------------------------------------------
    op.execute("""
    CREATE TABLE principals (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
        type TEXT NOT NULL,                -- 'user', 'service', 'root'
        
        email TEXT,                        -- human users only
        name TEXT NOT NULL,                -- display/service name
        
        password_hash TEXT,                -- for humans
        api_key_hash TEXT,                 -- for service accounts & root
        
        role TEXT NOT NULL,                -- 'admin','reader','ingestor','viewer'
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """)

    op.execute("""CREATE INDEX idx_principals_tenant ON principals(tenant_id);""")

    # Unique constraint only when email is NOT NULL
    op.execute("""
    CREATE UNIQUE INDEX idx_principals_email
        ON principals(email)
        WHERE email IS NOT NULL;
    """)

    # --------------------------------------------------------
    # 3. Update flags.created_by to reference principals
    # --------------------------------------------------------
    # old column was: created_by UUID (no FK)
    op.execute("""
    ALTER TABLE flags
        ADD CONSTRAINT fk_flags_created_by_principals
        FOREIGN KEY (created_by) REFERENCES principals(id);
    """)

    # --------------------------------------------------------
    # 4. Update audit_logs.actor to be principal ID
    # --------------------------------------------------------
    # Step 1: Drop old "actor" TEXT column
    op.execute("""
    ALTER TABLE audit_logs
        DROP COLUMN actor;
    """)

    # Step 2: Add new UUID-based actor referencing principals
    op.execute("""
    ALTER TABLE audit_logs
        ADD COLUMN actor UUID REFERENCES principals(id);
    """)

    # NOTE: existing rows will have NULL actor, which is acceptable


def downgrade():

    # --------------------------------------------------------
    # undo audit_logs.actor change
    # --------------------------------------------------------
    op.execute("""
    ALTER TABLE audit_logs
        DROP COLUMN actor;
    """)
    op.execute("""
    ALTER TABLE audit_logs
        ADD COLUMN actor TEXT;
    """)

    # --------------------------------------------------------
    # remove FK from flags
    # --------------------------------------------------------
    op.execute("""
    ALTER TABLE flags
        DROP CONSTRAINT IF EXISTS fk_flags_created_by_principals;
    """)

    # --------------------------------------------------------
    # drop principals table
    # --------------------------------------------------------
    op.execute("DROP INDEX IF EXISTS idx_principals_email;")
    op.execute("DROP INDEX IF EXISTS idx_principals_tenant;")
    op.execute("DROP TABLE IF EXISTS principals;")

    # --------------------------------------------------------
    # recreate service_accounts table (previous version)
    # --------------------------------------------------------
    op.execute("""
    CREATE TABLE service_accounts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        api_key_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'ingest',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """)
    op.execute("CREATE INDEX idx_sa_tenant ON service_accounts(tenant_id);")