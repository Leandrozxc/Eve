from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.events.models import Company, CompanyMember, Event, EventAssignment
from apps.userprofile.models import Profile
from apps.usersettings.models import UserSettings

User = get_user_model()


def get_or_create_demo_user(username, email, full_name):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "first_name": full_name.split()[0],
            "last_name": full_name.split()[1] if len(full_name.split()) > 1 else "",
        },
    )
    if created or not user.check_password("demo12345"):
        user.email = email
        user.first_name = full_name.split()[0]
        user.last_name = full_name.split()[1] if len(full_name.split()) > 1 else ""
        user.set_password("demo12345")
        user.save()

    Profile.objects.get_or_create(user=user, defaults={"full_name": full_name, "bio": "Demo account for testing Eve."})
    UserSettings.objects.get_or_create(user=user)
    return user


class Command(BaseCommand):
    help = "Seeds demo company, roles, events, and assignments for SQL JOIN and workflow evaluation."

    @transaction.atomic
    def handle(self, *args, **options):
        company, _ = Company.objects.get_or_create(
            name="JOIN Demo Company",
            defaults={"contact_number": "+63 900 123 4567", "address": "100 Ayala Avenue, Makati City"},
        )

        owner_user = get_or_create_demo_user("demo_owner", "owner@demo.com", "Alice Owner")
        manager_user = get_or_create_demo_user("demo_manager", "manager@demo.com", "Bob Manager")
        staff_one_user = get_or_create_demo_user("demo_staff_one", "staff1@demo.com", "Charlie Staff")
        staff_two_user = get_or_create_demo_user("demo_staff_two", "staff2@demo.com", "Diana Staff")

        def member(user, role):
            m, _ = CompanyMember.objects.get_or_create(
                company=company, user=user, defaults={"role": role}
            )
            if m.role != role:
                m.role = role
                m.save()
            return m

        owner = member(owner_user, "OWNER")
        manager = member(manager_user, "MANAGER")
        staff_one = member(staff_one_user, "STAFF")
        staff_two = member(staff_two_user, "STAFF")

        def event(title, days, location, status="UPCOMING"):
            e, _ = Event.objects.get_or_create(
                company=company,
                title=title,
                defaults={
                    "created_by": owner,
                    "description": "Seeded for the SQL JOIN and workflow demonstration.",
                    "event_date": date.today() + timedelta(days=days),
                    "start_time": time(9, 0),
                    "end_time": time(17, 0),
                    "location": location,
                    "status": status,
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

        ev_a = event("Concert Night", 7, "City Arena", "UPCOMING")
        ev_b = event("Trade Expo", 14, "Convention Center", "UPCOMING")
        ev_c = event("Charity Gala", 21, "Grand Hotel", "DRAFT")

        assign(ev_a, staff_one, "Usher", "Main Hall", time(9, 0), time(13, 0), "CONFIRMED")
        assign(ev_a, staff_two, "Cashier", "Entrance", time(13, 0), time(17, 0), "ASSIGNED")
        assign(ev_b, staff_one, "Technician", "Stage", time(10, 0), time(16, 0), "ASSIGNED")
        assign(ev_b, manager, "Floor Manager", "Pavilion", time(9, 0), time(17, 0), "CONFIRMED")

        self.stdout.write(self.style.SUCCESS(
            "Successfully seeded demo data!\n"
            "- Company: JOIN Demo Company\n"
            "- Accounts (Password: demo12345):\n"
            "   * Owner:   owner@demo.com (demo_owner)\n"
            "   * Manager: manager@demo.com (demo_manager)\n"
            "   * Staff 1: staff1@demo.com (demo_staff_one)\n"
            "   * Staff 2: staff2@demo.com (demo_staff_two)\n"
            "- Events: Concert Night (2 assignments), Trade Expo (2 assignments), Charity Gala (0 assignments)"
        ))
