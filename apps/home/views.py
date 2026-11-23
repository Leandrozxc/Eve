from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.events.models import (
    AttendanceRecord,
    Company,
    CompanyMember,
    Event,
    EventAssignment,
    EventTask,
    ShiftSwapRequest,
)


@login_required
def home_view(request):
    """Home view protected by login requirement.

    Provides high-level dashboard metrics, upcoming shifts, attention queue, and company roles.
    """
    user_memberships = (
        CompanyMember.objects.filter(user=request.user)
        .select_related("company")
        .order_by("-joined_at")
    )
    company_ids = list(user_memberships.values_list("company_id", flat=True))
    managed_company_ids = [
        m.company_id for m in user_memberships if m.role in ("OWNER", "MANAGER")
    ]

    # User's personal upcoming assignments
    my_assignments = (
        EventAssignment.objects.filter(
            member__user=request.user,
            event__event_date__gte=date.today(),
        )
        .exclude(status="CANCELLED")
        .select_related("event__company", "event")
        .order_by("event__event_date", "start_time")[:5]
    )

    # Company events summary
    company_events = (
        Event.objects.filter(company_id__in=company_ids)
        .select_related("company")
        .order_by("event_date", "start_time")
    )
    upcoming_events_qs = company_events.filter(status="UPCOMING")
    upcoming_events_count = upcoming_events_qs.count()
    total_events_count = company_events.count()
    upcoming_events_list = upcoming_events_qs[:5]

    # Staffing progress across all events
    total_assignments_count = EventAssignment.objects.filter(event__company_id__in=company_ids).count()
    confirmed_assignments_count = EventAssignment.objects.filter(
        event__company_id__in=company_ids,
        status__in=["CONFIRMED", "COMPLETED"],
    ).count()

    confirmation_rate = (
        int(confirmed_assignments_count / total_assignments_count * 100)
        if total_assignments_count > 0
        else 0
    )

    # Needs-attention operational counts (strictly backed by real records)
    pending_confirmations_count = EventAssignment.objects.filter(
        member__user=request.user,
        status="ASSIGNED",
        event__event_date__gte=date.today(),
    ).count()
    pending_swaps_count = ShiftSwapRequest.objects.filter(
        assignment__event__company_id__in=managed_company_ids if managed_company_ids else company_ids,
        status="PENDING",
    ).count()
    unverified_attendance_count = AttendanceRecord.objects.filter(
        assignment__event__company_id__in=managed_company_ids,
        status="CLOCKED_OUT",
    ).count() if managed_company_ids else 0
    incomplete_tasks_count = EventTask.objects.filter(
        event__company_id__in=company_ids,
        is_completed=False,
    ).count()

    context = {
        "today": date.today(),
        "user_memberships": user_memberships,
        "my_assignments": my_assignments,
        "upcoming_events_list": upcoming_events_list,
        "upcoming_events_count": upcoming_events_count,
        "total_events_count": total_events_count,
        "total_assignments_count": total_assignments_count,
        "confirmation_rate": confirmation_rate,
        "pending_confirmations_count": pending_confirmations_count,
        "pending_swaps_count": pending_swaps_count,
        "unverified_attendance_count": unverified_attendance_count,
        "incomplete_tasks_count": incomplete_tasks_count,
        "can_manage_any": bool(managed_company_ids),
    }
    return render(request, "home/home.html", context)
