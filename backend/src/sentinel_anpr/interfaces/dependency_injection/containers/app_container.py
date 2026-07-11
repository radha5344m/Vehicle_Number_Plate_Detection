"""Dependency injection container placeholder."""

from dataclasses import dataclass

from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from sentinel_anpr.application.ports.outbound.config_port import ConfigPort
from sentinel_anpr.application.ports.outbound.database_port import DatabasePort
from sentinel_anpr.application.ports.outbound.logging_port import LoggingPort
from sentinel_anpr.application.ports.outbound.token_provider_port import TokenProviderPort
from sentinel_anpr.application.ports.vision_ai_service import VisionAiService
from sentinel_anpr.application.use_cases.authentication.get_current_officer_use_case import (
    GetCurrentOfficerUseCase,
)
from sentinel_anpr.application.use_cases.authentication.login_use_case import LoginUseCase
from sentinel_anpr.application.use_cases.authentication.logout_use_case import LogoutUseCase
from sentinel_anpr.application.use_cases.authentication.user_management_use_cases import (
    ChangeUserStatusUseCase,
    CreateUserUseCase,
    QueryUsersUseCase,
    ResetStationAdminPasswordUseCase,
    ResetUserPasswordUseCase,
    SoftDeleteUserUseCase,
    UpdateUserUseCase,
)
from sentinel_anpr.application.use_cases.authentication.station_management_use_cases import (
    ChangeStationStatusUseCase,
    CreateStationUseCase,
    DeleteStationUseCase,
    GetStationUseCase,
    QueryStationsUseCase,
    UpdateStationUseCase,
)
from sentinel_anpr.application.use_cases.authentication.station_admin_portal_use_cases import (
    ChangeStationAdminPasswordUseCase,
    ChangeStationOfficerStatusUseCase,
    CreateStationOfficerUseCase,
    GetStationAdminDashboardUseCase,
    GetStationAdminProfileUseCase,
    GetStationAnalyticsUseCase,
    GetStationNotificationsUseCase,
    QueryStationOfficersUseCase,
    ResetStationOfficerPasswordUseCase,
    SoftDeleteStationOfficerUseCase,
    StationAdminPortalContext,
    UpdateStationAdminProfileUseCase,
    UpdateStationDetailsUseCase,
    UpdateStationOfficerUseCase,
)
from sentinel_anpr.application.use_cases.blockchain.anchor_evidence_block_use_case import (
    AnchorEvidenceBlockUseCase,
)
from sentinel_anpr.application.use_cases.blockchain.verify_investigation_integrity_use_case import (
    VerifyInvestigationIntegrityUseCase,
)
from sentinel_anpr.application.use_cases.chat.send_chat_message_use_case import (
    SendChatMessageUseCase,
)
from sentinel_anpr.application.use_cases.authentication.police_officer_portal_use_cases import (
    ChangePoliceOfficerPasswordUseCase,
    GetPoliceOfficerDashboardUseCase,
    GetPoliceOfficerNotificationsUseCase,
    GetPoliceOfficerProfileUseCase,
    UpdatePoliceOfficerProfileUseCase,
    PoliceOfficerPortalContext,
)
from sentinel_anpr.application.use_cases.dashboard.get_dashboard_summary_use_case import (
    GetDashboardSummaryUseCase,
)
from sentinel_anpr.application.use_cases.dashboard.get_executive_dashboard_use_case import (
    GetExecutiveDashboardUseCase,
)
from sentinel_anpr.application.use_cases.dashboard.export_executive_dashboard_use_case import (
    ExportExecutiveDashboardUseCase,
)
from sentinel_anpr.application.use_cases.dashboard.get_recent_activity_use_case import (
    GetRecentActivityUseCase,
)
from sentinel_anpr.application.use_cases.health.get_health_use_case import GetHealthUseCase
from sentinel_anpr.application.use_cases.ingestion.upload_vehicle_image_use_case import (
    UploadVehicleImageUseCase,
)
from sentinel_anpr.application.use_cases.vehicle.lookup_vehicle_use_case import LookupVehicleUseCase
from sentinel_anpr.application.use_cases.risk.assess_risk_use_case import AssessRiskUseCase
from sentinel_anpr.application.use_cases.history.query_scan_history_use_case import (
    QueryScanHistoryUseCase,
)
from sentinel_anpr.application.use_cases.history.save_completed_scan_use_case import (
    SaveCompletedScanUseCase,
)
from sentinel_anpr.application.use_cases.reporting.download_investigation_report_use_case import (
    DownloadInvestigationReportUseCase,
)
from sentinel_anpr.application.use_cases.reporting.export_investigation_reports_use_case import (
    ExportInvestigationReportsUseCase,
)
from sentinel_anpr.application.use_cases.reporting.generate_investigation_report_use_case import (
    GenerateInvestigationReportUseCase,
)
from sentinel_anpr.application.use_cases.reporting.query_investigation_reports_use_case import (
    QueryInvestigationReportsUseCase,
)
from sentinel_anpr.application.use_cases.analytics.get_analytics_overview_use_case import (
    GetAnalyticsOverviewUseCase,
)
from sentinel_anpr.application.use_cases.orchestration.run_vision_verification_workflow_use_case import (
    RunVisionVerificationWorkflowUseCase,
)
from sentinel_anpr.application.use_cases.orchestration.count_visible_vehicles_use_case import (
    CountVisibleVehiclesUseCase,
)
from sentinel_anpr.application.use_cases.orchestration.detect_vehicles_use_case import (
    DetectVehiclesUseCase,
)
from sentinel_anpr.application.use_cases.orchestration.run_selected_vehicles_verification_workflow_use_case import (
    RunSelectedVehiclesVerificationWorkflowUseCase,
)
from sentinel_anpr.application.use_cases.challans.challan_use_cases import (
    CancelChallanUseCase,
    CreateChallanUseCase,
    DeleteChallanUseCase,
    GenerateChallanPdfUseCase,
    GetChallanAnalyticsUseCase,
    GetChallanUseCase,
    ListViolationMasterUseCase,
    LookupChallansByRegistrationUseCase,
    MarkChallanPaidUseCase,
    QueryChallansUseCase,
    SearchVehicleForChallanUseCase,
    UpdateChallanUseCase,
)


