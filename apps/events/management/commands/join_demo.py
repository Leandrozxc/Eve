from django.core.management.base import BaseCommand
from django.db import connection


INNER_SQL = """
SELECT e.id AS event_id,
       a.id AS assignment_id,
       a.assigned_role,
       a.assigned_location,
       a.status
FROM events_event AS e
INNER JOIN events_eventassignment AS a
        ON e.id = a.event_id
ORDER BY e.id, a.id;
"""

LEFT_SQL = """
SELECT e.id AS event_id,
       a.id AS assignment_id,
       a.assigned_role,
       a.assigned_location,
       a.status
FROM events_event AS e
LEFT JOIN events_eventassignment AS a
       ON e.id = a.event_id
ORDER BY e.id, a.id;
"""


def run_query(title, sql, explanation):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)
    print("SQL USED:")
    print(sql.strip())

    with connection.cursor() as cursor:
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    print("\nRESULT:")
    print(" | ".join(columns))
    print("-" * 70)
    for row in rows:
        print(" | ".join("NULL" if v is None else str(v) for v in row))
    print(f"\nTotal rows: {len(rows)}")
    print("EXPLANATION:", explanation)


class Command(BaseCommand):
    help = "Demonstrates INNER JOIN and LEFT JOIN on Eve event tables."

    def handle(self, *args, **options):
        run_query(
            "JOIN 1: INNER JOIN (events WITH assignments)",
            INNER_SQL,
            "Only events with a matching assignment appear. "
            "Events with no assignment are excluded.",
        )
        run_query(
            "JOIN 2: LEFT JOIN (ALL events, assigned or not)",
            LEFT_SQL,
            "Every event appears. Events with no assignment show NULL "
            "for the assignment columns.",
        )