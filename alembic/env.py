"""Alembic migration environment. Given — do not edit.

The URL comes from `DATABASE_URL`, never from `alembic.ini`. In production that is a real database; in
your suite it will be a container that did not exist when the test started. Neither this file nor the
revisions know the difference, which is the entire point of Task 3.

`target_metadata` is `None`: there is no ORM here, the DDL is hand-written SQL, and there is nothing
for `--autogenerate` to diff.
"""
from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

# libpq wants `postgresql://`; SQLAlchemy wants a named driver or it reaches for psycopg2, which is
# not installed. One DSN in the environment, one translation, here.
url = os.environ["DATABASE_URL"]
config.set_main_option("sqlalchemy.url", url.replace("postgresql://", "postgresql+psycopg://", 1))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def run_migrations_offline() -> None:
    context.configure(url=config.get_main_option("sqlalchemy.url"),
                      target_metadata=target_metadata, literal_binds=True,
                      dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
