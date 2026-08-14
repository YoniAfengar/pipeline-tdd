from __future__ import annotations

import csv
import os
from collections.abc import Iterator
from pathlib import Path

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


@pytest.fixture(scope="session")
def seed_stations(postgres_url: str) -> None:
    seed_path = Path("given/seed/stations.csv")

    with seed_path.open(newline="") as seed_file:
        reader = csv.DictReader(seed_file)

        with psycopg.connect(postgres_url) as conn:
            with conn.cursor() as cursor:
                for row in reader:
                    cursor.execute(
                        """
                        INSERT INTO stations (station_id, name)
                        VALUES (%s, %s)
                        """,
                        (row["station_id"], row["name"]),
                    )

            conn.commit()


@pytest.fixture
def db_conn(
    postgres_url: str,
    seed_stations: None,
) -> Iterator[psycopg.Connection]:
    conn = psycopg.connect(postgres_url)
    conn.execute("BEGIN")

    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()


@pytest.fixture
def pipeline_db_url(
    postgres_url: str,
    seed_stations: None,
) -> Iterator[str]:
    with psycopg.connect(postgres_url) as conn:
        conn.execute("TRUNCATE TABLE dock_events")
        conn.commit()

    try:
        yield postgres_url
    finally:
        with psycopg.connect(postgres_url) as conn:
            conn.execute("TRUNCATE TABLE dock_events")
            conn.commit()