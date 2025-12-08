"""empty message

Revision ID: 38e0be10498d
Revises: 669f53395b24
Create Date: 2025-12-08 22:53:55.541378

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38e0be10498d'
down_revision: Union[str, Sequence[str], None] = '669f53395b24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""ALTER TABLE flags ENABLE ROW LEVEL SECURITY""")
    op.execute("""ALTER TABLE principals ENABLE ROW LEVEL SECURITY""")
    op.execute("""ALTER TABLE jobs ENABLE ROW LEVEL SECURITY""")
    op.execute("""ALTER TABLE flag_aggregates ENABLE ROW LEVEL SECURITY""")
    op.execute("""ALTER TABLE exposures ENABLE ROW LEVEL SECURITY""")
    op.execute("""ALTER TABLE events ENABLE ROW LEVEL SECURITY""")
    op.execute("""ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY""")
    op.execute("""ALTER TABLE assignments ENABLE ROW LEVEL SECURITY""")

    op.execute("""
                CREATE POLICY flags_tenant_policy ON flags
                USING (tenant_id = current_setting('app.tenant_id')::uuid);
                """)


def downgrade() -> None:
    # 1. Drop the policy
    op.execute("""DROP POLICY flags_tenant_policy ON flags""")

    # 2. Disable RLS on all tables (in reverse order of creation is standard practice)
    op.execute("""ALTER TABLE assignments DISABLE ROW LEVEL SECURITY""")
    op.execute("""ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY""")
    op.execute("""ALTER TABLE events DISABLE ROW LEVEL SECURITY""")
    op.execute("""ALTER TABLE exposures DISABLE ROW LEVEL SECURITY""")
    op.execute("""ALTER TABLE flag_aggregates DISABLE ROW LEVEL SECURITY""")
    op.execute("""ALTER TABLE jobs DISABLE ROW LEVEL SECURITY""")
    op.execute("""ALTER TABLE principals DISABLE ROW LEVEL SECURITY""")
    op.execute("""ALTER TABLE flags DISABLE ROW LEVEL SECURITY""")