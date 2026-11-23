from datetime import date, datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .models import Company, CompanyMember, Event, EventAssignment, AttendanceRecord, MemberAvailability, EventTask


def _parse_time_value(value):
    """Parse a time string in HH:MM or HH:MM:SS format into a datetime.time object."""
    if not value:
        return None
    if hasattr(value, "hour") and hasattr(value, "minute"):
        return value
    raw = str(value).strip()
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(raw, fmt).time()
        except ValueError:
            continue
    return None


def _validate_time_window(start_val, end_val):
    """Validate that start and end times parse cleanly and end_time is after start_time."""
    start_obj = _parse_time_value(start_val)
    end_obj = _parse_time_value(end_val)
    if start_obj is None or end_obj is None:
        return None, None, "Please provide valid start and end times."
    if end_obj <= start_obj:
        return None, None, "End time must be after start time."
    return start_obj, end_obj, None


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
            return render(request, "events/event_form.html", {"memberships": eligible_memberships, "is_edit": False})

        start_obj, end_obj, time_error = _validate_time_window(start_time, end_time)
        if time_error:
            messages.error(request, time_error)
            return render(request, "events/event_form.html", {"memberships": eligible_memberships, "is_edit": False})

        event = Event.objects.create(
            company=membership.company,
            created_by=membership,
            title=title,
            description=description,
            event_date=event_date,
            start_time=start_obj,
            end_time=end_obj,
            location=location,
            status=status,
        )
        messages.success(request, f'Event "{event.title}" created successfully! Now assign team members below.')
        return redirect("events:event_detail", event_id=event.id)

    return render(request, "events/event_form.html", {"memberships": eligible_memberships, "is_edit": False})


