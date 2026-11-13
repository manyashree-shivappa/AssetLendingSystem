from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date


from .models import (
    Branch,
    Category,
    UserProfile,
    Asset,
    LoanRequest,
    Loan,
    BranchTransfer,
    TransferLocation,
    AssetReturn,
)

# --------------------------------------------------
# ROLE MANAGEMENT
# --------------------------------------------------

def current_role(user):
    if not user.is_authenticated:
        return ""

    if user.is_superuser:
        return "ADMIN"

    try:
        return user.profile.role
    except UserProfile.DoesNotExist:
        return ""


def role_required(*allowed_roles):
    def decorator(view_function):
        @wraps(view_function)
        @login_required
        def wrapper(request, *args, **kwargs):
            role = current_role(request.user)

            if role not in allowed_roles:
                messages.error(
                    request,
                    "You do not have permission to access this page."
                )
                return redirect("dashboard")

            return view_function(request, *args, **kwargs)

        return wrapper

    return decorator


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

def login_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        selected_role = request.POST.get("role", "").upper()

        allowed_roles = {"ADMIN", "MANAGER", "STAFF"}

        if selected_role not in allowed_roles:
            messages.error(request, "Please select a valid role.")
            return render(request, "myapp/login.html")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:
            messages.error(
                request,
                "Invalid username or password."
            )
            return render(request, "myapp/login.html")

        actual_role = current_role(user)

        if not actual_role or actual_role != selected_role:
            messages.error(
                request,
                "The selected role does not match this account."
            )
            return render(request, "myapp/login.html")

        login(request, user)
        messages.success(request, "Login successful!")

        return redirect("dashboard")

    return render(request, "myapp/login.html")


# --------------------------------------------------
# BRANCH STAFF REGISTRATION
# --------------------------------------------------

def register_page(request):
    from django.contrib.auth.models import User

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")
        branch_id = request.POST.get("branch")

        if not username or not password1:
            messages.error(
                request,
                "Username and password are required."
            )

        elif password1 != password2:
            messages.error(
                request,
                "Passwords do not match."
            )

        elif User.objects.filter(username=username).exists():
            messages.error(
                request,
                "That username is already taken."
            )

        else:
            branch = None

            if branch_id:
                branch = get_object_or_404(
                    Branch,
                    pk=branch_id
                )

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )

            UserProfile.objects.create(
                user=user,
                role="STAFF",
                branch=branch
            )

            group, created = Group.objects.get_or_create(
                name="Branch Staff"
            )

            user.groups.add(group)

            messages.success(
                request,
                "Registration successful. Please log in."
            )

            return redirect("login")

    return render(
        request,
        "myapp/register.html",
        {
            "branches": Branch.objects.all()
        }
    )


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@login_required
def logout_page(request):
    logout(request)
    return redirect("login")


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@login_required
def dashboard(request):
    role = current_role(request.user)

    context = {
        "user_role": role,
        "total_assets": Asset.objects.count(),
        "available_assets": Asset.objects.filter(
            status="AVAILABLE"
        ).count(),
        "borrowed_assets": Asset.objects.filter(
            status="BORROWED"
        ).count(),
        "total_branches": Branch.objects.count(),
        "pending_requests": LoanRequest.objects.filter(
            status="PENDING"
        ).count(),
        "overdue_assets": Loan.objects.filter(
            status="ACTIVE",
            due_date__lt=timezone.localdate()
        ).count(),
    }

    return render(
        request,
        "myapp/dashboard.html",
        context
    )


# --------------------------------------------------
# ASSET MANAGEMENT
# --------------------------------------------------

from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date

from .models import (
    Branch,
    Category,
    UserProfile,
    Asset,
    LoanRequest,
    Loan,
    BranchTransfer,
    AssetReturn,
)


# --------------------------------------------------
# ROLE MANAGEMENT
# --------------------------------------------------

def current_role(user):
    if not user.is_authenticated:
        return ""

    if user.is_superuser:
        return "ADMIN"

    try:
        return user.profile.role
    except UserProfile.DoesNotExist:
        return ""


def role_required(*allowed_roles):
    def decorator(view_function):
        @wraps(view_function)
        @login_required
        def wrapper(request, *args, **kwargs):
            role = current_role(request.user)

            if role not in allowed_roles:
                messages.error(
                    request,
                    "You do not have permission to access this page."
                )
                return redirect("dashboard")

            return view_function(request, *args, **kwargs)

        return wrapper

    return decorator


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

def login_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        selected_role = request.POST.get("role", "").upper()

        allowed_roles = {"ADMIN", "MANAGER", "STAFF"}

        if selected_role not in allowed_roles:
            messages.error(request, "Please select a valid role.")
            return render(request, "myapp/login.html")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:
            messages.error(
                request,
                "Invalid username or password."
            )
            return render(request, "myapp/login.html")

        actual_role = current_role(user)

        if not actual_role or actual_role != selected_role:
            messages.error(
                request,
                "The selected role does not match this account."
            )
            return render(request, "myapp/login.html")

        login(request, user)
        messages.success(request, "Login successful!")

        return redirect("dashboard")

    return render(request, "myapp/login.html")


