from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.events.models import Company, CompanyMember, Event, EventAssignment


@login_required
def home_view(request):
    """Home view protected by login requirement.

    Provides high-level dashboard metrics, upcoming shifts, and company roles.
    """
    user_memberships = (
        CompanyMember.objects.filter(user=request.user)
        .select_related("company")
        .order_by("-joined_at")
    )
    company_ids = user_memberships.values_list("company_id", flat=True)

    # User's personal upcoming assignments
    my_assignments = (
        EventAssignment.objects.filter(
            member__user=request.user,
            event__event_date__gte=date.today(),
        )
        .select_related("event__company", "event")
        .order_by("event__event_date", "start_time")[:5]
    )

    # Company events summary
    company_events = (
        Event.objects.filter(company_id__in=company_ids)
        .select_related("company")
        .order_by("event_date")
    )
    upcoming_events_count = company_events.filter(status="UPCOMING").count()
    total_events_count = company_events.count()

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

    context = {
        "user_memberships": user_memberships,
        "my_assignments": my_assignments,
        "upcoming_events_count": upcoming_events_count,
        "total_events_count": total_events_count,
        "total_assignments_count": total_assignments_count,
        "confirmation_rate": confirmation_rate,
    }
    return render(request, "home/home.html", context)
