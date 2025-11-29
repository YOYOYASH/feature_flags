"""empty message

Revision ID: e7b857ef51f8
Revises: 
Create Date: 2025-11-29 18:54:17.053106

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7b857ef51f8'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 0. Extensions
    op.execute("""CREATE EXTENSION IF NOT EXISTS "pgcrypto";""")
    op.execute("""CREATE EXTENSION IF NOT EXISTS "pg_trgm";""")

    # 1. tenants
    op.execute("""
    CREATE TABLE tenants (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name TEXT NOT NULL,
        plan TEXT DEFAULT 'free',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        api_key_hash TEXT,
        secrets JSONB DEFAULT '{}'
    );
    """)

    op.execute("""CREATE UNIQUE INDEX idx_tenants_name ON tenants(name);""")

    # 1b. service accounts
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

    op.execute("""CREATE INDEX idx_sa_tenant ON service_accounts(tenant_id);""")

    # 2. flags
    op.execute("""
    CREATE TABLE flags (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
        key TEXT NOT NULL,
        description TEXT,
        enabled BOOLEAN NOT NULL DEFAULT FALSE,
        rollout_percent INT NOT NULL DEFAULT 0,
        variant_weights JSONB DEFAULT '{}',
        rules JSONB DEFAULT '{}',
        created_by UUID,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """)

    op.execute("""CREATE UNIQUE INDEX idx_flags_tenant_key ON flags(tenant_id, key);""")
    op.execute("""CREATE INDEX idx_flags_tenant_enabled ON flags(tenant_id, enabled);""")

    # 3. assignments (sticky)
    op.execute("""
    CREATE TABLE assignments (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
        flag_id UUID NOT NULL REFERENCES flags(id) ON DELETE CASCADE,
        user_id TEXT NOT NULL,
        variant TEXT NOT NULL,
        reason TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        UNIQUE (tenant_id, flag_id, user_id)
    );
    """)

    op.execute("""CREATE INDEX idx_assignments_flag_user
                  ON assignments(tenant_id, flag_id, user_id);""")

    # 4. exposures (write-heavy)
    op.execute("""
    CREATE TABLE exposures (
        id BIGSERIAL PRIMARY KEY,
        tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
        flag_key TEXT NOT NULL,
        user_id TEXT,
        variant TEXT,
        context JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """)

    op.execute("""CREATE INDEX idx_exposures_tenant_flag
                  ON exposures(tenant_id, flag_key, created_at);""")

    op.execute("""CREATE INDEX idx_exposures_tenant_user
                  ON exposures(tenant_id, user_id);""")

    # 5. events (conversions)
    op.execute("""
    CREATE TABLE events (
        id BIGSERIAL PRIMARY KEY,
        tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
        user_id TEXT,
        event_type TEXT NOT NULL,
        payload JSONB,
        flagged_variant JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """)

    op.execute("""CREATE INDEX idx_events_tenant_type
                  ON events(tenant_id, event_type, created_at);""")

    op.execute("""CREATE INDEX idx_events_tenant_user
                  ON events(tenant_id, user_id);""")

    # 6. flag_aggregates
    op.execute("""
    CREATE TABLE flag_aggregates (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
        flag_key TEXT NOT NULL,
        period DATE NOT NULL,
        variant TEXT NOT NULL,
        exposures BIGINT DEFAULT 0,
        conversions BIGINT DEFAULT 0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        UNIQUE (tenant_id, flag_key, period, variant)
    );
    """)

    op.execute("""CREATE INDEX idx_agg_tenant_flag_period
                  ON flag_aggregates(tenant_id, flag_key, period);""")

    # 7. jobs
    op.execute("""
    CREATE TABLE jobs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        tenant_id UUID,
        name TEXT NOT NULL,
        payload JSONB,
        status TEXT NOT NULL DEFAULT 'pending',
        attempts INT DEFAULT 0,
        last_error TEXT,
        scheduled_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """)

    op.execute("""CREATE INDEX idx_jobs_status ON jobs(status);""")
    op.execute("""CREATE INDEX idx_jobs_tenant_scheduled
                  ON jobs(tenant_id, scheduled_at);""")

    # 8. audit logs
    op.execute("""
    CREATE TABLE audit_logs (
        id BIGSERIAL PRIMARY KEY,
        tenant_id UUID,
        actor TEXT,
        action TEXT,
        details JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """)

    op.execute("""CREATE INDEX idx_audit_tenant
                  ON audit_logs(tenant_id, created_at);""")


def downgrade():
    op.execute("DROP TABLE audit_logs;")
    op.execute("DROP INDEX IF EXISTS idx_audit_tenant;")

    op.execute("DROP INDEX IF EXISTS idx_jobs_tenant_scheduled;")
    op.execute("DROP INDEX IF EXISTS idx_jobs_status;")
    op.execute("DROP TABLE jobs;")

    op.execute("DROP INDEX IF EXISTS idx_agg_tenant_flag_period;")
    op.execute("DROP TABLE flag_aggregates;")

    op.execute("DROP INDEX IF EXISTS idx_events_tenant_user;")
    op.execute("DROP INDEX IF EXISTS idx_events_tenant_type;")
    op.execute("DROP TABLE events;")

    op.execute("DROP INDEX IF EXISTS idx_exposures_tenant_user;")
    op.execute("DROP INDEX IF EXISTS idx_exposures_tenant_flag;")
    op.execute("DROP TABLE exposures;")

    op.execute("DROP INDEX IF EXISTS idx_assignments_flag_user;")
    op.execute("DROP TABLE assignments;")

    op.execute("DROP INDEX IF EXISTS idx_flags_tenant_enabled;")
    op.execute("DROP INDEX IF EXISTS idx_flags_tenant_key;")
    op.execute("DROP TABLE flags;")

    op.execute("DROP INDEX IF EXISTS idx_sa_tenant;")
    op.execute("DROP TABLE service_accounts;")

    op.execute("DROP INDEX IF EXISTS idx_tenants_name;")
    op.execute("DROP TABLE tenants;")

    op.execute("DROP EXTENSION IF EXISTS pg_trgm;")
    op.execute("DROP EXTENSION IF EXISTS pgcrypto;")