# --------------------------------------------------
# BRANCH STAFF REGISTRATION
# --------------------------------------------------

def register_page(request):
    from django.contrib.auth.models import User

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")
        branch_id = request.POST.get("branch")

        if not username or not password1:
            messages.error(
                request,
                "Username and password are required."
            )

        elif password1 != password2:
            messages.error(
                request,
                "Passwords do not match."
            )

        elif User.objects.filter(username=username).exists():
            messages.error(
                request,
                "That username is already taken."
            )

        else:
            branch = None

            if branch_id:
                branch = get_object_or_404(
                    Branch,
                    pk=branch_id
                )

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )

            UserProfile.objects.create(
                user=user,
                role="STAFF",
                branch=branch
            )

            group, created = Group.objects.get_or_create(
                name="Branch Staff"
            )

            user.groups.add(group)

            messages.success(
                request,
                "Registration successful. Please log in."
            )

            return redirect("login")

    return render(
        request,
        "myapp/register.html",
        {
            "branches": Branch.objects.all()
        }
    )


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@login_required
def logout_page(request):
    logout(request)
    return redirect("login")


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@login_required
def dashboard(request):
    role = current_role(request.user)

    context = {
        "user_role": role,
        "total_assets": Asset.objects.count(),
        "available_assets": Asset.objects.filter(
            status="AVAILABLE"
        ).count(),
        "borrowed_assets": Asset.objects.filter(
            status="BORROWED"
        ).count(),
        "total_branches": Branch.objects.count(),
        "pending_requests": LoanRequest.objects.filter(
            status="PENDING"
        ).count(),
        "overdue_assets": Loan.objects.filter(
            status="ACTIVE",
            due_date__lt=timezone.localdate()
        ).count(),
    }

    return render(
        request,
        "myapp/dashboard.html",
        context
    )


# --------------------------------------------------
# ASSET MANAGEMENT
# --------------------------------------------------
@login_required
def assets(request):
    from django.db.models import Q

    # Get all assets with their category and branch
    asset_list = Asset.objects.select_related(
        "category",
        "branch"
    ).all()

    # Get all categories for the dropdown
    categories = Category.objects.all().order_by("name")

    # Read search and filter values
    search = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    status = request.GET.get("status", "").strip()

    # Search by asset name or asset code
    if search:
        asset_list = asset_list.filter(
            Q(name__icontains=search) |
            Q(asset_code__icontains=search)
        )

    # Filter by category
    if category_id:
        asset_list = asset_list.filter(
            category_id=category_id
        )

    # Filter by status
    if status:
        asset_list = asset_list.filter(
            status=status
        )

    # Send all required information to the HTML page
    context = {
        "assets": asset_list,
        "categories": categories,
        "user_role": current_role(request.user),
        "selected_category": category_id,
        "selected_status": status,
        "search_query": search,
    }

    return render(
        request,
        "myapp/assets.html",
        context
    )

@login_required
def asset_detail(request, asset_id):
    asset = get_object_or_404(
        Asset,
        pk=asset_id
    )

    return render(
        request,
        "myapp/asset_detail.html",
        {
            "asset": asset
        }
    )


@role_required("ADMIN")
def asset_add(request):
    if request.method == "POST":
        category = get_object_or_404(
            Category,
            pk=request.POST.get("category")
        )

        branch = get_object_or_404(
            Branch,
            pk=request.POST.get("branch")
        )

        Asset.objects.create(
            asset_code=request.POST.get(
                "asset_code", ""
            ).strip(),
            name=request.POST.get(
                "name", ""
            ).strip(),
            category=category,
            branch=branch,
            owner=request.POST.get(
                "owner", ""
            ).strip(),
            condition=request.POST.get(
                "condition", "GOOD"
            ),
            status=request.POST.get(
                "status", "AVAILABLE"
            ),
            description=request.POST.get(
                "description", ""
            ).strip(),
        )

        messages.success(
            request,
            "Asset created successfully."
        )

        return redirect("assets")

    return render(
        request,
        "myapp/asset_form.html",
        {
            "categories": Category.objects.all(),
            "branches": Branch.objects.all(),
        }
    )


@role_required("ADMIN")
def asset_delete(request, asset_id):
    asset = get_object_or_404(
        Asset,
        pk=asset_id
    )

    if request.method == "POST":

        if Loan.objects.filter(
            asset=asset,
            status="ACTIVE"
        ).exists():

            messages.error(
                request,
                "This asset has an active loan and cannot be deleted."
            )

        else:
            asset.delete()

            messages.success(
                request,
                "Asset deleted successfully."
            )

        return redirect("assets")

    return render(
        request,
        "myapp/delete_asset.html",
        {
            "asset": asset
        }
    )


# --------------------------------------------------
# LOAN REQUESTS
# --------------------------------------------------

@login_required
def requests_page(request):
    if current_role(request.user) == "STAFF":

        request_list = LoanRequest.objects.filter(
            requested_by=request.user
        ).select_related(
            "asset",
            "requested_by"
        )

    else:
        request_list = LoanRequest.objects.all().select_related(
            "asset",
            "requested_by"
        )

    return render(
        request,
        "myapp/requests.html",
        {
            "requests": request_list
        }
    )


