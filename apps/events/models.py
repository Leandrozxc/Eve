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