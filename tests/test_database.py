import psycopg


def test_migrations_build_schema(postgres_url: str) -> None:
    with psycopg.connect(postgres_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            tables = {row[0] for row in cursor.fetchall()}

            cursor.execute("""
                SELECT indexname
                FROM pg_indexes
                WHERE schemaname = 'public'
            """)
            indexes = {row[0] for row in cursor.fetchall()}

    assert "stations" in tables
    assert "dock_events" in tables
    assert "dock_events_station_time_idx" in indexes


def test_transaction_isolation_first(db_conn: psycopg.Connection) -> None:
    db_conn.execute(
        "INSERT INTO stations (station_id, name) VALUES (%s, %s)",
        ("ST-TEST", "Test Station"),
    )
    db_conn.execute(
        """
        INSERT INTO dock_events (
            event_id,
            station_id,
            occurred_at,
            bikes_available,
            docks_free
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        ("E-SAME", "ST-TEST", "2026-06-01T06:00:00+00:00", 5, 10),
    )


def test_transaction_isolation_second(db_conn: psycopg.Connection) -> None:
    db_conn.execute(
        "INSERT INTO stations (station_id, name) VALUES (%s, %s)",
        ("ST-TEST", "Test Station"),
    )
    db_conn.execute(
        """
        INSERT INTO dock_events (
            event_id,
            station_id,
            occurred_at,
            bikes_available,
            docks_free
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        ("E-SAME", "ST-TEST", "2026-06-01T06:00:00+00:00", 5, 10),
    )


def test_known_station_is_seeded(db_conn: psycopg.Connection) -> None:
    row = db_conn.execute(
        "SELECT name FROM stations WHERE station_id = %s",
        ("ST-0007",),
    ).fetchone()

    assert row == ("Meridian Wharf",)