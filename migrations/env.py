import os
from alembic import context
from sqlalchemy import create_engine, pool
from config import Config


def run_migrations_online():
    # Get DB URL from environment
    db_url = Config.DB_CONNECTION_STRING

    connectable = create_engine(
        db_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=None,   # no ORM
            literal_binds=True,
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