@role_required("STAFF")
def request_create(request):

    if request.method == "POST":

        asset = get_object_or_404(
            Asset,
            pk=request.POST.get("asset")
        )

        start_date = parse_date(
            request.POST.get("start_date", "")
        )

        end_date = parse_date(
            request.POST.get("end_date", "")
        )

        purpose = request.POST.get(
            "purpose", ""
        ).strip()

        if not start_date or not end_date or end_date < start_date:

            messages.error(
                request,
                "Please enter a valid date range."
            )

        elif asset.status != "AVAILABLE":

            messages.error(
                request,
                "This asset is not currently available."
            )

        elif Loan.objects.filter(
            asset=asset,
            status="ACTIVE",
            checkout_date__lte=end_date,
            due_date__gte=start_date
        ).exists():

            messages.error(
                request,
                "This asset is already booked for those dates."
            )

        elif LoanRequest.objects.filter(
            asset=asset,
            status="PENDING",
            start_date__lte=end_date,
            end_date__gte=start_date
        ).exists():

            messages.error(
                request,
                "There is already a pending request for those dates."
            )

        elif not purpose:

            messages.error(
                request,
                "Please enter the purpose of the request."
            )

        else:

            LoanRequest.objects.create(
                asset=asset,
                requested_by=request.user,
                start_date=start_date,
                end_date=end_date,
                purpose=purpose
            )

            messages.success(
                request,
                "Your asset request has been submitted."
            )

            return redirect("requests")

    return render(
        request,
        "myapp/request_form.html",
        {
            "assets": Asset.objects.filter(
                status="AVAILABLE"
            )
        }
    )


# --------------------------------------------------
# ADMIN APPROVALS
# --------------------------------------------------

@role_required("ADMIN")
@transaction.atomic
def approve_request(request, request_id):

    if request.method != "POST":
        return redirect("approvals")

    item = get_object_or_404(
        LoanRequest.objects.select_for_update(),
        pk=request_id
    )

    if item.status != "PENDING":
        messages.error(request, "This request has already been reviewed.")
        return redirect("approvals")

    asset = Asset.objects.select_for_update().get(
        pk=item.asset_id
    )

    if asset.status != "AVAILABLE":
        messages.error(request, "This asset is not available.")
        return redirect("approvals")

    if Loan.objects.filter(
        asset=asset,
        status="ACTIVE"
    ).exists():
        messages.error(request, "This asset has an active loan.")
        return redirect("approvals")

    item.status = "APPROVED"
    item.reviewed_by = request.user
    item.reviewed_at = timezone.now()
    item.save()

    # Do not create a Loan here.
    # The loan will be created after transfer receipt.

    messages.success(
        request,
        "Request approved. It is now ready for branch transfer."
    )

    return redirect("approvals")
@role_required("ADMIN")
def reject_request(request, request_id):

    item = get_object_or_404(
        LoanRequest,
        pk=request_id
    )

    if request.method == "POST" and item.status == "PENDING":

        item.status = "REJECTED"
        item.reviewed_by = request.user
        item.reviewed_at = timezone.now()
        item.save()

        messages.success(
            request,
            "Request rejected."
        )

    return redirect("approvals")


@role_required("ADMIN")
def approvals(request):

    pending = LoanRequest.objects.filter(
        status="PENDING"
    ).select_related(
        "asset",
        "requested_by"
    )

    return render(
        request,
        "myapp/approvals.html",
        {
            "requests": pending
        }
    )


# --------------------------------------------------
# BRANCH TRANSFERS
# --------------------------------------------------

@login_required
def transfers(request):

    transfer_list = BranchTransfer.objects.select_related(
        "asset",
        "from_branch",
        "to_branch",
        "recorded_by"
    ).all()

    return render(
        request,
        "myapp/transfers.html",
        {
            "transfers": transfer_list
        }
    )
@role_required("STAFF", "ADMIN")
@transaction.atomic
def transfer_create(request):

    approved_requests = LoanRequest.objects.filter(
        status="APPROVED",
        transfers__isnull=True
    ).select_related(
        "asset",
        "asset__branch",
        "requested_by",
        "requested_by__profile",
        "requested_by__profile__branch"
    ).order_by("-created_at")

    if request.method == "POST":

        request_id = request.POST.get("request_id")

        loan_request = get_object_or_404(
            LoanRequest.objects.select_for_update(),
            pk=request_id,
            status="APPROVED"
        )

        if loan_request.transfers.exists():
            messages.error(
                request,
                "A transfer already exists for this request."
            )
            return redirect("transfer_create")

        asset = Asset.objects.select_for_update().get(
            pk=loan_request.asset_id
        )

        profile = getattr(
            loan_request.requested_by,
            "profile",
            None
        )

        if not profile or not profile.branch_id:
            messages.error(
                request,
                "The requesting staff member has no assigned branch."
            )
            return redirect("transfer_create")

        from_branch = asset.branch
        to_branch = profile.branch

        if from_branch.id == to_branch.id:
            messages.error(
                request,
                "This asset already belongs to the requesting branch."
            )
            return redirect("transfer_create")

        if asset.status != "AVAILABLE":
            messages.error(
                request,
                "This asset is not available for transfer."
            )
            return redirect("transfer_create")

        if Loan.objects.filter(
            asset=asset,
            status="ACTIVE"
        ).exists():
            messages.error(
                request,
                "This asset has an active loan."
            )
            return redirect("transfer_create")

        BranchTransfer.objects.create(
            asset=asset,
            request=loan_request,
            from_branch=from_branch,
            to_branch=to_branch,
            sender=request.POST.get("sender", "").strip(),
            receiver=request.POST.get("receiver", "").strip(),
            recorded_by=request.user,
            notes=request.POST.get("notes", "").strip()
        )

        messages.success(
            request,
            "Approved request successfully added to transfers."
        )

        return redirect("transfers")

    return render(
        request,
        "myapp/transfer_form.html",
        {
            "approved_requests": approved_requests
        }
    )



