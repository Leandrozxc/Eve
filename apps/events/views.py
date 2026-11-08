from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Company, CompanyMember, Event, EventAssignment

# Raw SQL Joins for IM2 Demonstration
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


# ==============================================================================
# COMPANY & ROLES VIEWS
# ==============================================================================

@login_required
def company_list(request):
    """List companies the user belongs to, plus other companies they can join."""
    my_memberships = (
        CompanyMember.objects.filter(user=request.user)
        .select_related("company")
        .order_by("-joined_at")
    )
    my_company_ids = my_memberships.values_list("company_id", flat=True)

    other_companies = (
        Company.objects.exclude(id__in=my_company_ids)
        .order_by("name")
    )

    context = {
        "my_memberships": my_memberships,
        "other_companies": other_companies,
    }
    return render(request, "events/company_list.html", context)


@login_required
def company_create(request):
    """Create a new company; the creator becomes OWNER."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        contact_number = request.POST.get("contact_number", "").strip()
        address = request.POST.get("address", "").strip()

        if not name:
            messages.error(request, "Company name is required.")
            return render(request, "events/company_form.html")

        with transaction.atomic():
            company = Company.objects.create(
                name=name,
                contact_number=contact_number,
                address=address,
            )
            CompanyMember.objects.create(
                company=company,
                user=request.user,
                role="OWNER",
            )

        messages.success(request, f'Company "{company.name}" created successfully! You are the Owner.')
        return redirect("events:company_list")

    return render(request, "events/company_form.html")


@login_required
def company_join(request, company_id):
    """Join an existing company as STAFF."""
    company = get_object_or_404(Company, id=company_id)

    if CompanyMember.objects.filter(company=company, user=request.user).exists():
        messages.info(request, f"You are already a member of {company.name}.")
        return redirect("events:company_list")

    CompanyMember.objects.create(
        company=company,
        user=request.user,
        role="STAFF",
    )
    messages.success(request, f'You successfully joined "{company.name}" as Staff!')
    return redirect("events:company_list")


@login_required
def company_members(request, company_id):
    """Manage company members and their roles (Owner, Manager, Staff)."""
    company = get_object_or_404(Company, id=company_id)
    current_membership = get_object_or_404(CompanyMember, company=company, user=request.user)

    can_manage = current_membership.role in ("OWNER", "MANAGER")

    if request.method == "POST" and can_manage:
        action = request.POST.get("action")
        member_id = request.POST.get("member_id")
        target_member = get_object_or_404(CompanyMember, id=member_id, company=company)

        if action == "change_role":
            new_role = request.POST.get("new_role")
            if new_role in dict(CompanyMember.ROLE_CHOICES):
                # Ensure we don't demote the last owner
                if target_member.role == "OWNER" and new_role != "OWNER":
                    owners_count = CompanyMember.objects.filter(company=company, role="OWNER").count()
                    if owners_count <= 1:
                        messages.error(request, "Cannot demote the sole owner of the company.")
                        return redirect("events:company_members", company_id=company.id)

                target_member.role = new_role
                target_member.save()
                messages.success(request, f"Updated role for {target_member.user.get_full_name() or target_member.user.username} to {target_member.get_role_display()}.")

        elif action == "remove_member":
            if target_member.role == "OWNER":
                owners_count = CompanyMember.objects.filter(company=company, role="OWNER").count()
                if owners_count <= 1:
                    messages.error(request, "Cannot remove the sole owner of the company.")
                    return redirect("events:company_members", company_id=company.id)

            username = target_member.user.username
            target_member.delete()
            messages.success(request, f"Removed {username} from {company.name}.")

        return redirect("events:company_members", company_id=company.id)

    members = company.members.select_related("user").order_by("role", "-joined_at")

    context = {
        "company": company,
        "members": members,
        "current_membership": current_membership,
        "can_manage": can_manage,
        "role_choices": CompanyMember.ROLE_CHOICES,
    }
    return render(request, "events/company_members.html", context)


# ==============================================================================
# EVENT & ASSIGNMENT VIEWS
# ==============================================================================

@login_required
def event_list(request):
    """List all events with progress indicators and filter options."""
    my_memberships = request.user.company_memberships.select_related("company").all()
    company_ids = [m.company_id for m in my_memberships]

    status_filter = request.GET.get("status", "")
    company_filter = request.GET.get("company_id", "")

    events_qs = (
        Event.objects.all()
        .select_related("company", "created_by__user")
        .prefetch_related("assignments__member__user")
        .order_by("-event_date")
    )

    if company_filter and company_filter.isdigit():
        events_qs = events_qs.filter(company_id=int(company_filter))
    elif company_ids:
        # Default to user's companies if any exist
        user_events = events_qs.filter(company_id__in=company_ids)
        if user_events.exists():
            events_qs = user_events

    if status_filter in dict(Event.STATUS_CHOICES):
        events_qs = events_qs.filter(status=status_filter)

    # Compute progress stats for each event
    events_data = []
    for ev in events_qs:
        total_assignments = ev.assignments.count()
        confirmed_count = ev.assignments.filter(status__in=["CONFIRMED", "COMPLETED"]).count()
        completed_count = ev.assignments.filter(status="COMPLETED").count()
        progress_pct = int((confirmed_count / total_assignments * 100)) if total_assignments > 0 else 0

        events_data.append({
            "event": ev,
            "total_assignments": total_assignments,
            "confirmed_count": confirmed_count,
            "completed_count": completed_count,
            "progress_pct": progress_pct,
        })

    context = {
        "events_data": events_data,
        "status_filter": status_filter,
        "company_filter": company_filter,
        "status_choices": Event.STATUS_CHOICES,
        "my_memberships": my_memberships,
    }
    return render(request, "events/event_list.html", context)


@login_required
def event_create(request):
    """Create a new event under one of the user's companies."""
    eligible_memberships = request.user.company_memberships.filter(
        role__in=["OWNER", "MANAGER", "STAFF"]
    ).select_related("company")

    if not eligible_memberships.exists():
        messages.warning(request, "Please create or join a company first before scheduling an event.")
        return redirect("events:company_create")

    if request.method == "POST":
        company_id = request.POST.get("company_id")
        membership = eligible_memberships.filter(company_id=company_id).first()
        if not membership:
            membership = eligible_memberships.first()

        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        event_date = request.POST.get("event_date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        location = request.POST.get("location", "").strip()
        status = request.POST.get("status", "UPCOMING")

        if not title or not event_date or not start_time or not end_time or not location:
            messages.error(request, "Please fill in all required fields.")
            return render(request, "events/event_form.html", {"memberships": eligible_memberships})

        event = Event.objects.create(
            company=membership.company,
            created_by=membership,
            title=title,
            description=description,
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            location=location,
            status=status,
        )
        messages.success(request, f'Event "{event.title}" created successfully! Now assign team members below.')
        return redirect("events:event_detail", event_id=event.id)

    return render(request, "events/event_form.html", {"memberships": eligible_memberships})


@login_required
def event_detail(request, event_id):
    """Track event progress and manage assignments."""
    event = get_object_or_404(
        Event.objects.select_related("company", "created_by__user"),
        id=event_id,
    )

    user_membership = CompanyMember.objects.filter(
        company=event.company, user=request.user
    ).first()

    can_manage = user_membership is not None and user_membership.role in ("OWNER", "MANAGER")

    assignments = (
        event.assignments.select_related("member__user")
        .order_by("start_time", "assigned_role")
    )

    # Calculate progress metrics
    total_assignments = assignments.count()
    assigned_count = assignments.filter(status="ASSIGNED").count()
    confirmed_count = assignments.filter(status="CONFIRMED").count()
    completed_count = assignments.filter(status="COMPLETED").count()
    cancelled_count = assignments.filter(status="CANCELLED").count()

    active_assignments = confirmed_count + completed_count
    progress_pct = int((active_assignments / total_assignments * 100)) if total_assignments > 0 else 0

    # Company members not yet assigned to this event
    assigned_member_ids = assignments.values_list("member_id", flat=True)
    available_members = event.company.members.exclude(id__in=assigned_member_ids).select_related("user")

    # Check if current logged in user has an assignment
    my_assignment = assignments.filter(member__user=request.user).first()

    context = {
        "event": event,
        "assignments": assignments,
        "user_membership": user_membership,
        "can_manage": can_manage,
        "available_members": available_members,
        "my_assignment": my_assignment,
        "total_assignments": total_assignments,
        "assigned_count": assigned_count,
        "confirmed_count": confirmed_count,
        "completed_count": completed_count,
        "cancelled_count": cancelled_count,
        "progress_pct": progress_pct,
        "status_choices": Event.STATUS_CHOICES,
        "assignment_status_choices": EventAssignment.STATUS_CHOICES,
    }
    return render(request, "events/event_detail.html", context)


@login_required
def event_update_status(request, event_id):
    """Change overall event status (Draft, Upcoming, Completed, Cancelled)."""
    event = get_object_or_404(Event, id=event_id)
    user_membership = CompanyMember.objects.filter(
        company=event.company, user=request.user
    ).first()

    if not user_membership or user_membership.role not in ("OWNER", "MANAGER"):
        messages.error(request, "You do not have permission to update this event's status.")
        return redirect("events:event_detail", event_id=event.id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Event.STATUS_CHOICES):
            event.status = new_status
            event.save()
            messages.success(request, f'Event status updated to {event.get_status_display()}.')

    return redirect("events:event_detail", event_id=event.id)


@login_required
def assignment_create(request, event_id):
    """Assign a company member to the event with role, location, times, and status."""
    event = get_object_or_404(Event, id=event_id)
    user_membership = CompanyMember.objects.filter(
        company=event.company, user=request.user
    ).first()

    if not user_membership or user_membership.role not in ("OWNER", "MANAGER"):
        messages.error(request, "Only Owners and Managers can assign members to events.")
        return redirect("events:event_detail", event_id=event.id)

    if request.method == "POST":
        member_id = request.POST.get("member_id")
        assigned_role = request.POST.get("assigned_role", "").strip()
        assigned_location = request.POST.get("assigned_location", "").strip() or event.location
        start_time = request.POST.get("start_time") or str(event.start_time)
        end_time = request.POST.get("end_time") or str(event.end_time)
        status = request.POST.get("status", "ASSIGNED")

        if not member_id or not assigned_role:
            messages.error(request, "Please select a member and assign a role.")
            return redirect("events:event_detail", event_id=event.id)

        target_member = get_object_or_404(CompanyMember, id=member_id, company=event.company)

        # Check unique constraint
        if EventAssignment.objects.filter(event=event, member=target_member).exists():
            messages.warning(request, f"{target_member.user.username} is already assigned to this event.")
            return redirect("events:event_detail", event_id=event.id)

        EventAssignment.objects.create(
            event=event,
            member=target_member,
            assigned_role=assigned_role,
            assigned_location=assigned_location,
            start_time=start_time,
            end_time=end_time,
            status=status,
        )
        messages.success(request, f"Assigned {target_member.user.get_full_name() or target_member.user.username} as {assigned_role}!")

    return redirect("events:event_detail", event_id=event.id)


@login_required
def assignment_update(request, assignment_id):
    """Update an assignment's role, location, times, and status."""
    assignment = get_object_or_404(EventAssignment.objects.select_related("event__company"), id=assignment_id)
    user_membership = CompanyMember.objects.filter(
        company=assignment.event.company, user=request.user
    ).first()

    # Can be updated by Owner/Manager OR the assigned user themselves (for confirming/completing status)
    is_manager = user_membership is not None and user_membership.role in ("OWNER", "MANAGER")
    is_assignee = assignment.member.user == request.user

    if not (is_manager or is_assignee):
        messages.error(request, "You do not have permission to update this assignment.")
        return redirect("events:event_detail", event_id=assignment.event.id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(EventAssignment.STATUS_CHOICES):
            assignment.status = new_status

        # Only managers can change role, location, times
        if is_manager:
            role = request.POST.get("assigned_role", "").strip()
            location = request.POST.get("assigned_location", "").strip()
            start_time = request.POST.get("start_time")
            end_time = request.POST.get("end_time")

            if role:
                assignment.assigned_role = role
            if location:
                assignment.assigned_location = location
            if start_time:
                assignment.start_time = start_time
            if end_time:
                assignment.end_time = end_time

        assignment.save()
        messages.success(request, f"Assignment for {assignment.member.user.username} updated to {assignment.get_status_display()}.")

    return redirect("events:event_detail", event_id=assignment.event.id)


@login_required
def assignment_delete(request, assignment_id):
    """Remove a member's assignment from an event."""
    assignment = get_object_or_404(EventAssignment.objects.select_related("event__company"), id=assignment_id)
    event_id = assignment.event.id

    user_membership = CompanyMember.objects.filter(
        company=assignment.event.company, user=request.user
    ).first()

    if not user_membership or user_membership.role not in ("OWNER", "MANAGER"):
        messages.error(request, "Only Owners and Managers can remove event assignments.")
        return redirect("events:event_detail", event_id=event_id)

    if request.method == "POST":
        username = assignment.member.user.username
        assignment.delete()
        messages.success(request, f"Removed assignment for {username}.")

    return redirect("events:event_detail", event_id=event_id)
