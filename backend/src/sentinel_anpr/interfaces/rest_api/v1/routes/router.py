"""API v1 route aggregation."""

from fastapi import APIRouter

from sentinel_anpr.interfaces.rest_api.v1.routes.auth.auth_handler import router as auth_router
from sentinel_anpr.interfaces.rest_api.v1.routes.vehicles.vehicle_handler import (
    router as vehicle_router,
)
from sentinel_anpr.interfaces.rest_api.v1.routes.uploads.upload_handler import (
    router as upload_router,
)
from sentinel_anpr.interfaces.rest_api.v1.routes.dashboard.dashboard_handler import (
    router as dashboard_router,
)
from sentinel_anpr.interfaces.rest_api.v1.routes.history.history_handler import (
    router as history_router,
)
from sentinel_anpr.interfaces.rest_api.v1.routes.workflow.workflow_handler import (
    router as workflow_router,
)
from sentinel_anpr.interfaces.rest_api.v1.routes.analytics.analytics_handler import (
    router as analytics_router,
)
from sentinel_anpr.interfaces.rest_api.v1.routes.reports.report_handler import (
    router as reports_router,
)
from sentinel_anpr.interfaces.rest_api.v1.routes.investigation_reports.investigation_reports_handler import (
    router as investigation_reports_router,
)
from sentinel_anpr.interfaces.rest_api.v1.routes.users.user_management_handler import (
    router as users_router,
)
from sentinel_anpr.interfaces.rest_api.v1.routes.stations.station_management_handler import (
    router as stations_router,
)
from sentinel_anpr.interfaces.rest_api.v1.routes.station_admin.station_admin_handler import (
    router as station_admin_router,
)
from sentinel_anpr.interfaces.rest_api.v1.routes.police_officer.police_officer_handler import (
    router as police_officer_router,
)
from sentinel_anpr.interfaces.rest_api.v1.routes.challans.challan_handler import (
    router as challans_router,
)
from sentinel_anpr.interfaces.rest_api.v1.routes.blockchain.blockchain_handler import (
    router as blockchain_router,
)
from sentinel_anpr.interfaces.rest_api.v1.routes.health.health_handler import router as health_router

api_v1_router = APIRouter(prefix="/v1")
api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(upload_router)
api_v1_router.include_router(vehicle_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(history_router)
api_v1_router.include_router(reports_router)
api_v1_router.include_router(investigation_reports_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(stations_router)
api_v1_router.include_router(station_admin_router)
api_v1_router.include_router(police_officer_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(workflow_router)
api_v1_router.include_router(blockchain_router)
api_v1_router.include_router(challans_router)