# --------------------------------------------------
# ASSET RETURNS
# --------------------------------------------------

@login_required
def returns_page(request):

    role = current_role(request.user)

    active_loans = Loan.objects.filter(
        status="ACTIVE"
    ).select_related(
        "asset",
        "borrower"
    )

    if role == "STAFF":
        active_loans = active_loans.filter(
            borrower=request.user
        )

    completed_returns = AssetReturn.objects.select_related(
        "loan__asset",
        "received_by"
    )

    if role == "STAFF":
        completed_returns = completed_returns.filter(
            loan__borrower=request.user
        )

    return render(
        request,
        "myapp/returns.html",
        {
            "loans": active_loans,
            "completed_returns": completed_returns,
        }
    )


@login_required
@transaction.atomic
def mark_return(request, loan_id):

    loan = get_object_or_404(
        Loan.objects.select_for_update(),
        pk=loan_id
    )

    role = current_role(request.user)

    if request.method == "POST" and loan.status == "ACTIVE":

        if role == "STAFF" and loan.borrower_id != request.user.id:

            messages.error(
                request,
                "You can only return your own loan."
            )

            return redirect("returns")

        if role not in ("STAFF", "ADMIN"):

            messages.error(
                request,
                "You do not have permission to record returns."
            )

            return redirect("returns")

        condition = request.POST.get(
            "return_condition",
            "GOOD"
        )

        valid_conditions = dict(
            Asset.CONDITION_CHOICES
        )

        if condition not in valid_conditions:
            condition = "GOOD"

        AssetReturn.objects.create(
            loan=loan,
            received_by=request.user,
            return_condition=condition,
            notes=request.POST.get(
                "notes", ""
            ).strip()
        )

        loan.status = "RETURNED"
        loan.returned_at = timezone.now()

        loan.save(
            update_fields=["status", "returned_at"]
        )

        loan.asset.condition = condition

        loan.asset.status = (
            "MAINTENANCE"
            if condition in (
                "DAMAGED",
                "UNDER_MAINTENANCE"
            )
            else "AVAILABLE"
        )

        loan.asset.save(
            update_fields=["condition", "status"]
        )

        messages.success(
            request,
            "Asset return recorded successfully."
        )

    return redirect("returns")


# --------------------------------------------------
# BRANCH MANAGEMENT
# --------------------------------------------------

@role_required("ADMIN")
def branches(request):

    if request.method == "POST":

        name = request.POST.get(
            "name", ""
        ).strip()

        code = request.POST.get(
            "branch_code", ""
        ).strip()

        location = request.POST.get(
            "location", ""
        ).strip()

        if name and code and location:

            Branch.objects.create(
                name=name,
                branch_code=code,
                location=location
            )

            messages.success(
                request,
                "Branch created successfully."
            )

            return redirect("branches")

        messages.error(
            request,
            "Please fill in all branch fields."
        )

    return render(
        request,
        "myapp/branches.html",
        {
            "branches": Branch.objects.all()
        }
    )


#--------------------------------------------------
# MANAGER REPORTS
# --------------------------------------------------

@role_required("MANAGER", "ADMIN")
def reports(request):

    branch_reports = []

    for branch in Branch.objects.all():

        branch_assets = Asset.objects.filter(
            branch=branch
        )

        branch_reports.append({
            "name": branch.name,

            "total_assets": branch_assets.count(),

            "available_assets": branch_assets.filter(
                status="AVAILABLE"
            ).count(),

            "active_loans": Loan.objects.filter(
                branch=branch,
                status="ACTIVE"
            ).count(),
        })

    context = {
        "total_assets": Asset.objects.count(),

        "available_assets": Asset.objects.filter(
            status="AVAILABLE"
        ).count(),

        "borrowed_assets": Asset.objects.filter(
            status="BORROWED"
        ).count(),

        "overdue_assets": Loan.objects.filter(
            status="ACTIVE",
            due_date__lt=timezone.localdate()
        ).count(),

        "branch_reports": branch_reports,
    }

    return render(
        request,
        "myapp/reports.html",
        context
    )
@login_required
def asset_detail(request, asset_id):
    asset = get_object_or_404(
        Asset,
        pk=asset_id
    )

    return render(
        request,
        "myapp/asset_detail.html",
        {
            "asset": asset
        }
    )


