from django.conf import settings
from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=150)
    contact_number = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name


class CompanyMember(models.Model):
    ROLE_CHOICES = [
        ("OWNER", "Owner"),
        ("MANAGER", "Manager"),
        ("STAFF", "Staff"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="members",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="company_memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="STAFF",
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "user"],
                name="unique_company_member",
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.company.name}"


class Event(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("UPCOMING", "Upcoming"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="events",
    )
    created_by = models.ForeignKey(
        CompanyMember,
        on_delete=models.PROTECT,
        related_name="created_events",
    )
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=150)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class EventAssignment(models.Model):
    STATUS_CHOICES = [
        ("ASSIGNED", "Assigned"),
        ("CONFIRMED", "Confirmed"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    member = models.ForeignKey(
        CompanyMember,
        on_delete=models.CASCADE,
        related_name="event_assignments",
    )
    assigned_role = models.CharField(max_length=100)
    assigned_location = models.CharField(max_length=150, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ASSIGNED",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "member"],
                name="unique_event_assignment",
            )
        ]

    def __str__(self):
        return f"{self.member.user.username} - {self.event.title}"


class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ("CLOCKED_IN", "Clocked In"),
        ("CLOCKED_OUT", "Clocked Out"),
        ("VERIFIED", "Verified by Manager"),
    ]

    assignment = models.OneToOneField(
        EventAssignment,
        on_delete=models.CASCADE,
        related_name="attendance_record",
    )
    clock_in_time = models.DateTimeField(auto_now_add=True)
    clock_out_time = models.DateTimeField(null=True, blank=True)
    clock_in_notes = models.CharField(max_length=255, blank=True)
    clock_out_notes = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="CLOCKED_IN",
    )
    verified_by = models.ForeignKey(
        CompanyMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_attendances",
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    def duration_display(self):
        if not self.clock_out_time:
            return "In progress"
        diff = self.clock_out_time - self.clock_in_time
        hours, remainder = divmod(int(diff.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours}h {minutes}m"

    def __str__(self):
        return f"Attendance: {self.assignment.member.user.username} @ {self.assignment.event.title}"


class MemberAvailability(models.Model):
    AVAILABILITY_TYPES = [
        ("AVAILABLE", "Preferred Available"),
        ("UNAVAILABLE", "Unavailable / Time Off"),
    ]
    DAYS_OF_WEEK = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    member = models.ForeignKey(
        CompanyMember,
        on_delete=models.CASCADE,
        related_name="availability_preferences",
    )
    availability_type = models.CharField(
        max_length=20,
        choices=AVAILABILITY_TYPES,
        default="AVAILABLE",
    )
    day_of_week = models.IntegerField(
        choices=DAYS_OF_WEEK,
        null=True,
        blank=True,
        help_text="Recurring weekly day preference",
    )
    specific_date = models.DateField(
        null=True,
        blank=True,
        help_text="Specific single date time-off or override",
    )
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["day_of_week", "specific_date", "start_time"]

    def __str__(self):
        target = self.get_day_of_week_display() if self.day_of_week is not None else str(self.specific_date)
        return f"{self.member.user.username} - {self.get_availability_type_display()} ({target})"


class EventTask(models.Model):
    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("URGENT", "Urgent"),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    assigned_to = models.ForeignKey(
        CompanyMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    title = models.CharField(max_length=150)
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="MEDIUM",
    )
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        CompanyMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="completed_tasks",
    )
    due_time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["is_completed", "-priority", "created_at"]

    def __str__(self):
        status = "Done" if self.is_completed else "Pending"
        return f"[{status}] {self.title} ({self.event.title})"


class ShiftSwapRequest(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("DECLINED", "Declined"),
        ("CANCELLED", "Cancelled"),
    ]

    assignment = models.ForeignKey(
        EventAssignment,
        on_delete=models.CASCADE,
        related_name="swap_requests",
    )
    requested_by = models.ForeignKey(
        CompanyMember,
        on_delete=models.CASCADE,
        related_name="swap_requests_sent",
    )
    target_member = models.ForeignKey(
        CompanyMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="swap_requests_received",
        help_text="Optional specific teammate; leave blank for an open cover request.",
    )
    reason = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )
    reviewed_by = models.ForeignKey(
        CompanyMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="swap_requests_reviewed",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"SwapRequest({self.assignment.event.title}: {self.requested_by.user.username} -> {self.get_status_display()})"


