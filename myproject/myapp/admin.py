from django.contrib import admin
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


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "branch_code",
        "location",
        "latitude",
        "longitude",
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "branch")
    list_filter = ("role", "branch")


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        "asset_code",
        "name",
        "category",
        "branch",
        "condition",
        "status",
    )
    list_filter = ("status", "branch", "category")


@admin.register(LoanRequest)
class LoanRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "asset",
        "requested_by",
        "start_date",
        "end_date",
        "status",
    )
    list_filter = ("status",)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
        "asset",
        "borrower",
        "branch",
        "checkout_date",
        "due_date",
        "status",
    )
    list_filter = ("status",)


@admin.register(BranchTransfer)
class BranchTransferAdmin(admin.ModelAdmin):
    list_display = (
        "asset",
        "from_branch",
        "to_branch",
        "sender",
        "receiver",
        "status",
        "handoff_time",
        "received_at",
    )
    list_filter = ("status", "from_branch", "to_branch")


@admin.register(TransferLocation)
class TransferLocationAdmin(admin.ModelAdmin):
    list_display = (
        "transfer",
        "shared_by",
        "latitude",
        "longitude",
        "accuracy",
        "recorded_at",
    )
    list_filter = ("shared_by",)


@admin.register(AssetReturn)
class AssetReturnAdmin(admin.ModelAdmin):
    list_display = (
        "loan",
        "received_by",
        "return_condition",
        "returned_at",
    )