@dataclass
class AppContainer:
    """Holds wired dependencies for the application lifetime."""

    config: ConfigPort
    logger: LoggingPort
    database: DatabasePort
    engine: Engine
    session_factory: sessionmaker[Session]
    get_health_use_case: GetHealthUseCase
    token_provider: TokenProviderPort
    login_use_case: LoginUseCase
    logout_use_case: LogoutUseCase
    get_current_officer_use_case: GetCurrentOfficerUseCase
    query_users_use_case: QueryUsersUseCase
    create_user_use_case: CreateUserUseCase
    update_user_use_case: UpdateUserUseCase
    change_user_status_use_case: ChangeUserStatusUseCase
    reset_user_password_use_case: ResetUserPasswordUseCase
    reset_station_admin_password_use_case: ResetStationAdminPasswordUseCase
    soft_delete_user_use_case: SoftDeleteUserUseCase
    query_stations_use_case: QueryStationsUseCase
    get_station_use_case: GetStationUseCase
    create_station_use_case: CreateStationUseCase
    update_station_use_case: UpdateStationUseCase
    change_station_status_use_case: ChangeStationStatusUseCase
    delete_station_use_case: DeleteStationUseCase
    station_admin_context: StationAdminPortalContext
    get_station_admin_dashboard_use_case: GetStationAdminDashboardUseCase
    query_station_officers_use_case: QueryStationOfficersUseCase
    create_station_officer_use_case: CreateStationOfficerUseCase
    update_station_officer_use_case: UpdateStationOfficerUseCase
    change_station_officer_status_use_case: ChangeStationOfficerStatusUseCase
    reset_station_officer_password_use_case: ResetStationOfficerPasswordUseCase
    soft_delete_station_officer_use_case: SoftDeleteStationOfficerUseCase
    update_station_details_use_case: UpdateStationDetailsUseCase
    get_station_analytics_use_case: GetStationAnalyticsUseCase
    get_station_notifications_use_case: GetStationNotificationsUseCase
    get_station_admin_profile_use_case: GetStationAdminProfileUseCase
    update_station_admin_profile_use_case: UpdateStationAdminProfileUseCase
    change_station_admin_password_use_case: ChangeStationAdminPasswordUseCase
    police_officer_context: PoliceOfficerPortalContext
    get_police_officer_dashboard_use_case: GetPoliceOfficerDashboardUseCase
    get_police_officer_notifications_use_case: GetPoliceOfficerNotificationsUseCase
    get_police_officer_profile_use_case: GetPoliceOfficerProfileUseCase
    update_police_officer_profile_use_case: UpdatePoliceOfficerProfileUseCase
    change_police_officer_password_use_case: ChangePoliceOfficerPasswordUseCase
    upload_vehicle_image_use_case: UploadVehicleImageUseCase
    lookup_vehicle_use_case: LookupVehicleUseCase
    assess_risk_use_case: AssessRiskUseCase
    save_completed_scan_use_case: SaveCompletedScanUseCase
    query_scan_history_use_case: QueryScanHistoryUseCase
    generate_investigation_report_use_case: GenerateInvestigationReportUseCase
    download_investigation_report_use_case: DownloadInvestigationReportUseCase
    query_investigation_reports_use_case: QueryInvestigationReportsUseCase
    export_investigation_reports_use_case: ExportInvestigationReportsUseCase
    get_analytics_overview_use_case: GetAnalyticsOverviewUseCase
    run_vehicle_verification_workflow_use_case: RunVisionVerificationWorkflowUseCase
    detect_vehicles_use_case: DetectVehiclesUseCase
    count_visible_vehicles_use_case: CountVisibleVehiclesUseCase
    run_selected_vehicles_verification_workflow_use_case: RunSelectedVehiclesVerificationWorkflowUseCase
    get_dashboard_summary_use_case: GetDashboardSummaryUseCase
    get_recent_activity_use_case: GetRecentActivityUseCase
    get_executive_dashboard_use_case: GetExecutiveDashboardUseCase
    export_executive_dashboard_use_case: ExportExecutiveDashboardUseCase
    list_violation_master_use_case: ListViolationMasterUseCase
    lookup_challans_by_registration_use_case: LookupChallansByRegistrationUseCase
    search_vehicle_for_challan_use_case: SearchVehicleForChallanUseCase
    query_challans_use_case: QueryChallansUseCase
    get_challan_use_case: GetChallanUseCase
    create_challan_use_case: CreateChallanUseCase
    update_challan_use_case: UpdateChallanUseCase
    cancel_challan_use_case: CancelChallanUseCase
    mark_challan_paid_use_case: MarkChallanPaidUseCase
    delete_challan_use_case: DeleteChallanUseCase
    get_challan_analytics_use_case: GetChallanAnalyticsUseCase
    generate_challan_pdf_use_case: GenerateChallanPdfUseCase
    anchor_evidence_block_use_case: AnchorEvidenceBlockUseCase
    verify_investigation_integrity_use_case: VerifyInvestigationIntegrityUseCase
    send_chat_message_use_case: SendChatMessageUseCase
    vision_ai_service: VisionAiService | None = None
