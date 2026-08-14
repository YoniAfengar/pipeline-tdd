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