@role_required("ADMIN")
def asset_add(request):
    if request.method == "POST":
        category = get_object_or_404(
            Category,
            pk=request.POST.get("category")
        )

        branch = get_object_or_404(
            Branch,
            pk=request.POST.get("branch")
        )

        Asset.objects.create(
            asset_code=request.POST.get(
                "asset_code", ""
            ).strip(),
            name=request.POST.get(
                "name", ""
            ).strip(),
            category=category,
            branch=branch,
            owner=request.POST.get(
                "owner", ""
            ).strip(),
            condition=request.POST.get(
                "condition", "GOOD"
            ),
            status=request.POST.get(
                "status", "AVAILABLE"
            ),
            description=request.POST.get(
                "description", ""
            ).strip(),
        )

        messages.success(
            request,
            "Asset created successfully."
        )

        return redirect("assets")

    return render(
        request,
        "myapp/asset_form.html",
        {
            "categories": Category.objects.all(),
            "branches": Branch.objects.all(),
        }
    )


@role_required("ADMIN")
def asset_delete(request, asset_id):
    asset = get_object_or_404(
        Asset,
        pk=asset_id
    )

    if request.method == "POST":

        if Loan.objects.filter(
            asset=asset,
            status="ACTIVE"
        ).exists():

            messages.error(
                request,
                "This asset has an active loan and cannot be deleted."
            )

        else:
            asset.delete()

            messages.success(
                request,
                "Asset deleted successfully."
            )

        return redirect("assets")

    return render(
        request,
        "myapp/delete_asset.html",
        {
            "asset": asset
        }
    )


# --------------------------------------------------
# LOAN REQUESTS
# --------------------------------------------------

@login_required
def requests_page(request):
    if current_role(request.user) == "STAFF":

        request_list = LoanRequest.objects.filter(
            requested_by=request.user
        ).select_related(
            "asset",
            "requested_by"
        )

    else:
        request_list = LoanRequest.objects.all().select_related(
            "asset",
            "requested_by"
        )

    return render(
        request,
        "myapp/requests.html",
        {
            "requests": request_list
        }
    )


@role_required("STAFF")
def request_create(request):

    if request.method == "POST":

        asset = get_object_or_404(
            Asset,
            pk=request.POST.get("asset")
        )

        start_date = parse_date(
            request.POST.get("start_date", "")
        )

        end_date = parse_date(
            request.POST.get("end_date", "")
        )

        purpose = request.POST.get(
            "purpose", ""
        ).strip()

        if not start_date or not end_date or end_date < start_date:

            messages.error(
                request,
                "Please enter a valid date range."
            )

        elif asset.status != "AVAILABLE":

            messages.error(
                request,
                "This asset is not currently available."
            )

        elif Loan.objects.filter(
            asset=asset,
            status="ACTIVE",
            checkout_date__lte=end_date,
            due_date__gte=start_date
        ).exists():

            messages.error(
                request,
                "This asset is already booked for those dates."
            )

        elif LoanRequest.objects.filter(
            asset=asset,
            status="PENDING",
            start_date__lte=end_date,
            end_date__gte=start_date
        ).exists():

            messages.error(
                request,
                "There is already a pending request for those dates."
            )

        elif not purpose:

            messages.error(
                request,
                "Please enter the purpose of the request."
            )

        else:

            LoanRequest.objects.create(
                asset=asset,
                requested_by=request.user,
                start_date=start_date,
                end_date=end_date,
                purpose=purpose
            )

            messages.success(
                request,
                "Your asset request has been submitted."
            )

            return redirect("requests")

    return render(
        request,
        "myapp/request_form.html",
        {
            "assets": Asset.objects.filter(
                status="AVAILABLE"
            )
        }
    )


# --------------------------------------------------
# ADMIN APPROVALS
# --------------------------------------------------

@role_required("ADMIN")
@transaction.atomic
def approve_request(request, request_id):

    item = get_object_or_404(
        LoanRequest.objects.select_for_update(),
        pk=request_id
    )

    if request.method == "POST" and item.status == "PENDING":

        asset = Asset.objects.select_for_update().get(
            pk=item.asset_id
        )

        conflict = Loan.objects.filter(
            asset=asset,
            status="ACTIVE",
            checkout_date__lte=item.end_date,
            due_date__gte=item.start_date
        ).exists()

        if conflict:

            messages.error(
                request,
                "The asset is already booked for those dates."
            )

        else:

            item.status = "APPROVED"
            item.reviewed_by = request.user
            item.reviewed_at = timezone.now()
            item.save()

            Loan.objects.create(
                request=item,
                asset=asset,
                borrower=item.requested_by,
                branch=asset.branch,
                checkout_date=item.start_date,
                due_date=item.end_date
            )

            asset.status = "BORROWED"

            asset.save(
                update_fields=["status"]
            )

            messages.success(
                request,
                "Request approved and loan recorded."
            )

    return redirect("approvals")


@role_required("ADMIN")
def reject_request(request, request_id):

    item = get_object_or_404(
        LoanRequest,
        pk=request_id
    )

    if request.method == "POST" and item.status == "PENDING":

        item.status = "REJECTED"
        item.reviewed_by = request.user
        item.reviewed_at = timezone.now()
        item.save()

        messages.success(
            request,
            "Request rejected."
        )

    return redirect("approvals")


