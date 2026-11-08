from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.events.models import Company, CompanyMember, Event, EventAssignment

User = get_user_model()


def get_user(username):
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password("demo12345")
        user.save()
    return user


class Command(BaseCommand):
    help = "Seeds 3 events: two assignments, one assignment, none."

    @transaction.atomic
    def handle(self, *args, **options):
        company, _ = Company.objects.get_or_create(
            name="JOIN Demo Company",
            defaults={"contact_number": "0000000000", "address": "Demo Street"},
        )

        def member(username, role):
            m, _ = CompanyMember.objects.get_or_create(
                company=company, user=get_user(username), defaults={"role": role}
            )
            return m

        owner = member("demo_owner", "OWNER")
        staff_one = member("demo_staff_one", "STAFF")
        staff_two = member("demo_staff_two", "STAFF")

        def event(title, days, location):
            e, _ = Event.objects.get_or_create(
                company=company,
                title=title,
                defaults={
                    "created_by": owner,
                    "description": "Seeded for the SQL JOIN demo.",
                    "event_date": date.today() + timedelta(days=days),
                    "start_time": time(9, 0),
                    "end_time": time(17, 0),
                    "location": location,
                    "status": "UPCOMING",
                },
            )
            return e

        def assign(ev, mem, role, place, start, end, status):
            EventAssignment.objects.get_or_create(
                event=ev,
                member=mem,
                defaults={
                    "assigned_role": role,
                    "assigned_location": place,
                    "start_time": start,
                    "end_time": end,
                    "status": status,
                },
            )

        ev_a = event("Concert Night", 7, "City Arena")
        ev_b = event("Trade Expo", 14, "Convention Center")
        ev_c = event("Charity Gala", 21, "Grand Hotel")

        assign(ev_a, staff_one, "Usher", "Main Hall", time(9, 0), time(13, 0), "CONFIRMED")
        assign(ev_a, staff_two, "Cashier", "Entrance", time(13, 0), time(17, 0), "ASSIGNED")
        assign(ev_b, staff_one, "Technician", "Stage", time(10, 0), time(16, 0), "ASSIGNED")

        self.stdout.write(self.style.SUCCESS(
            "Seeded: Concert Night (2 assignments), Trade Expo (1), "
            "Charity Gala (0)."
        ))