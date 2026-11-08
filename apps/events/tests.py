from datetime import date, time
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.events.models import Company, CompanyMember, Event, EventAssignment

User = get_user_model()


class CompanyWorkflowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="owner@example.com", password="password123")
        self.staff_user = User.objects.create_user(username="staff@example.com", password="password123")
        self.client.login(username="owner@example.com", password="password123")

    def test_company_list_renders(self):
        response = self.client.get(reverse("events:company_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events/company_list.html")

    def test_create_company_sets_owner_role(self):
        response = self.client.post(reverse("events:company_create"), {
            "name": "Apex Events",
            "contact_number": "123456",
            "address": "Makati",
        })
        self.assertRedirects(response, reverse("events:company_list"))
        company = Company.objects.get(name="Apex Events")
        membership = CompanyMember.objects.get(company=company, user=self.user)
        self.assertEqual(membership.role, "OWNER")

    def test_join_company_sets_staff_role(self):
        company = Company.objects.create(name="Public Org")
        self.client.login(username="staff@example.com", password="password123")
        response = self.client.get(reverse("events:company_join", kwargs={"company_id": company.id}))
        self.assertRedirects(response, reverse("events:company_list"))
        membership = CompanyMember.objects.get(company=company, user=self.staff_user)
        self.assertEqual(membership.role, "STAFF")

    def test_company_members_management_role_change(self):
        company = Company.objects.create(name="Delta Corp")
        owner_mem = CompanyMember.objects.create(company=company, user=self.user, role="OWNER")
        staff_mem = CompanyMember.objects.create(company=company, user=self.staff_user, role="STAFF")

        # Promote staff to manager
        response = self.client.post(
            reverse("events:company_members", kwargs={"company_id": company.id}),
            {
                "action": "change_role",
                "member_id": staff_mem.id,
                "new_role": "MANAGER",
            },
        )
        self.assertRedirects(response, reverse("events:company_members", kwargs={"company_id": company.id}))
        staff_mem.refresh_from_db()
        self.assertEqual(staff_mem.role, "MANAGER")


class EventWorkflowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="manager@example.com", password="password123")
        self.staff_user = User.objects.create_user(username="worker@example.com", password="password123")
        self.company = Company.objects.create(name="Event Pros")
        self.manager_mem = CompanyMember.objects.create(company=self.company, user=self.user, role="MANAGER")
        self.staff_mem = CompanyMember.objects.create(company=self.company, user=self.staff_user, role="STAFF")
        self.client.login(username="manager@example.com", password="password123")

    def test_event_list_renders(self):
        response = self.client.get(reverse("events:event_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events/event_list.html")

    def test_event_create_under_company(self):
        response = self.client.post(reverse("events:event_create"), {
            "company_id": self.company.id,
            "title": "Grand Gala 2026",
            "description": "Annual gala",
            "event_date": "2026-12-15",
            "start_time": "18:00",
            "end_time": "23:00",
            "location": "Grand Ballroom",
            "status": "UPCOMING",
        })
        event = Event.objects.get(title="Grand Gala 2026")
        self.assertRedirects(response, reverse("events:event_detail", kwargs={"event_id": event.id}))
        self.assertEqual(event.company, self.company)
        self.assertEqual(event.created_by, self.manager_mem)

    def test_assignment_create_and_track_progress(self):
        event = Event.objects.create(
            company=self.company,
            created_by=self.manager_mem,
            title="Music Fest",
            event_date=date.today(),
            start_time=time(10, 0),
            end_time=time(20, 0),
            location="Festival Grounds",
            status="UPCOMING",
        )
        # Assign staff member
        response = self.client.post(
            reverse("events:assignment_create", kwargs={"event_id": event.id}),
            {
                "member_id": self.staff_mem.id,
                "assigned_role": "Lead Usher",
                "assigned_location": "Gate A",
                "start_time": "10:00",
                "end_time": "16:00",
                "status": "ASSIGNED",
            },
        )
        self.assertRedirects(response, reverse("events:event_detail", kwargs={"event_id": event.id}))
        assignment = EventAssignment.objects.get(event=event, member=self.staff_mem)
        self.assertEqual(assignment.assigned_role, "Lead Usher")
        self.assertEqual(assignment.status, "ASSIGNED")

        # Staff logs in and confirms shift
        self.client.login(username="worker@example.com", password="password123")
        update_response = self.client.post(
            reverse("events:assignment_update", kwargs={"assignment_id": assignment.id}),
            {"status": "CONFIRMED"},
        )
        self.assertRedirects(update_response, reverse("events:event_detail", kwargs={"event_id": event.id}))
        assignment.refresh_from_db()
        self.assertEqual(assignment.status, "CONFIRMED")


class EventsJoinDemoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="demouser", password="password123")
        self.company = Company.objects.create(name="Demo Company")
        self.member = CompanyMember.objects.create(company=self.company, user=self.user, role="STAFF")
        self.event = Event.objects.create(
            company=self.company,
            created_by=self.member,
            title="Demo Concert",
            event_date=date.today(),
            start_time=time(9, 0),
            end_time=time(17, 0),
            location="Arena",
            status="UPCOMING",
        )
        self.assignment = EventAssignment.objects.create(
            event=self.event,
            member=self.member,
            assigned_role="Usher",
            assigned_location="Door 1",
            start_time=time(9, 0),
            end_time=time(17, 0),
            status="CONFIRMED",
        )

    def test_join_demo_view_renders_successfully(self):
        response = self.client.get(reverse("events:join_demo"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events/join_demo.html")
        self.assertContains(response, "SQL JOIN Demonstration")
        self.assertContains(response, "INNER JOIN")
        self.assertContains(response, "LEFT JOIN")
