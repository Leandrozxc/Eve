from datetime import date, time
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.events.models import Company, CompanyMember, Event, EventAssignment, AttendanceRecord, MemberAvailability, EventTask

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


class EventEditDeleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner_user = User.objects.create_user(username="owneruser", password="password123")
        self.staff_user = User.objects.create_user(username="staffuser", password="password123")
        self.company = Company.objects.create(name="Demo Company")
        self.owner_member = CompanyMember.objects.create(company=self.company, user=self.owner_user, role="OWNER")
        self.staff_member = CompanyMember.objects.create(company=self.company, user=self.staff_user, role="STAFF")
        self.event = Event.objects.create(
            company=self.company,
            created_by=self.owner_member,
            title="Initial Title",
            event_date=date.today(),
            start_time=time(9, 0),
            end_time=time(17, 0),
            location="Arena",
            status="UPCOMING",
        )

    def test_owner_can_edit_event(self):
        self.client.login(username="owneruser", password="password123")
        response = self.client.post(
            reverse("events:event_edit", kwargs={"event_id": self.event.id}),
            {
                "title": "Updated Title",
                "description": "Updated Description",
                "event_date": str(date.today()),
                "start_time": "10:00",
                "end_time": "18:00",
                "location": "New Arena",
                "status": "COMPLETED",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, "Updated Title")
        self.assertEqual(self.event.status, "COMPLETED")

    def test_staff_cannot_delete_event(self):
        self.client.login(username="staffuser", password="password123")
        response = self.client.post(reverse("events:event_delete", kwargs={"event_id": self.event.id}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Event.objects.filter(id=self.event.id).exists())

    def test_owner_can_delete_event(self):
        self.client.login(username="owneruser", password="password123")
        response = self.client.post(reverse("events:event_delete", kwargs={"event_id": self.event.id}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Event.objects.filter(id=self.event.id).exists())


class AttendanceWorkflowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username="owner_att", password="password123")
        self.staff = User.objects.create_user(username="staff_att", password="password123")

        self.company = Company.objects.create(name="Attendance Test Org")
        self.owner_member = CompanyMember.objects.create(
            company=self.company, user=self.owner, role="OWNER"
        )
        self.staff_member = CompanyMember.objects.create(
            company=self.company, user=self.staff, role="STAFF"
        )

        self.event = Event.objects.create(
            company=self.company,
            created_by=self.owner_member,
            title="Concert Shift",
            event_date=date.today(),
            start_time=time(9, 0),
            end_time=time(17, 0),
            location="Stage A",
            status="UPCOMING",
        )
        self.assignment = EventAssignment.objects.create(
            event=self.event,
            member=self.staff_member,
            assigned_role="Sound Engineer",
            start_time=time(9, 0),
            end_time=time(17, 0),
            status="ASSIGNED",
        )

    def test_attendance_dashboard_renders(self):
        self.client.login(username="owner_att", password="password123")
        response = self.client.get(reverse("events:attendance_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events/attendance_dashboard.html")

    def test_clock_in_creates_record(self):
        self.client.login(username="staff_att", password="password123")
        response = self.client.post(
            reverse("events:clock_in", kwargs={"assignment_id": self.assignment.id}),
            {"notes": "Station sound check complete"},
        )
        self.assertRedirects(response, reverse("events:attendance_dashboard"))
        self.assertTrue(AttendanceRecord.objects.filter(assignment=self.assignment).exists())
        record = AttendanceRecord.objects.get(assignment=self.assignment)
        self.assertEqual(record.status, "CLOCKED_IN")
        self.assertEqual(record.clock_in_notes, "Station sound check complete")
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.status, "CONFIRMED")

    def test_clock_out_completes_shift(self):
        self.client.login(username="staff_att", password="password123")
        self.client.post(reverse("events:clock_in", kwargs={"assignment_id": self.assignment.id}))
        response = self.client.post(
            reverse("events:clock_out", kwargs={"assignment_id": self.assignment.id}),
            {"notes": "Shift ended smoothly"},
        )
        self.assertRedirects(response, reverse("events:attendance_dashboard"))
        record = AttendanceRecord.objects.get(assignment=self.assignment)
        self.assertEqual(record.status, "CLOCKED_OUT")
        self.assertIsNotNone(record.clock_out_time)
        self.assertEqual(record.clock_out_notes, "Shift ended smoothly")
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.status, "COMPLETED")

    def test_manager_can_verify_attendance(self):
        # Staff clocks in and out
        self.client.login(username="staff_att", password="password123")
        self.client.post(reverse("events:clock_in", kwargs={"assignment_id": self.assignment.id}))
        self.client.post(reverse("events:clock_out", kwargs={"assignment_id": self.assignment.id}))
        record = AttendanceRecord.objects.get(assignment=self.assignment)

        # Owner verifies
        self.client.login(username="owner_att", password="password123")
        response = self.client.post(reverse("events:verify_attendance", kwargs={"record_id": record.id}))
        self.assertRedirects(response, reverse("events:attendance_dashboard"))
        record.refresh_from_db()
        self.assertEqual(record.status, "VERIFIED")
        self.assertEqual(record.verified_by, self.owner_member)
        self.assertIsNotNone(record.verified_at)


class AvailabilityWorkflowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="avail_user", password="password123")
        self.company = Company.objects.create(name="Availability Org")
        self.member = CompanyMember.objects.create(
            company=self.company, user=self.user, role="STAFF"
        )
        self.client.login(username="avail_user", password="password123")

    def test_availability_list_renders(self):
        response = self.client.get(reverse("events:availability_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events/availability_list.html")

    def test_create_weekly_availability(self):
        response = self.client.post(reverse("events:availability_create"), {
            "company_id": self.company.id,
            "availability_type": "AVAILABLE",
            "timing_type": "weekly",
            "day_of_week": "2",  # Wednesday
            "start_time": "09:00",
            "end_time": "17:00",
            "reason": "Available Wednesdays",
        })
        self.assertRedirects(response, reverse("events:availability_list"))
        self.assertTrue(MemberAvailability.objects.filter(member=self.member).exists())
        record = MemberAvailability.objects.get(member=self.member)
        self.assertEqual(record.day_of_week, 2)
        self.assertEqual(record.availability_type, "AVAILABLE")

    def test_delete_availability(self):
        record = MemberAvailability.objects.create(
            member=self.member,
            availability_type="UNAVAILABLE",
            day_of_week=5,
            reason="Weekend offline",
        )
        response = self.client.post(reverse("events:availability_delete", kwargs={"record_id": record.id}))
        self.assertRedirects(response, reverse("events:availability_list"))
        self.assertFalse(MemberAvailability.objects.filter(id=record.id).exists())


class TaskAndAnalyticsWorkflowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="analytics_user", password="password123")
        self.company = Company.objects.create(name="Analytics Corp")
        self.member = CompanyMember.objects.create(
            company=self.company, user=self.user, role="OWNER"
        )
        self.event = Event.objects.create(
            company=self.company,
            created_by=self.member,
            title="Tech Summit",
            event_date=date.today(),
            start_time=time(10, 0),
            end_time=time(18, 0),
            location="Auditorium",
            status="UPCOMING",
        )
        self.client.login(username="analytics_user", password="password123")

    def test_analytics_report_renders(self):
        response = self.client.get(reverse("events:analytics_report"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events/analytics_report.html")
        self.assertEqual(response.context["total_events"], 1)

    def test_create_event_task(self):
        response = self.client.post(
            reverse("events:task_create", kwargs={"event_id": self.event.id}),
            {
                "title": "Stage audio calibration",
                "priority": "HIGH",
            },
        )
        self.assertRedirects(response, reverse("events:event_detail", kwargs={"event_id": self.event.id}))
        self.assertTrue(EventTask.objects.filter(event=self.event, title="Stage audio calibration").exists())

    def test_toggle_and_delete_task(self):
        task = EventTask.objects.create(
            event=self.event,
            title="Credential check",
            priority="MEDIUM",
        )
        # Toggle completion
        response = self.client.post(reverse("events:task_toggle", kwargs={"task_id": task.id}))
        self.assertRedirects(response, reverse("events:event_detail", kwargs={"event_id": self.event.id}))
        task.refresh_from_db()
        self.assertTrue(task.is_completed)
        self.assertIsNotNone(task.completed_at)

        # Delete task
        response = self.client.post(reverse("events:task_delete", kwargs={"task_id": task.id}))
        self.assertRedirects(response, reverse("events:event_detail", kwargs={"event_id": self.event.id}))
        self.assertFalse(EventTask.objects.filter(id=task.id).exists())


class TimeWindowValidationTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="tw_owner", password="pw")
        self.staff = User.objects.create_user(username="tw_staff", password="pw")
        self.company = Company.objects.create(name="TimeCo")
        self.owner_m = CompanyMember.objects.create(company=self.company, user=self.owner, role="OWNER")
        self.staff_m = CompanyMember.objects.create(company=self.company, user=self.staff, role="STAFF")
        self.event = Event.objects.create(
            company=self.company,
            created_by=self.owner_m,
            title="Valid Event",
            event_date=date(2026, 11, 25),
            start_time=time(9, 0),
            end_time=time(17, 0),
            location="Main Hall",
            status="UPCOMING",
        )
        self.client.login(username="tw_owner", password="pw")

    def test_event_create_rejects_end_before_start(self):
        response = self.client.post(
            reverse("events:event_create"),
            {
                "company_id": self.company.id,
                "title": "Bad Window Event",
                "event_date": "2026-11-26",
                "start_time": "17:00",
                "end_time": "09:00",
                "location": "Room A",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Event.objects.filter(title="Bad Window Event").exists())

    def test_event_edit_rejects_equal_start_and_end(self):
        self.client.post(
            reverse("events:event_edit", kwargs={"event_id": self.event.id}),
            {
                "title": "Valid Event",
                "event_date": "2026-11-25",
                "start_time": "10:00",
                "end_time": "10:00",
                "location": "Main Hall",
            },
        )
        self.event.refresh_from_db()
        self.assertEqual(self.event.start_time, time(9, 0))
        self.assertEqual(self.event.end_time, time(17, 0))

    def test_assignment_create_and_update_reject_invalid_window(self):
        self.client.post(
            reverse("events:assignment_create", kwargs={"event_id": self.event.id}),
            {
                "member_id": self.staff_m.id,
                "assigned_role": "Usher",
                "start_time": "15:00",
                "end_time": "12:00",
            },
        )
        self.assertFalse(EventAssignment.objects.filter(event=self.event, member=self.staff_m).exists())

        assignment = EventAssignment.objects.create(
            event=self.event,
            member=self.staff_m,
            assigned_role="Usher",
            start_time=time(9, 0),
            end_time=time(13, 0),
        )
        self.client.post(
            reverse("events:assignment_update", kwargs={"assignment_id": assignment.id}),
            {
                "start_time": "14:00",
                "end_time": "11:00",
                "status": "ASSIGNED",
            },
        )
        assignment.refresh_from_db()
        self.assertEqual(assignment.start_time, time(9, 0))
        self.assertEqual(assignment.end_time, time(13, 0))


class ScheduleConflictAndAvailabilityTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="sc_owner", password="pw")
        self.staff = User.objects.create_user(username="sc_staff", password="pw")
        self.company = Company.objects.create(name="ConflictCo")
        self.owner_m = CompanyMember.objects.create(company=self.company, user=self.owner, role="OWNER")
        self.staff_m = CompanyMember.objects.create(company=self.company, user=self.staff, role="STAFF")
        self.event1 = Event.objects.create(
            company=self.company,
            created_by=self.owner_m,
            title="Morning Shift Event",
            event_date=date(2026, 11, 28),
            start_time=time(9, 0),
            end_time=time(13, 0),
            location="Hall A",
            status="UPCOMING",
        )
        self.event2 = Event.objects.create(
            company=self.company,
            created_by=self.owner_m,
            title="Overlapping Event",
            event_date=date(2026, 11, 28),
            start_time=time(11, 0),
            end_time=time(15, 0),
            location="Hall B",
            status="UPCOMING",
        )
        self.event3 = Event.objects.create(
            company=self.company,
            created_by=self.owner_m,
            title="Evening Event",
            event_date=date(2026, 11, 28),
            start_time=time(14, 0),
            end_time=time(18, 0),
            location="Hall C",
            status="UPCOMING",
        )
        self.client.login(username="sc_owner", password="pw")

    def test_blocks_overlapping_shift_and_allows_non_overlapping(self):
        EventAssignment.objects.create(
            event=self.event1,
            member=self.staff_m,
            assigned_role="Usher",
            start_time=time(9, 0),
            end_time=time(13, 0),
        )
        # Overlapping assignment should be blocked
        self.client.post(
            reverse("events:assignment_create", kwargs={"event_id": self.event2.id}),
            {
                "member_id": self.staff_m.id,
                "assigned_role": "Stage Hand",
                "start_time": "11:00",
                "end_time": "15:00",
            },
        )
        self.assertFalse(EventAssignment.objects.filter(event=self.event2, member=self.staff_m).exists())

        # Non-overlapping assignment on the same day should succeed
        self.client.post(
            reverse("events:assignment_create", kwargs={"event_id": self.event3.id}),
            {
                "member_id": self.staff_m.id,
                "assigned_role": "Closer",
                "start_time": "14:00",
                "end_time": "18:00",
            },
        )
        self.assertTrue(EventAssignment.objects.filter(event=self.event3, member=self.staff_m).exists())

    def test_blocks_unavailable_member_unless_overridden(self):
        MemberAvailability.objects.create(
            member=self.staff_m,
            availability_type="UNAVAILABLE",
            specific_date=date(2026, 11, 28),
            reason="Doctor appointment",
        )
        self.client.post(
            reverse("events:assignment_create", kwargs={"event_id": self.event1.id}),
            {
                "member_id": self.staff_m.id,
                "assigned_role": "Usher",
                "start_time": "09:00",
                "end_time": "13:00",
            },
        )
        self.assertFalse(EventAssignment.objects.filter(event=self.event1, member=self.staff_m).exists())

        # With override_unavailable=1 it succeeds
        self.client.post(
            reverse("events:assignment_create", kwargs={"event_id": self.event1.id}),
            {
                "member_id": self.staff_m.id,
                "assigned_role": "Usher",
                "start_time": "09:00",
                "end_time": "13:00",
                "override_unavailable": "1",
            },
        )
        self.assertTrue(EventAssignment.objects.filter(event=self.event1, member=self.staff_m).exists())






