from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

from .models import Branch, Asset, Loan


@login_required
def branch_monitoring(request):

    if request.user.is_superuser:
        role = "ADMIN"
    else:
        try:
            role = request.user.profile.role
        except Exception:
            role = ""

    if role not in ["MANAGER", "ADMIN"]:
        messages.error(
            request,
            "You do not have permission to view branch monitoring."
        )
        return redirect("dashboard")

    branch_data = []

    for branch in Branch.objects.all().order_by("name"):

        assets = Asset.objects.filter(branch=branch)

        branch_data.append({
            "branch": branch,
            "total_assets": assets.count(),
            "available_assets": assets.filter(
                status="AVAILABLE"
            ).count(),
            "borrowed_assets": assets.filter(
                status="BORROWED"
            ).count(),
            "maintenance_assets": assets.filter(
                status="MAINTENANCE"
            ).count(),
        })

    return render(
        request,
        "myapp/branch_monitoring.html",
        {
            "branch_data": branch_data,
        }
    )


@login_required
def overdue_tracking(request):

    if request.user.is_superuser:
        role = "ADMIN"
    else:
        try:
            role = request.user.profile.role
        except Exception:
            role = ""

    if role not in ["MANAGER", "ADMIN"]:
        messages.error(
            request,
            "You do not have permission to view overdue tracking."
        )
        return redirect("dashboard")

    from django.utils import timezone

    overdue_loans = Loan.objects.filter(
        status="ACTIVE",
        due_date__lt=timezone.localdate()
    ).select_related(
        "asset",
        "borrower",
        "branch"
    ).order_by("due_date")

    return render(
        request,
        "myapp/overdue_tracking.html",
        {
            "overdue_loans": overdue_loans,
            "overdue_count": overdue_loans.count(),
        }
    )