@role_required("ADMIN")
def approvals(request):

    pending = LoanRequest.objects.filter(
        status="PENDING"
    ).select_related(
        "asset",
        "requested_by"
    )

    return render(
        request,
        "myapp/approvals.html",
        {
            "requests": pending
        }
    )


# --------------------------------------------------
# BRANCH TRANSFERS
# --------------------------------------------------

@login_required
def transfers(request):

    transfer_list = BranchTransfer.objects.select_related(
        "asset",
        "from_branch",
        "to_branch",
        "recorded_by"
    ).all()

    return render(
        request,
        "myapp/transfers.html",
        {
            "transfers": transfer_list
        }
    )

@role_required("STAFF", "ADMIN")
@transaction.atomic
def transfer_create(request):

    approved_requests = LoanRequest.objects.filter(
        status="APPROVED",
        transfers__isnull=True
    ).select_related(
        "asset",
        "asset__branch",
        "requested_by",
        "requested_by__profile",
        "requested_by__profile__branch"
    ).order_by("-created_at")

    if request.method == "POST":

        request_id = request.POST.get("request_id")

        loan_request = get_object_or_404(
            LoanRequest.objects.select_for_update(),
            pk=request_id,
            status="APPROVED"
        )

        if loan_request.transfers.exists():
            messages.error(
                request,
                "A transfer already exists for this request."
            )
            return redirect("transfer_create")

        asset = Asset.objects.select_for_update().get(
            pk=loan_request.asset_id
        )

        profile = getattr(
            loan_request.requested_by,
            "profile",
            None
        )

        if not profile or not profile.branch_id:
            messages.error(
                request,
                "The requesting staff member has no assigned branch."
            )
            return redirect("transfer_create")

        from_branch = asset.branch
        to_branch = profile.branch

        if from_branch.id == to_branch.id:
            messages.error(
                request,
                "This asset already belongs to the requesting branch."
            )
            return redirect("transfer_create")

        if asset.status != "AVAILABLE":
            messages.error(
                request,
                "This asset is not available for transfer."
            )
            return redirect("transfer_create")

        if Loan.objects.filter(
            asset=asset,
            status="ACTIVE"
        ).exists():
            messages.error(
                request,
                "This asset has an active loan."
            )
            return redirect("transfer_create")

        BranchTransfer.objects.create(
            asset=asset,
            request=loan_request,
            from_branch=from_branch,
            to_branch=to_branch,
            sender=request.POST.get("sender", "").strip(),
            receiver=request.POST.get("receiver", "").strip(),
            recorded_by=request.user,
            notes=request.POST.get("notes", "").strip()
        )

        messages.success(
            request,
            "Approved request successfully added to transfers."
        )

        return redirect("transfers")

    return render(
        request,
        "myapp/transfer_form.html",
        {
            "approved_requests": approved_requests
        }
    )



# --------------------------------------------------
# ASSET RETURNS
# --------------------------------------------------

@login_required
def returns_page(request):

    role = current_role(request.user)

    active_loans = Loan.objects.filter(
        status="ACTIVE"
    ).select_related(
        "asset",
        "borrower"
    )

    if role == "STAFF":
        active_loans = active_loans.filter(
            borrower=request.user
        )

    completed_returns = AssetReturn.objects.select_related(
        "loan__asset",
        "received_by"
    )

    if role == "STAFF":
        completed_returns = completed_returns.filter(
            loan__borrower=request.user
        )

    return render(
        request,
        "myapp/returns.html",
        {
            "loans": active_loans,
            "completed_returns": completed_returns,
        }
    )

@login_required
def mark_return(request, loan_id):
    loan = get_object_or_404(
        Loan.objects.select_related(
            "asset", "borrower", "branch"
        ),
        pk=loan_id
    )

    role = current_role(request.user)

    if role == "STAFF" and loan.borrower_id != request.user.id:
        messages.error(request, "You can only return your own loan.")
        return redirect("returns")

    if role not in ("STAFF", "ADMIN"):
        messages.error(request, "You do not have permission to record returns.")
        return redirect("returns")

    if loan.status != "ACTIVE":
        messages.error(request, "This loan has already been returned.")
        return redirect("returns")

    if request.method == "POST":
        condition = request.POST.get("return_condition", "")
        notes = request.POST.get("notes", "").strip()

        valid_conditions = dict(Asset.CONDITION_CHOICES)

        if condition not in valid_conditions:
            messages.error(request, "Please select a valid return condition.")
            return redirect("mark_return", loan_id=loan.id)

        with transaction.atomic():
            loan = get_object_or_404(
                Loan.objects.select_for_update(),
                pk=loan_id
            )

            if loan.status != "ACTIVE":
                messages.error(request, "This loan has already been returned.")
                return redirect("returns")

            AssetReturn.objects.create(
                loan=loan,
                received_by=request.user,
                return_condition=condition,
                notes=notes
            )

            loan.status = "RETURNED"
            loan.returned_at = timezone.now()
            loan.save(update_fields=["status", "returned_at"])

            loan.asset.condition = condition

            if condition in ("DAMAGED", "UNDER_MAINTENANCE"):
                loan.asset.status = "MAINTENANCE"
            else:
                loan.asset.status = "AVAILABLE"

            loan.asset.save(update_fields=["condition", "status"])

        messages.success(request, "Asset return recorded successfully.")
        return redirect("returns")

    return render(
        request,
        "myapp/return_form.html",
        {"loan": loan}
    )


