from .models import CompanyMember


def workspace_navigation(request):
    """Provide pre-fetched organization memberships for the global sidebar and topbar."""
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {
            "nav_memberships": [],
            "nav_primary_membership": None,
            "nav_can_manage_any": False,
        }

    memberships = list(
        CompanyMember.objects.filter(user=request.user)
        .select_related("company")
        .order_by("role", "-joined_at")
    )
    primary = memberships[0] if memberships else None
    can_manage_any = any(m.role in ("OWNER", "MANAGER") for m in memberships)
    return {
        "nav_memberships": memberships,
        "nav_primary_membership": primary,
        "nav_can_manage_any": can_manage_any,
    }
