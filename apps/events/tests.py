from django.test import TestCase, Client
from django.urls import reverse
from apps.events.models import Company, CompanyMember, Event, EventAssignment
from django.contrib.auth import get_user_model
from datetime import date, time

User = get_user_model()


class EventsJoinDemoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.company = Company.objects.create(name="Test Company")
        self.member = CompanyMember.objects.create(company=self.company, user=self.user, role="STAFF")
        self.event = Event.objects.create(
            company=self.company,
            created_by=self.member,
            title="Test Event",
            event_date=date.today(),
            start_time=time(9, 0),
            end_time=time(17, 0),
            location="Test Hall",
            status="UPCOMING",
        )
        self.assignment = EventAssignment.objects.create(
            event=self.event,
            member=self.member,
            assigned_role="Staff",
            assigned_location="Entrance",
            start_time=time(9, 0),
            end_time=time(17, 0),
            status="CONFIRMED",
        )

    def test_join_demo_view_renders_successfully(self):
        response = self.client.get(reverse('events:join_demo'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events/join_demo.html')
        self.assertContains(response, 'SQL JOIN Demonstration')
        self.assertContains(response, 'INNER JOIN')
        self.assertContains(response, 'LEFT JOIN')
