from __future__ import annotations

import os
from collections.abc import Iterator

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from testcontainers.community.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_url() -> Iterator[str]:
    with PostgresContainer("postgres:16-alpine", driver=None) as postgres:
        url = postgres.get_connection_url()
        os.environ["DATABASE_URL"] = url

        cfg = Config("alembic.ini")
        command.upgrade(cfg, "head")

        yield url


@pytest.fixture
def db_conn(postgres_url: str) -> Iterator[psycopg.Connection]:
    conn = psycopg.connect(postgres_url)
    conn.execute("BEGIN")

    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()