# --------------------------------------------------
# BRANCH MANAGEMENT
# --------------------------------------------------

@role_required("ADMIN")
def branches(request):

    if request.method == "POST":

        name = request.POST.get(
            "name", ""
        ).strip()

        code = request.POST.get(
            "branch_code", ""
        ).strip()

        location = request.POST.get(
            "location", ""
        ).strip()

        if name and code and location:

            Branch.objects.create(
                name=name,
                branch_code=code,
                location=location
            )

            messages.success(
                request,
                "Branch created successfully."
            )

            return redirect("branches")

        messages.error(
            request,
            "Please fill in all branch fields."
        )

    return render(
        request,
        "myapp/branches.html",
        {
            "branches": Branch.objects.all()
        }
    )


#--------------------------------------------------
# MANAGER REPORTS
# --------------------------------------------------

@role_required("MANAGER", "ADMIN")
def reports(request):

    branch_reports = []

    for branch in Branch.objects.all():

        branch_assets = Asset.objects.filter(
            branch=branch
        )

        branch_reports.append({
            "name": branch.name,

            "total_assets": branch_assets.count(),

            "available_assets": branch_assets.filter(
                status="AVAILABLE"
            ).count(),

            "active_loans": Loan.objects.filter(
                branch=branch,
                status="ACTIVE"
            ).count(),
        })

    context = {
        "total_assets": Asset.objects.count(),

        "available_assets": Asset.objects.filter(
            status="AVAILABLE"
        ).count(),

        "borrowed_assets": Asset.objects.filter(
            status="BORROWED"
        ).count(),

        "overdue_assets": Loan.objects.filter(
            status="ACTIVE",
            due_date__lt=timezone.localdate()
        ).count(),

        "branch_reports": branch_reports,
    }

    return render(
        request,
        "myapp/reports.html",
        context
    )



@role_required("STAFF", "ADMIN")
@transaction.atomic
def dispatch_transfer(request, transfer_id):

    if request.method != "POST":
        return redirect("transfers")

    transfer = get_object_or_404(
        BranchTransfer.objects.select_for_update(),
        pk=transfer_id
    )

    if current_role(request.user) == "STAFF":
        profile = getattr(request.user, "profile", None)

        if not profile or profile.branch_id != transfer.from_branch_id:
            messages.error(request, "You cannot dispatch this transfer.")
            return redirect("transfers")

    if transfer.status != "PENDING":
        messages.error(request, "This transfer cannot be dispatched.")
        return redirect("transfers")

    asset = Asset.objects.select_for_update().get(
        pk=transfer.asset_id
    )

    if asset.branch_id != transfer.from_branch_id:
        messages.error(request, "The asset's current branch has changed.")
        return redirect("transfers")

    if asset.status != "AVAILABLE":
        messages.error(request, "The asset is not available.")
        return redirect("transfers")

    asset.status = "IN_TRANSFER"
    asset.save(update_fields=["status"])

    transfer.status = "IN_TRANSIT"
    transfer.handoff_time = timezone.now()
    transfer.save(update_fields=["status", "handoff_time"])

    messages.success(request, "Asset dispatched. GPS tracking is now available.")

    return redirect("transfers")
@role_required("STAFF", "ADMIN")
@transaction.atomic
def dispatch_transfer(request, transfer_id):

    if request.method != "POST":
        return redirect("transfers")

    transfer = get_object_or_404(
        BranchTransfer.objects.select_for_update(),
        pk=transfer_id
    )

    if current_role(request.user) == "STAFF":
        profile = getattr(request.user, "profile", None)

        if not profile or profile.branch_id != transfer.from_branch_id:
            messages.error(request, "You cannot dispatch this transfer.")
            return redirect("transfers")

    if transfer.status != "PENDING":
        messages.error(request, "This transfer cannot be dispatched.")
        return redirect("transfers")

    asset = Asset.objects.select_for_update().get(
        pk=transfer.asset_id
    )

    if asset.branch_id != transfer.from_branch_id:
        messages.error(request, "The asset's current branch has changed.")
        return redirect("transfers")

    if asset.status != "AVAILABLE":
        messages.error(request, "The asset is not available.")
        return redirect("transfers")

    asset.status = "IN_TRANSFER"
    asset.save(update_fields=["status"])

    transfer.status = "IN_TRANSIT"
    transfer.handoff_time = timezone.now()
    transfer.save(update_fields=["status", "handoff_time"])

    messages.success(request, "Asset dispatched. GPS tracking is now available.")

    return redirect("transfers")

