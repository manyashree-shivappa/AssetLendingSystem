from django.conf import settings
from django.db import models
from django.utils import timezone


# --------------------------------------------------
# BRANCHES
# --------------------------------------------------

class Branch(models.Model):
    name = models.CharField(max_length=100)
    branch_code = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=200)

    # GPS coordinates are entered by Admin.
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


# --------------------------------------------------
# CATEGORIES
# --------------------------------------------------

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# --------------------------------------------------
# USER PROFILES AND ROLES
# --------------------------------------------------

class UserProfile(models.Model):

    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("MANAGER", "Manager"),
        ("STAFF", "Branch Staff"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="STAFF"
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# --------------------------------------------------
# ASSETS
# --------------------------------------------------

class Asset(models.Model):

    STATUS_CHOICES = [
        ("AVAILABLE", "Available"),
        ("BORROWED", "Borrowed"),
        ("IN_TRANSFER", "In Transfer"),
        ("MAINTENANCE", "Maintenance"),
    ]

    CONDITION_CHOICES = [
        ("NEW", "New"),
        ("GOOD", "Good"),
        ("DAMAGED", "Damaged"),
        ("UNDER_MAINTENANCE", "Under Maintenance"),
    ]

    asset_code = models.CharField(
        max_length=30,
        unique=True
    )

    name = models.CharField(max_length=150)

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT
    )

    owner = models.CharField(
        max_length=150,
        blank=True
    )

    condition = models.CharField(
        max_length=25,
        choices=CONDITION_CHOICES,
        default="GOOD"
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="AVAILABLE"
    )

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.asset_code} - {self.name}"


# --------------------------------------------------
# LOAN REQUESTS
# --------------------------------------------------

class LoanRequest(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    asset = models.ForeignKey(
        Asset,
        on_delete=models.PROTECT
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="asset_requests"
    )

    start_date = models.DateField()
    end_date = models.DateField()

    purpose = models.TextField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_requests"
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request #{self.pk} - {self.asset}"


# --------------------------------------------------
# ACTIVE LOANS
# --------------------------------------------------

class Loan(models.Model):

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("RETURNED", "Returned"),
    ]

    request = models.OneToOneField(
        LoanRequest,
        on_delete=models.PROTECT,
        related_name="loan"
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.PROTECT,
        related_name="loans"
    )

    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT
    )

    checkout_date = models.DateField(
        default=timezone.localdate
    )

    due_date = models.DateField()

    returned_at = models.DateTimeField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="ACTIVE"
    )

    @property
    def is_overdue(self):
        return (
            self.status == "ACTIVE"
            and self.due_date < timezone.localdate()
        )

    def __str__(self):
        return f"{self.asset} - {self.borrower}"


# --------------------------------------------------
# BRANCH TRANSFERS
# --------------------------------------------------

class BranchTransfer(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending Dispatch"),
        ("IN_TRANSIT", "In Transit"),
        ("RECEIVED", "Received"),
    ]

    asset = models.ForeignKey(
        Asset,
        on_delete=models.PROTECT
    )

    request = models.ForeignKey(
        LoanRequest,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="transfers"
    )

    from_branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="outgoing_transfers"
    )

    to_branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="incoming_transfers"
    )

    sender = models.CharField(max_length=120)

    receiver = models.CharField(max_length=120)

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    handoff_time = models.DateTimeField(
        default=timezone.now
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    received_at = models.DateTimeField(
        null=True,
        blank=True
    )

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.asset} - {self.status}"


# --------------------------------------------------
# GPS LOCATION HISTORY
# --------------------------------------------------

class TransferLocation(models.Model):

    transfer = models.ForeignKey(
        BranchTransfer,
        on_delete=models.CASCADE,
        related_name="location_updates"
    )

    shared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    accuracy = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    recorded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Transfer {self.transfer_id} - {self.recorded_at}"


# --------------------------------------------------
# ASSET RETURNS
# --------------------------------------------------

class AssetReturn(models.Model):

    loan = models.OneToOneField(
        Loan,
        on_delete=models.PROTECT,
        related_name="asset_return"
    )

    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    return_condition = models.CharField(
        max_length=25,
        choices=Asset.CONDITION_CHOICES,
        default="GOOD"
    )

    notes = models.TextField(blank=True)

    returned_at = models.DateTimeField(
        default=timezone.now
    )

    def __str__(self):
        return f"Return - {self.loan.asset}"