from django.urls import path
from . import views
from . import manager_views

urlpatterns = [

    # LOGIN AND REGISTRATION
    path("", views.dashboard, name="dashboard"),
    path("login/", views.login_page, name="login"),
    path("logout/", views.logout_page, name="logout"),
    path("register/", views.register_page, name="register"),

    # ASSET MANAGEMENT
    path("assets/", views.assets, name="assets"),
    path("assets/add/", views.asset_add, name="asset_add"),
    path(
        "assets/<int:asset_id>/",
        views.asset_detail,
        name="asset_detail"
    ),
    path(
        "assets/delete/<int:asset_id>/",
        views.asset_delete,
        name="asset_delete"
    ),

    # REQUESTS AND APPROVALS
    path("requests/", views.requests_page, name="requests"),
    path(
        "requests/create/",
        views.request_create,
        name="request_create"
    ),
    path("approvals/", views.approvals, name="approvals"),
    path(
        "requests/<int:request_id>/approve/",
        views.approve_request,
        name="approve_request"
    ),
    path(
        "requests/<int:request_id>/reject/",
        views.reject_request,
        name="reject_request"
    ),

    # BRANCH TRANSFERS
    path("transfers/", views.transfers, name="transfers"),
    path(
        "transfers/create/",
        views.transfer_create,
        name="transfer_create"
    ),
    path(
        "transfers/<int:transfer_id>/dispatch/",
        views.dispatch_transfer,
        name="dispatch_transfer"
    ),
    path(
        "transfers/<int:transfer_id>/receive/",
        views.receive_transfer,
        name="receive_transfer"
    ),

    # GPS TRACKING
    path(
        "transfers/<int:transfer_id>/gps/",
        views.gps_tracking,
        name="gps_tracking"
    ),
    path(
        "transfers/<int:transfer_id>/gps/update/",
        views.update_transfer_location,
        name="update_transfer_location"
    ),
    path(
        "transfers/<int:transfer_id>/gps/latest/",
        views.latest_transfer_location,
        name="latest_transfer_location"
    ),
    path(
        "branch-map/",
        views.branch_map,
        name="branch_map"
    ),

    # RETURNS
    path("returns/", views.returns_page, name="returns"),
    path(
        "returns/<int:loan_id>/mark/",
        views.mark_return,
        name="mark_return"
    ),

    # BRANCHES AND REPORTS
    path("branches/", views.branches, name="branches"),
    path("reports/", views.reports, name="reports"),

    # MANAGER FEATURES
    path(
        "manager/branch-monitoring/",
        manager_views.branch_monitoring,
        name="branch_monitoring"
    ),
    path(
        "manager/overdue-tracking/",
        manager_views.overdue_tracking,
        name="overdue_tracking"
    ),
]