@role_required("STAFF", "ADMIN")
@transaction.atomic
def receive_transfer(request, transfer_id):

    if request.method != "POST":
        return redirect("transfers")

    transfer = get_object_or_404(
        BranchTransfer.objects.select_for_update(),
        pk=transfer_id
    )

    # Only receiving branch staff or Admin can receive.
    if current_role(request.user) == "STAFF":
        profile = getattr(request.user, "profile", None)

        if not profile or profile.branch_id != transfer.to_branch_id:
            messages.error(
                request,
                "You cannot receive this transfer."
            )
            return redirect("transfers")

    if transfer.status != "IN_TRANSIT":
        messages.error(
            request,
            "This transfer is not in transit."
        )
        return redirect("transfers")

    asset = Asset.objects.select_for_update().get(
        pk=transfer.asset_id
    )

    if asset.status != "IN_TRANSFER":
        messages.error(
            request,
            "Asset is not marked as in transfer."
        )
        return redirect("transfers")

    # Check whether this request already has an active loan.
    if transfer.request_id:
        existing_loan = Loan.objects.filter(
            request_id=transfer.request_id,
            status="ACTIVE"
        ).exists()

        if existing_loan:
            messages.error(
                request,
                "An active loan already exists for this request. "
                "Please review the loan before receiving the asset."
            )
            return redirect("transfers")

    # Confirm receipt and move the asset.
    asset.branch = transfer.to_branch
    asset.status = "AVAILABLE"
    asset.save(update_fields=["branch", "status"])

    transfer.status = "RECEIVED"
    transfer.received_at = timezone.now()
    transfer.save(update_fields=["status", "received_at"])

    messages.success(
        request,
        "Asset received successfully. "
        "It is now available at the receiving branch."
    )

    return redirect("transfers")

@role_required("STAFF", "ADMIN", "MANAGER")
def gps_tracking(request, transfer_id):
    transfer = get_object_or_404(
        BranchTransfer.objects.select_related(
            "asset",
            "from_branch",
            "to_branch"
        ),
        pk=transfer_id
    )

    if current_role(request.user) == "STAFF":
        profile = getattr(request.user, "profile", None)

        if not profile or profile.branch_id not in (
            transfer.from_branch_id,
            transfer.to_branch_id
        ):
            messages.error(request, "You cannot view this transfer.")
            return redirect("transfers")

    return render(
        request,
        "myapp/gps_tracking.html",
        {"transfer": transfer}
    )

@role_required("STAFF", "ADMIN", "MANAGER")
def latest_transfer_location(request, transfer_id):
    from django.http import JsonResponse

    transfer = get_object_or_404(
        BranchTransfer,
        pk=transfer_id
    )

    if current_role(request.user) == "STAFF":
        profile = getattr(request.user, "profile", None)

        if not profile or profile.branch_id not in (
            transfer.from_branch_id,
            transfer.to_branch_id
        ):
            return JsonResponse(
                {"error": "You are not authorized."},
                status=403
            )

    latest = transfer.location_updates.order_by(
        "-recorded_at"
    ).first()

    if latest is None:
        return JsonResponse({"location": None})

    return JsonResponse({
        "location": {
            "latitude": float(latest.latitude),
            "longitude": float(latest.longitude),
            "accuracy": (
                float(latest.accuracy)
                if latest.accuracy is not None
                else None
            ),
            "recorded_at": latest.recorded_at.isoformat(),
            "shared_by": latest.shared_by.username
        }
    })

@role_required("STAFF", "ADMIN")
def update_transfer_location(request, transfer_id):
    from decimal import Decimal, InvalidOperation
    from django.http import JsonResponse

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST method required."},
            status=405
        )

    transfer = get_object_or_404(
        BranchTransfer,
        pk=transfer_id
    )

    if transfer.status != "IN_TRANSIT":
        return JsonResponse(
            {"error": "Transfer is not active."},
            status=400
        )

    if current_role(request.user) == "STAFF":
        profile = getattr(request.user, "profile", None)

        if not profile or profile.branch_id not in (
            transfer.from_branch_id,
            transfer.to_branch_id
        ):
            return JsonResponse(
                {"error": "Not authorized."},
                status=403
            )

    try:
        latitude = Decimal(request.POST.get("latitude", ""))
        longitude = Decimal(request.POST.get("longitude", ""))

        if (
            not latitude.is_finite()
            or not longitude.is_finite()
            or latitude < -90
            or latitude > 90
            or longitude < -180
            or longitude > 180
        ):
            raise ValueError

        accuracy_text = request.POST.get("accuracy", "")
        accuracy = Decimal(accuracy_text) if accuracy_text else None

        if accuracy is not None and (
            not accuracy.is_finite() or accuracy < 0
        ):
            raise ValueError

    except (InvalidOperation, ValueError):
        return JsonResponse(
            {"error": "Invalid GPS coordinates."},
            status=400
        )

    TransferLocation.objects.create(
        transfer=transfer,
        shared_by=request.user,
        latitude=latitude,
        longitude=longitude,
        accuracy=accuracy
    )

    return JsonResponse({
        "message": "GPS location saved successfully."
    })

@role_required("ADMIN", "MANAGER", "STAFF")
def branch_map(request):
    branches_list = Branch.objects.exclude(
        latitude__isnull=True
    ).exclude(
        longitude__isnull=True
    ).order_by("name")

    if current_role(request.user) == "STAFF":
        profile = getattr(request.user, "profile", None)

        if not profile:
            messages.error(request, "Your branch profile is missing.")
            return redirect("dashboard")

    return render(
        request,
        "myapp/branch_map.html",
        {
            "branches": branches_list
        }
    )