@login_required
def event_edit(request, event_id):
    """Edit an existing event's details (restricted to Owners and Managers)."""
    event = get_object_or_404(Event.objects.select_related("company"), id=event_id)
    user_membership = CompanyMember.objects.filter(
        company=event.company, user=request.user
    ).first()

    if not user_membership or user_membership.role not in ("OWNER", "MANAGER"):
        messages.error(request, "Only Owners and Managers can edit this event.")
        return redirect("events:event_detail", event_id=event.id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        event_date = request.POST.get("event_date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        location = request.POST.get("location", "").strip()
        status = request.POST.get("status", event.status)

        if not title or not event_date or not start_time or not end_time or not location:
            messages.error(request, "Please fill in all required fields.")
            return render(request, "events/event_form.html", {"event": event, "is_edit": True})

        start_obj, end_obj, time_error = _validate_time_window(start_time, end_time)
        if time_error:
            messages.error(request, time_error)
            return render(request, "events/event_form.html", {"event": event, "is_edit": True})

        event.title = title
        event.description = description
        event.event_date = event_date
        event.start_time = start_obj
        event.end_time = end_obj
        event.location = location
        if status in dict(Event.STATUS_CHOICES):
            event.status = status
        event.save()

        messages.success(request, f'Event "{event.title}" updated successfully!')
        return redirect("events:event_detail", event_id=event.id)

    return render(request, "events/event_form.html", {"event": event, "is_edit": True})


@login_required
def event_delete(request, event_id):
    """Delete an event (restricted to Owners and Managers)."""
    event = get_object_or_404(Event.objects.select_related("company"), id=event_id)
    user_membership = CompanyMember.objects.filter(
        company=event.company, user=request.user
    ).first()

    if not user_membership or user_membership.role not in ("OWNER", "MANAGER"):
        messages.error(request, "Only Owners and Managers can delete this event.")
        return redirect("events:event_detail", event_id=event.id)

    if request.method == "POST":
        title = event.title
        event.delete()
        messages.success(request, f'Event "{title}" and all its shift assignments have been deleted.')
        return redirect("events:event_list")

    return redirect("events:event_detail", event_id=event.id)


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
        "tasks": event.tasks.select_related("assigned_to__user", "completed_by__user").all(),
        "task_priority_choices": EventTask.PRIORITY_CHOICES,
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

        start_obj, end_obj, time_error = _validate_time_window(start_time, end_time)
        if time_error:
            messages.error(request, time_error)
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
            start_time=start_obj,
            end_time=end_obj,
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

            if start_time or end_time:
                start_obj, end_obj, time_error = _validate_time_window(
                    start_time or assignment.start_time,
                    end_time or assignment.end_time,
                )
                if time_error:
                    messages.error(request, time_error)
                    return redirect("events:event_detail", event_id=assignment.event.id)
                assignment.start_time = start_obj
                assignment.end_time = end_obj

            if role:
                assignment.assigned_role = role
            if location:
                assignment.assigned_location = location

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


# ==============================================================================
# ATTENDANCE & REAL-TIME CLOCK-IN/OUT VIEWS
# ==============================================================================

@login_required
def attendance_dashboard(request, company_id=None):
    """Real-time attendance tracking board across user's companies."""
    user_memberships = (
        CompanyMember.objects.filter(user=request.user)
        .select_related("company")
        .order_by("company__name")
    )
    user_company_ids = list(user_memberships.values_list("company_id", flat=True))

    selected_company = None
    if company_id:
        selected_company = get_object_or_404(Company, id=company_id, id__in=user_company_ids)
        target_company_ids = [selected_company.id]
    else:
        target_company_ids = user_company_ids

    records = (
        AttendanceRecord.objects.filter(assignment__event__company_id__in=target_company_ids)
        .select_related(
            "assignment__member__user",
            "assignment__event__company",
            "assignment__event",
            "verified_by__user",
        )
        .order_by("-clock_in_time")
    )

    total_clocked_in = records.filter(status="CLOCKED_IN").count()
    total_clocked_out = records.filter(status="CLOCKED_OUT").count()
    total_verified = records.filter(status="VERIFIED").count()

    # Find assignments assigned to the current user that have not yet clocked in
    my_pending_clockins = (
        EventAssignment.objects.filter(
            member__user=request.user,
            event__company_id__in=target_company_ids,
            attendance_record__isnull=True,
            status__in=["ASSIGNED", "CONFIRMED"],
        )
        .select_related("event__company", "event")
        .order_by("event__event_date", "start_time")
    )

    # Check manager permissions in selected or any company
    is_manager = user_memberships.filter(
        company_id__in=target_company_ids,
        role__in=["OWNER", "MANAGER"],
    ).exists()

    context = {
        "user_memberships": user_memberships,
        "selected_company": selected_company,
        "records": records,
        "total_clocked_in": total_clocked_in,
        "total_clocked_out": total_clocked_out,
        "total_verified": total_verified,
        "my_pending_clockins": my_pending_clockins,
        "is_manager": is_manager,
    }
    return render(request, "events/attendance_dashboard.html", context)


@login_required
def clock_in(request, assignment_id):
    """Clock in for a specific event assignment."""
    assignment = get_object_or_404(
        EventAssignment.objects.select_related("event__company", "member__user"),
        id=assignment_id,
    )
    user_membership = CompanyMember.objects.filter(
        company=assignment.event.company, user=request.user
    ).first()

    is_owner_or_manager = user_membership and user_membership.role in ("OWNER", "MANAGER")
    is_assignee = assignment.member.user == request.user

    if not (is_owner_or_manager or is_assignee):
        messages.error(request, "You are not authorized to clock in for this assignment.")
        return redirect("events:attendance_dashboard")

    if hasattr(assignment, "attendance_record"):
        messages.warning(request, f"{assignment.member.user.username} is already clocked in.")
        return redirect("events:attendance_dashboard")

    notes = request.POST.get("notes", "").strip() if request.method == "POST" else ""
    with transaction.atomic():
        AttendanceRecord.objects.create(
            assignment=assignment,
            clock_in_notes=notes,
            status="CLOCKED_IN",
        )
        assignment.status = "CONFIRMED"
        assignment.save(update_fields=["status"])

    messages.success(request, f"Successfully clocked in for {assignment.event.title} ({assignment.assigned_role})!")
    return redirect("events:attendance_dashboard")


@login_required
def clock_out(request, assignment_id):
    """Clock out from an active event assignment."""
    assignment = get_object_or_404(
        EventAssignment.objects.select_related("event__company", "member__user"),
        id=assignment_id,
    )
    user_membership = CompanyMember.objects.filter(
        company=assignment.event.company, user=request.user
    ).first()

    is_owner_or_manager = user_membership and user_membership.role in ("OWNER", "MANAGER")
    is_assignee = assignment.member.user == request.user

    if not (is_owner_or_manager or is_assignee):
        messages.error(request, "You are not authorized to clock out for this assignment.")
        return redirect("events:attendance_dashboard")

    if not hasattr(assignment, "attendance_record"):
        messages.error(request, "No active clock-in record found to clock out from.")
        return redirect("events:attendance_dashboard")

    record = assignment.attendance_record
    if record.clock_out_time:
        messages.warning(request, "This assignment has already been clocked out.")
        return redirect("events:attendance_dashboard")

    notes = request.POST.get("notes", "").strip() if request.method == "POST" else ""
    with transaction.atomic():
        record.clock_out_time = timezone.now()
        record.clock_out_notes = notes
        record.status = "CLOCKED_OUT"
        record.save()

        assignment.status = "COMPLETED"
        assignment.save(update_fields=["status"])

    messages.success(request, f"Clocked out from {assignment.event.title}. Total time: {record.duration_display()}.")
    return redirect("events:attendance_dashboard")


@login_required
def verify_attendance(request, record_id):
    """Manager verification of an employee's completed attendance record."""
    record = get_object_or_404(
        AttendanceRecord.objects.select_related("assignment__event__company"),
        id=record_id,
    )
    user_membership = CompanyMember.objects.filter(
        company=record.assignment.event.company,
        user=request.user,
        role__in=["OWNER", "MANAGER"],
    ).first()

    if not user_membership:
        messages.error(request, "Only Owners and Managers can verify attendance records.")
        return redirect("events:attendance_dashboard")

    if request.method == "POST":
        record.status = "VERIFIED"
        record.verified_by = user_membership
        record.verified_at = timezone.now()
        record.save(update_fields=["status", "verified_by", "verified_at"])
        messages.success(request, f"Attendance record for {record.assignment.member.user.username} verified!")

    return redirect("events:attendance_dashboard")


# ==============================================================================
# EMPLOYEE AVAILABILITY & SCHEDULE PREFERENCE VIEWS
# ==============================================================================

@login_required
def availability_list(request, company_id=None):
    """Team availability directory and preference submission board."""
    user_memberships = (
        CompanyMember.objects.filter(user=request.user)
        .select_related("company")
        .order_by("company__name")
    )
    user_company_ids = list(user_memberships.values_list("company_id", flat=True))

    selected_company = None
    if company_id:
        selected_company = get_object_or_404(Company, id=company_id, id__in=user_company_ids)
        target_company_ids = [selected_company.id]
    else:
        target_company_ids = user_company_ids

    # Query availability records for members in these companies
    availabilities = (
        MemberAvailability.objects.filter(member__company_id__in=target_company_ids)
        .select_related("member__user", "member__company")
        .order_by("availability_type", "day_of_week", "specific_date")
    )

    my_records = availabilities.filter(member__user=request.user)
    team_records = availabilities.exclude(member__user=request.user)

    available_count = availabilities.filter(availability_type="AVAILABLE").count()
    timeoff_count = availabilities.filter(availability_type="UNAVAILABLE").count()

    context = {
        "user_memberships": user_memberships,
        "selected_company": selected_company,
        "availabilities": availabilities,
        "my_records": my_records,
        "team_records": team_records,
        "available_count": available_count,
        "timeoff_count": timeoff_count,
        "days_of_week": MemberAvailability.DAYS_OF_WEEK,
        "availability_types": MemberAvailability.AVAILABILITY_TYPES,
    }
    return render(request, "events/availability_list.html", context)


@login_required
def availability_create(request):
    """Submit new availability preference or time-off request."""
    if request.method == "POST":
        company_id = request.POST.get("company_id")
        availability_type = request.POST.get("availability_type", "AVAILABLE")
        timing_type = request.POST.get("timing_type", "weekly")
        day_of_week = request.POST.get("day_of_week")
        specific_date = request.POST.get("specific_date")
        start_time = request.POST.get("start_time") or None
        end_time = request.POST.get("end_time") or None
        reason = request.POST.get("reason", "").strip()

        membership = CompanyMember.objects.filter(
            company_id=company_id, user=request.user
        ).first()

        if not membership:
            messages.error(request, "Invalid organization selected for availability.")
            return redirect("events:availability_list")

        clean_day = int(day_of_week) if (timing_type == "weekly" and day_of_week is not None and day_of_week != "") else None
        clean_date = specific_date if (timing_type == "date" and specific_date) else None

        MemberAvailability.objects.create(
            member=membership,
            availability_type=availability_type,
            day_of_week=clean_day,
            specific_date=clean_date,
            start_time=start_time,
            end_time=end_time,
            reason=reason,
        )
        messages.success(request, "Availability preference recorded successfully!")

    return redirect("events:availability_list")


@login_required
def availability_delete(request, record_id):
    """Remove an availability entry."""
    record = get_object_or_404(
        MemberAvailability.objects.select_related("member__company", "member__user"),
        id=record_id,
    )
    user_membership = CompanyMember.objects.filter(
        company=record.member.company, user=request.user
    ).first()

    is_author = record.member.user == request.user
    is_manager = user_membership and user_membership.role in ("OWNER", "MANAGER")

    if not (is_author or is_manager):
        messages.error(request, "You do not have permission to delete this availability record.")
        return redirect("events:availability_list")

    if request.method == "POST":
        record.delete()
        messages.success(request, "Availability entry deleted.")

    return redirect("events:availability_list")


# ==============================================================================
# EVENT OPERATIONAL TASKS & TELEMETRY ANALYTICS VIEWS
# ==============================================================================

@login_required
def task_create(request, event_id):
    """Add a new operational task checklist item to an event."""
    event = get_object_or_404(Event, id=event_id)
    user_membership = CompanyMember.objects.filter(
        company=event.company, user=request.user
    ).first()

    if not user_membership:
        messages.error(request, "You are not a member of this event's organization.")
        return redirect("events:event_detail", event_id=event.id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        priority = request.POST.get("priority", "MEDIUM")
        assigned_to_id = request.POST.get("assigned_to")
        due_time = request.POST.get("due_time") or None

        if not title:
            messages.error(request, "Task title is required.")
            return redirect("events:event_detail", event_id=event.id)

        assigned_to = None
        if assigned_to_id:
            assigned_to = CompanyMember.objects.filter(id=assigned_to_id, company=event.company).first()

        EventTask.objects.create(
            event=event,
            title=title,
            priority=priority,
            assigned_to=assigned_to,
            due_time=due_time,
        )
        messages.success(request, f'Task "{title}" added to checklist.')

    return redirect("events:event_detail", event_id=event.id)


@login_required
def task_toggle(request, task_id):
    """Toggle completion status of an operational task."""
    task = get_object_or_404(
        EventTask.objects.select_related("event__company"), id=task_id
    )
    user_membership = CompanyMember.objects.filter(
        company=task.event.company, user=request.user
    ).first()

    if not user_membership:
        messages.error(request, "You do not have access to toggle tasks for this event.")
        return redirect("events:event_detail", event_id=task.event.id)

    if request.method == "POST":
        task.is_completed = not task.is_completed
        if task.is_completed:
            task.completed_at = timezone.now()
            task.completed_by = user_membership
        else:
            task.completed_at = None
            task.completed_by = None
        task.save()
        status_label = "completed" if task.is_completed else "marked pending"
        messages.success(request, f'Task "{task.title}" {status_label}.')

    return redirect("events:event_detail", event_id=task.event.id)


@login_required
def task_delete(request, task_id):
    """Delete an operational task."""
    task = get_object_or_404(
        EventTask.objects.select_related("event__company"), id=task_id
    )
    user_membership = CompanyMember.objects.filter(
        company=task.event.company, user=request.user
    ).first()

    if not user_membership or user_membership.role not in ("OWNER", "MANAGER"):
        messages.error(request, "Only Owners and Managers can delete checklist tasks.")
        return redirect("events:event_detail", event_id=task.event.id)

    if request.method == "POST":
        title = task.title
        event_id = task.event.id
        task.delete()
        messages.success(request, f'Task "{title}" deleted.')

    return redirect("events:event_detail", event_id=event_id)


@login_required
def analytics_report(request, company_id=None):
    """Consolidated telemetry and shift readiness analytics report."""
    user_memberships = (
        CompanyMember.objects.filter(user=request.user)
        .select_related("company")
        .order_by("company__name")
    )
    user_company_ids = list(user_memberships.values_list("company_id", flat=True))

    selected_company = None
    if company_id:
        selected_company = get_object_or_404(Company, id=company_id, id__in=user_company_ids)
        target_company_ids = [selected_company.id]
    else:
        target_company_ids = user_company_ids

    events = Event.objects.filter(company_id__in=target_company_ids)
    total_events = events.count()
    upcoming_events = events.filter(status="UPCOMING").count()
    completed_events = events.filter(status="COMPLETED").count()
    draft_events = events.filter(status="DRAFT").count()

    assignments = EventAssignment.objects.filter(event__company_id__in=target_company_ids)
    total_assignments = assignments.count()
    confirmed_assignments = assignments.filter(status__in=["CONFIRMED", "COMPLETED"]).count()
    completed_assignments = assignments.filter(status="COMPLETED").count()
    confirmation_rate = int(confirmed_assignments / total_assignments * 100) if total_assignments > 0 else 0

    attendance_records = AttendanceRecord.objects.filter(assignment__event__company_id__in=target_company_ids)
    total_logs = attendance_records.count()
    verified_logs = attendance_records.filter(status="VERIFIED").count()
    verification_rate = int(verified_logs / total_logs * 100) if total_logs > 0 else 0

    tasks = EventTask.objects.filter(event__company_id__in=target_company_ids)
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(is_completed=True).count()
    task_rate = int(completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    context = {
        "user_memberships": user_memberships,
        "selected_company": selected_company,
        "total_events": total_events,
        "upcoming_events": upcoming_events,
        "completed_events": completed_events,
        "draft_events": draft_events,
        "total_assignments": total_assignments,
        "confirmed_assignments": confirmed_assignments,
        "completed_assignments": completed_assignments,
        "confirmation_rate": confirmation_rate,
        "total_logs": total_logs,
        "verified_logs": verified_logs,
        "verification_rate": verification_rate,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "task_rate": task_rate,
        "events": events.order_by("-event_date")[:10],
    }
    return render(request, "events/analytics_report.html", context)



