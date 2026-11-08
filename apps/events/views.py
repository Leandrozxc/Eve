from django.db import connection
from django.shortcuts import render

INNER_SQL = """
SELECT e.id AS event_id,
       a.id AS assignment_id,
       a.assigned_role,
       a.assigned_location,
       a.status
FROM events_event AS e
INNER JOIN events_eventassignment AS a
        ON e.id = a.event_id
ORDER BY e.id, a.id
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
ORDER BY e.id, a.id
"""


def _run(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        return cursor.fetchall()


def join_demo(request):
    context = {
        "inner_sql": INNER_SQL.strip(),
        "inner_rows": _run(INNER_SQL),
        "left_sql": LEFT_SQL.strip(),
        "left_rows": _run(LEFT_SQL),
    }
    return render(request, "events/join_demo.html", context)