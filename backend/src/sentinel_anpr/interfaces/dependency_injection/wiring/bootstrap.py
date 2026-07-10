"""Application dependency wiring."""

import os

from dotenv import dotenv_values

from sentinel_anpr.application.use_cases.authentication.get_current_officer_use_case import (
    GetCurrentOfficerUseCase,
)
from sentinel_anpr.application.use_cases.authentication.login_use_case import LoginUseCase
from sentinel_anpr.application.use_cases.authentication.logout_use_case import LogoutUseCase
from sentinel_anpr.application.use_cases.authentication.user_management_use_cases import (
    ChangeUserStatusUseCase,
    CreateUserUseCase,
    QueryUsersUseCase,
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
from sentinel_anpr.infrastructure.config.loaders.settings_adapter import SettingsConfigAdapter
from sentinel_anpr.infrastructure.config.settings import (
    Settings,
    get_backend_dir,
    get_env_file_path,
    hf_token_exists,
    load_env_file,
    reload_settings,
    resolve_hf_api_url,
    resolve_hf_token,
    validate_vision_configuration,
)
from sentinel_anpr.infrastructure.authentication.jwt.jwt_token_provider import JwtTokenProvider
from sentinel_anpr.infrastructure.authentication.password.bcrypt_hasher import BcryptPasswordHasher
from sentinel_anpr.infrastructure.authentication.stores.in_memory_refresh_token_store import (
    InMemoryRefreshTokenStore,
)
from sentinel_anpr.infrastructure.authentication.stores.sqlite_credential_store import (
    SqliteCredentialStore,
)
from sentinel_anpr.application.ports.outbound.logging_port import LoggingPort
from sentinel_anpr.application.ports.vision_ai_service import VisionAiService
from sentinel_anpr.infrastructure.ai.huggingface_vision_service import HuggingFaceVisionService
from sentinel_anpr.infrastructure.adapters.workflow_progress_adapter import (
    NoOpWorkflowProgressAdapter,
)
from sentinel_anpr.infrastructure.ai.stub_vision_service import StubVisionService
from sentinel_anpr.infrastructure.ai.stub_vehicle_detection_service import StubVehicleDetectionService
from sentinel_anpr.infrastructure.ai.opencv_vehicle_detection_service import OpenCvVehicleDetectionService
from sentinel_anpr.infrastructure.ai.stub_license_plate_detection_service import StubLicensePlateDetectionService
from sentinel_anpr.infrastructure.ai.opencv_license_plate_detection_service import OpenCvLicensePlateDetectionService
from sentinel_anpr.infrastructure.ai.intelligent_scene_detection_service import DefaultIntelligentSceneDetectionService
from sentinel_anpr.infrastructure.database.init_demo_database import initialize_demo_database
from sentinel_anpr.infrastructure.database.repositories.vehicles.sqlite_vehicle_repository import (
    SqliteVehicleRepository,
)
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
from sentinel_anpr.domain.risk.services.risk_engine_policy import RiskEnginePolicy
from sentinel_anpr.domain.reporting.services.investigation_report_policy import (
    InvestigationReportPolicy,
)
from sentinel_anpr.infrastructure.database.repositories.scan_history.sqlite_scan_repository import (
    SqliteScanRepository,
)
from sentinel_anpr.application.use_cases.analytics.get_analytics_overview_use_case import (
    GetAnalyticsOverviewUseCase,
)
from sentinel_anpr.application.use_cases.orchestration.run_vision_verification_workflow_use_case import (
    RunVisionVerificationWorkflowUseCase,
)
from sentinel_anpr.application.use_cases.orchestration.detect_vehicles_use_case import (
    DetectVehiclesUseCase,
)
from sentinel_anpr.application.use_cases.orchestration.run_selected_vehicles_verification_workflow_use_case import (
    RunSelectedVehiclesVerificationWorkflowUseCase,
)
from sentinel_anpr.application.use_cases.challans.challan_use_cases import (
    CancelChallanUseCase,
    ChallanPortalContext,
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
from sentinel_anpr.infrastructure.database.repositories.investigation_reports.sqlite_report_repository import (
    SqliteReportRepository,
)
from sentinel_anpr.application.use_cases.persistence.persist_workflow_outcome_use_case import (
    PersistWorkflowOutcomeUseCase,
)
from sentinel_anpr.infrastructure.database.repositories.dashboard.sqlite_dashboard_snapshot_repository import (
    SqliteDashboardSnapshotRepository,
)
from sentinel_anpr.infrastructure.database.repositories.officer_activity.sqlite_officer_activity_repository import (
    SqliteOfficerActivityRepository,
)
from sentinel_anpr.infrastructure.database.repositories.risk.sqlite_risk_assessment_repository import (
    SqliteRiskAssessmentRepository,
)
from sentinel_anpr.infrastructure.database.repositories.verification.sqlite_verification_result_repository import (
    SqliteVerificationResultRepository,
)
from sentinel_anpr.infrastructure.database.repositories.workflow.sqlite_workflow_persistence_repository import (
    SqliteWorkflowPersistenceRepository,
)
from sentinel_anpr.infrastructure.database.repositories.analytics.sqlite_analytics_repository import (
    SqliteAnalyticsRepository,
)
from sentinel_anpr.infrastructure.database.repositories.reporting.sqlite_investigation_reports_query_repository import (
    SqliteInvestigationReportsQueryRepository,
)
from sentinel_anpr.infrastructure.database.repositories.officers.sqlite_user_identity_sequence_repository import (
    SqliteUserIdentitySequenceRepository,
)
from sentinel_anpr.infrastructure.database.repositories.officers.sqlite_user_management_repository import (
    SqliteUserManagementRepository,
)
from sentinel_anpr.infrastructure.database.repositories.stations.sqlite_station_management_repository import (
    SqliteStationManagementRepository,
)
from sentinel_anpr.infrastructure.database.repositories.station_admin.sqlite_station_admin_portal_repository import (
    SqliteStationAdminPortalRepository,
)
from sentinel_anpr.infrastructure.database.repositories.challans.sqlite_challan_repository import (
    SqliteChallanRepository,
)
from sentinel_anpr.infrastructure.database.repositories.police_officer.sqlite_police_officer_portal_repository import (
    SqlitePoliceOfficerPortalRepository,
)
from sentinel_anpr.infrastructure.pdf.reportlab_challan_pdf_generator import (
    ReportLabChallanPdfGenerator,
)
from sentinel_anpr.infrastructure.pdf.reportlab_investigation_pdf_generator import (
    ReportLabInvestigationPdfGenerator,
)
from sentinel_anpr.infrastructure.reporting.department_investigation_export_generator import (
    DepartmentInvestigationExportGenerator,
)
from sentinel_anpr.infrastructure.reporting.executive_dashboard_export_generator import (
    ExecutiveDashboardExportGenerator,
)
from sentinel_anpr.infrastructure.ingestion.pillow_image_inspector import PillowImageInspector
from sentinel_anpr.infrastructure.storage.local_image_storage import LocalImageStorage
from sentinel_anpr.infrastructure.dashboard.sqlite_dashboard_data_adapter import (
    SqliteDashboardDataAdapter,
)
from sentinel_anpr.infrastructure.dashboard.sqlite_executive_dashboard_repository import (
    SqliteExecutiveDashboardRepository,
)
from sentinel_anpr.infrastructure.database.connection.engine import create_db_engine
from sentinel_anpr.infrastructure.database.connection.session import create_session_factory
from sentinel_anpr.infrastructure.database.connection.sqlite_adapter import SqliteDatabaseAdapter
from sentinel_anpr.infrastructure.logging.adapters.stdlib_logging_adapter import StdlibLoggingAdapter
from sentinel_anpr.infrastructure.logging.setup import configure_logging
from sentinel_anpr.interfaces.dependency_injection.containers.app_container import AppContainer


def _build_vision_ai_service(
    *,
    settings: Settings,
    logger: LoggingPort,
) -> VisionAiService:
    """Select the vision provider from configuration.

    Active providers:
    - ``huggingface`` → :class:`HuggingFaceVisionService` (default production provider)
    - ``stub`` → :class:`StubVisionService` (local/tests)
    """
    provider = (settings.vision_provider or "huggingface").strip().lower()
    hf_model = (settings.hf_model or "google/gemma-3-4b-it:deepinfra").strip()
    hf_model = hf_model or "google/gemma-3-4b-it:deepinfra"
    token_exists = hf_token_exists(settings)
    hf_api_url = resolve_hf_api_url(settings=settings)

    # Startup diagnostics — never log the token value.
    logger.info(
        "startup_configuration",
        detail="Vision configuration",
        vision_provider=provider,
        hf_model=hf_model,
        hf_api_url=hf_api_url,
        hf_token_exists=token_exists,
        project_root=str(get_backend_dir()),
        working_directory=os.getcwd(),
        loaded_env_path=str(get_env_file_path()),
        env_file_exists=get_env_file_path().is_file(),
        environment=settings.env,
    )
    logger.info("Vision Provider", vision_provider=provider)
    logger.info("Hugging Face Model", hf_model=hf_model)
    logger.info("Hugging Face Token Exists", hf_token_exists=token_exists)

    if provider == "huggingface":
        validate_vision_configuration(settings)
        token = resolve_hf_token(settings)
        service = HuggingFaceVisionService(
            token=token,
            model=hf_model,
            api_url=hf_api_url,
            request_timeout_seconds=settings.hf_request_timeout_seconds,
            logger=logger,
        )
        logger.info(
            "vision_service_ready",
            vision_provider=provider,
            hf_model=hf_model,
            hf_token_exists=True,
            vision_service_type=type(service).__name__,
            huggingface_service_initialized=service.is_ready,
        )
        if get_env_file_path().is_file():
            logger.info("loaded_env_successfully", path=str(get_env_file_path()))
        if not service.is_ready and service.init_failure_reason:
            raise RuntimeError(service.init_failure_reason)
        return service

    if provider == "stub":
        if settings.env.strip().lower() == "production":
            raise RuntimeError(
                "SENTINEL_VISION_PROVIDER=stub is not allowed when SENTINEL_ENV=production. "
                "Set SENTINEL_VISION_PROVIDER=huggingface and configure HF_TOKEN."
            )
        if token_exists and get_env_file_path().is_file():
            file_values = dotenv_values(get_env_file_path())
            file_provider = (file_values.get("SENTINEL_VISION_PROVIDER") or "").strip().lower()
            if file_provider == "huggingface":
                logger.warning(
                    "vision_provider_stub_over_huggingface_config",
                    detail=(
                        "Stub vision is active but backend/.env requests huggingface and "
                        "HF_TOKEN is set. Restart in a fresh shell or remove "
                        "SENTINEL_VISION_PROVIDER=stub from the process environment."
                    ),
                    vision_provider=provider,
                    env_file_provider=file_provider,
                )
        service = StubVisionService()
        logger.info(
            "vision_service_ready",
            vision_provider=provider,
            hf_model=hf_model,
            hf_token_exists=token_exists,
            vision_service_type=type(service).__name__,
        )
        return service

    raise ValueError(
        f"Unsupported vision_provider '{settings.vision_provider}'. "
        "Expected 'huggingface' or 'stub'."
    )


def _build_vehicle_detection_service(*, settings: Settings, logger: LoggingPort):
    """Select the vehicle detection provider from configuration."""
    provider = (settings.vehicle_detection_provider or "opencv").strip().lower()
    if provider == "stub":
        service = StubVehicleDetectionService()
    elif provider == "opencv":
        service = OpenCvVehicleDetectionService()
    else:
        raise ValueError(
            f"Unsupported vehicle_detection_provider '{settings.vehicle_detection_provider}'. "
            "Expected 'opencv' or 'stub'."
        )
    logger.info(
        "vehicle_detection_service_ready",
        vehicle_detection_provider=provider,
        vehicle_detection_service_type=type(service).__name__,
    )
    return service


def _build_license_plate_detection_service(*, settings: Settings, logger: LoggingPort):
    """Select the license plate detection provider from configuration."""
    provider = (settings.vehicle_detection_provider or "opencv").strip().lower()
    if provider == "stub":
        service = StubLicensePlateDetectionService()
    elif provider == "opencv":
        service = OpenCvLicensePlateDetectionService()
    else:
        raise ValueError(
            f"Unsupported vehicle_detection_provider '{settings.vehicle_detection_provider}'. "
            "Expected 'opencv' or 'stub'."
        )
    logger.info(
        "license_plate_detection_service_ready",
        vehicle_detection_provider=provider,
        license_plate_detection_service_type=type(service).__name__,
    )
    return service


def build_container() -> AppContainer:
    """Composition root — wire concrete adapters to use cases."""
    load_env_file()
    settings = reload_settings()
    configure_logging(settings.log_level)
    validate_vision_configuration(settings)

    config = SettingsConfigAdapter(settings)
    logger = StdlibLoggingAdapter()
    password_hasher = BcryptPasswordHasher()
    engine = create_db_engine(settings.database_url)
    initialize_demo_database(engine, password_hasher=password_hasher)
    session_factory = create_session_factory(engine)
    database = SqliteDatabaseAdapter(engine)

    get_health = GetHealthUseCase(config=config, database=database)

    credential_store = SqliteCredentialStore(session_factory=session_factory)
    identity_sequences = SqliteUserIdentitySequenceRepository(session_factory=session_factory)
    user_management_repository = SqliteUserManagementRepository(session_factory=session_factory)
    station_management_repository = SqliteStationManagementRepository(session_factory=session_factory)
    station_admin_repository = SqliteStationAdminPortalRepository(session_factory=session_factory)
    police_officer_repository = SqlitePoliceOfficerPortalRepository(session_factory=session_factory)
    refresh_token_store = InMemoryRefreshTokenStore()
    token_provider = JwtTokenProvider(
        secret=settings.auth_jwt_secret,
        issuer=settings.auth_jwt_issuer,
        access_token_ttl_seconds=settings.auth_access_token_ttl_seconds,
        refresh_token_ttl_seconds=settings.auth_refresh_token_ttl_seconds,
    )
    login_use_case = LoginUseCase(
        credential_store=credential_store,
        password_hasher=password_hasher,
        token_provider=token_provider,
        refresh_token_store=refresh_token_store,
    )
    logout_use_case = LogoutUseCase(refresh_token_store=refresh_token_store)
    get_current_officer_use_case = GetCurrentOfficerUseCase(credential_store=credential_store)
    query_users_use_case = QueryUsersUseCase(repository=user_management_repository)
    create_user_use_case = CreateUserUseCase(
        repository=user_management_repository,
        password_hasher=password_hasher,
        identity_sequences=identity_sequences,
    )
    update_user_use_case = UpdateUserUseCase(repository=user_management_repository)
    change_user_status_use_case = ChangeUserStatusUseCase(repository=user_management_repository)
    reset_user_password_use_case = ResetUserPasswordUseCase(
        repository=user_management_repository,
        password_hasher=password_hasher,
    )
    soft_delete_user_use_case = SoftDeleteUserUseCase(repository=user_management_repository)
    query_stations_use_case = QueryStationsUseCase(repository=station_management_repository)
    get_station_use_case = GetStationUseCase(repository=station_management_repository)
    create_station_use_case = CreateStationUseCase(repository=station_management_repository)
    update_station_use_case = UpdateStationUseCase(repository=station_management_repository)
    change_station_status_use_case = ChangeStationStatusUseCase(
        repository=station_management_repository
    )
    delete_station_use_case = DeleteStationUseCase(repository=station_management_repository)
    station_admin_context = StationAdminPortalContext(
        get_current_officer_use_case=get_current_officer_use_case
    )
    get_station_admin_dashboard_use_case = GetStationAdminDashboardUseCase(
        repository=station_admin_repository,
        context=station_admin_context,
    )
    query_station_officers_use_case = QueryStationOfficersUseCase(
        repository=station_admin_repository,
        context=station_admin_context,
    )
    create_station_officer_use_case = CreateStationOfficerUseCase(
        repository=station_admin_repository,
        context=station_admin_context,
        password_hasher=password_hasher,
        identity_sequences=identity_sequences,
    )
    update_station_officer_use_case = UpdateStationOfficerUseCase(
        repository=station_admin_repository,
        context=station_admin_context,
    )
    change_station_officer_status_use_case = ChangeStationOfficerStatusUseCase(
        repository=station_admin_repository,
        context=station_admin_context,
    )
    reset_station_officer_password_use_case = ResetStationOfficerPasswordUseCase(
        repository=station_admin_repository,
        context=station_admin_context,
        password_hasher=password_hasher,
    )
    soft_delete_station_officer_use_case = SoftDeleteStationOfficerUseCase(
        repository=station_admin_repository,
        context=station_admin_context,
    )
    update_station_details_use_case = UpdateStationDetailsUseCase(
        repository=station_admin_repository,
        context=station_admin_context,
    )
    get_station_analytics_use_case = GetStationAnalyticsUseCase(
        repository=station_admin_repository,
        context=station_admin_context,
    )
    get_station_notifications_use_case = GetStationNotificationsUseCase(
        repository=station_admin_repository,
        context=station_admin_context,
    )
    get_station_admin_profile_use_case = GetStationAdminProfileUseCase(
        repository=station_admin_repository,
        context=station_admin_context,
    )
    update_station_admin_profile_use_case = UpdateStationAdminProfileUseCase(
        repository=station_admin_repository,
        context=station_admin_context,
    )
    change_station_admin_password_use_case = ChangeStationAdminPasswordUseCase(
        repository=station_admin_repository,
        context=station_admin_context,
        credential_store=credential_store,
        password_hasher=password_hasher,
    )
    police_officer_context = PoliceOfficerPortalContext(
        get_current_officer_use_case=get_current_officer_use_case
    )
    get_police_officer_dashboard_use_case = GetPoliceOfficerDashboardUseCase(
        repository=police_officer_repository,
        context=police_officer_context,
    )
    get_police_officer_notifications_use_case = GetPoliceOfficerNotificationsUseCase(
        repository=police_officer_repository,
        context=police_officer_context,
    )
    get_police_officer_profile_use_case = GetPoliceOfficerProfileUseCase(
        repository=police_officer_repository,
        context=police_officer_context,
    )
    update_police_officer_profile_use_case = UpdatePoliceOfficerProfileUseCase(
        repository=police_officer_repository,
        context=police_officer_context,
    )
    change_police_officer_password_use_case = ChangePoliceOfficerPasswordUseCase(
        repository=police_officer_repository,
        context=police_officer_context,
        credential_store=credential_store,
        password_hasher=password_hasher,
    )

    image_inspector = PillowImageInspector()
    image_storage = LocalImageStorage(base_dir=settings.upload_storage_dir)
    upload_vehicle_image_use_case = UploadVehicleImageUseCase(
        image_inspector=image_inspector,
        image_storage=image_storage,
    )

    vision_ai_service = _build_vision_ai_service(settings=settings, logger=logger)
    vehicle_detection_service = _build_vehicle_detection_service(settings=settings, logger=logger)
    license_plate_detection_service = _build_license_plate_detection_service(
        settings=settings,
        logger=logger,
    )
    intelligent_scene_detection_service = DefaultIntelligentSceneDetectionService(
        vehicle_detection_service=vehicle_detection_service,
        license_plate_detection_service=license_plate_detection_service,
        logger=logger,
    )

    vehicle_repository = SqliteVehicleRepository(session_factory=session_factory)
    lookup_vehicle_use_case = LookupVehicleUseCase(vehicle_repository=vehicle_repository)

    assess_risk_use_case = AssessRiskUseCase(risk_engine_policy=RiskEnginePolicy())

    scan_repository = SqliteScanRepository(session_factory=session_factory)
    save_completed_scan_use_case = SaveCompletedScanUseCase(scan_repository=scan_repository)
    query_scan_history_use_case = QueryScanHistoryUseCase(scan_repository=scan_repository)

    report_repository = SqliteReportRepository(
        session_factory=session_factory,
        storage_dir=settings.report_storage_dir,
    )
    pdf_generator = ReportLabInvestigationPdfGenerator()
    generate_investigation_report_use_case = GenerateInvestigationReportUseCase(
        pdf_generator=pdf_generator,
        report_repository=report_repository,
        report_policy=InvestigationReportPolicy(),
    )
    download_investigation_report_use_case = DownloadInvestigationReportUseCase(
        report_repository=report_repository,
        credential_store=credential_store,
    )
    investigation_reports_query_repository = SqliteInvestigationReportsQueryRepository(
        session_factory=session_factory,
    )
    query_investigation_reports_use_case = QueryInvestigationReportsUseCase(
        query_port=investigation_reports_query_repository,
    )
    tabular_export_generator = DepartmentInvestigationExportGenerator()
    export_investigation_reports_use_case = ExportInvestigationReportsUseCase(
        query_port=investigation_reports_query_repository,
        export_port=tabular_export_generator,
    )

    analytics_repository = SqliteAnalyticsRepository(session_factory=session_factory)
    get_analytics_overview_use_case = GetAnalyticsOverviewUseCase(
        analytics_repository=analytics_repository,
    )

    verification_repository = SqliteVerificationResultRepository(session_factory=session_factory)
    risk_assessment_repository = SqliteRiskAssessmentRepository(session_factory=session_factory)
    officer_activity_repository = SqliteOfficerActivityRepository(session_factory=session_factory)
    dashboard_snapshot_repository = SqliteDashboardSnapshotRepository(
        session_factory=session_factory
    )
    workflow_persistence_repository = SqliteWorkflowPersistenceRepository(
        session_factory=session_factory,
        scan_repository=scan_repository,
        verification_repository=verification_repository,
        risk_assessment_repository=risk_assessment_repository,
        officer_activity_repository=officer_activity_repository,
        dashboard_snapshot_repository=dashboard_snapshot_repository,
        report_repository=report_repository,
        report_storage_dir=settings.report_storage_dir,
    )
    persist_workflow_outcome_use_case = PersistWorkflowOutcomeUseCase(
        workflow_persistence=workflow_persistence_repository,
    )

    challan_repository = SqliteChallanRepository(session_factory=session_factory)
    challan_pdf_generator = ReportLabChallanPdfGenerator()
    challan_context = ChallanPortalContext(get_current_officer_use_case=get_current_officer_use_case)
    list_violation_master_use_case = ListViolationMasterUseCase(repository=challan_repository)
    lookup_challans_by_registration_use_case = LookupChallansByRegistrationUseCase(
        repository=challan_repository
    )
    search_vehicle_for_challan_use_case = SearchVehicleForChallanUseCase(
        repository=challan_repository,
        lookup_vehicle_use_case=lookup_vehicle_use_case,
    )
    query_challans_use_case = QueryChallansUseCase(
        repository=challan_repository,
        context=challan_context,
    )
    get_challan_use_case = GetChallanUseCase(repository=challan_repository, context=challan_context)
    create_challan_use_case = CreateChallanUseCase(repository=challan_repository, context=challan_context)
    update_challan_use_case = UpdateChallanUseCase(repository=challan_repository, context=challan_context)
    cancel_challan_use_case = CancelChallanUseCase(repository=challan_repository, context=challan_context)
    mark_challan_paid_use_case = MarkChallanPaidUseCase(repository=challan_repository, context=challan_context)
    delete_challan_use_case = DeleteChallanUseCase(repository=challan_repository, context=challan_context)
    get_challan_analytics_use_case = GetChallanAnalyticsUseCase(
        repository=challan_repository,
        context=challan_context,
    )
    generate_challan_pdf_use_case = GenerateChallanPdfUseCase(
        repository=challan_repository,
        pdf_generator=challan_pdf_generator,
        context=challan_context,
    )

    run_vehicle_verification_workflow_use_case = RunVisionVerificationWorkflowUseCase(
        upload_vehicle_image_use_case=upload_vehicle_image_use_case,
        vision_ai_service=vision_ai_service,
        lookup_vehicle_use_case=lookup_vehicle_use_case,
        assess_risk_use_case=assess_risk_use_case,
        persist_workflow_outcome_use_case=persist_workflow_outcome_use_case,
        generate_investigation_report_use_case=generate_investigation_report_use_case,
        lookup_challans_use_case=lookup_challans_by_registration_use_case,
        logger=logger,
        workflow_progress=NoOpWorkflowProgressAdapter(),
    )
    detect_vehicles_use_case = DetectVehiclesUseCase(
        scene_detection_service=intelligent_scene_detection_service,
        logger=logger,
    )
    run_selected_vehicles_verification_workflow_use_case = (
        RunSelectedVehiclesVerificationWorkflowUseCase(
            single_vehicle_workflow=run_vehicle_verification_workflow_use_case,
            scene_detection_service=intelligent_scene_detection_service,
            logger=logger,
        )
    )

    dashboard_data = SqliteDashboardDataAdapter(session_factory=session_factory)
    get_dashboard_summary = GetDashboardSummaryUseCase(dashboard_data=dashboard_data)
    get_recent_activity = GetRecentActivityUseCase(dashboard_data=dashboard_data)
    executive_dashboard_repository = SqliteExecutiveDashboardRepository(
        session_factory=session_factory
    )
    executive_dashboard_export_generator = ExecutiveDashboardExportGenerator()
    get_executive_dashboard_use_case = GetExecutiveDashboardUseCase(
        dashboard_port=executive_dashboard_repository
    )
    export_executive_dashboard_use_case = ExportExecutiveDashboardUseCase(
        dashboard_port=executive_dashboard_repository,
        export_port=executive_dashboard_export_generator,
    )

    logger.info(
        "dependency_injection_complete",
        workflow_type=type(run_vehicle_verification_workflow_use_case).__name__,
        vision_service_type=type(vision_ai_service).__name__,
        vision_provider=settings.vision_provider,
        hf_token_exists=bool(resolve_hf_token(settings)),
    )
    logger.info("container_initialized", environment=config.environment)

    return AppContainer(
        config=config,
        logger=logger,
        database=database,
        engine=engine,
        session_factory=session_factory,
        get_health_use_case=get_health,
        token_provider=token_provider,
        login_use_case=login_use_case,
        logout_use_case=logout_use_case,
        get_current_officer_use_case=get_current_officer_use_case,
        query_users_use_case=query_users_use_case,
        create_user_use_case=create_user_use_case,
        update_user_use_case=update_user_use_case,
        change_user_status_use_case=change_user_status_use_case,
        reset_user_password_use_case=reset_user_password_use_case,
        soft_delete_user_use_case=soft_delete_user_use_case,
        query_stations_use_case=query_stations_use_case,
        get_station_use_case=get_station_use_case,
        create_station_use_case=create_station_use_case,
        update_station_use_case=update_station_use_case,
        change_station_status_use_case=change_station_status_use_case,
        delete_station_use_case=delete_station_use_case,
        station_admin_context=station_admin_context,
        get_station_admin_dashboard_use_case=get_station_admin_dashboard_use_case,
        query_station_officers_use_case=query_station_officers_use_case,
        create_station_officer_use_case=create_station_officer_use_case,
        update_station_officer_use_case=update_station_officer_use_case,
        change_station_officer_status_use_case=change_station_officer_status_use_case,
        reset_station_officer_password_use_case=reset_station_officer_password_use_case,
        soft_delete_station_officer_use_case=soft_delete_station_officer_use_case,
        update_station_details_use_case=update_station_details_use_case,
        get_station_analytics_use_case=get_station_analytics_use_case,
        get_station_notifications_use_case=get_station_notifications_use_case,
        get_station_admin_profile_use_case=get_station_admin_profile_use_case,
        update_station_admin_profile_use_case=update_station_admin_profile_use_case,
        change_station_admin_password_use_case=change_station_admin_password_use_case,
        police_officer_context=police_officer_context,
        get_police_officer_dashboard_use_case=get_police_officer_dashboard_use_case,
        get_police_officer_notifications_use_case=get_police_officer_notifications_use_case,
        get_police_officer_profile_use_case=get_police_officer_profile_use_case,
        update_police_officer_profile_use_case=update_police_officer_profile_use_case,
        change_police_officer_password_use_case=change_police_officer_password_use_case,
        upload_vehicle_image_use_case=upload_vehicle_image_use_case,
        lookup_vehicle_use_case=lookup_vehicle_use_case,
        assess_risk_use_case=assess_risk_use_case,
        save_completed_scan_use_case=save_completed_scan_use_case,
        query_scan_history_use_case=query_scan_history_use_case,
        generate_investigation_report_use_case=generate_investigation_report_use_case,
        download_investigation_report_use_case=download_investigation_report_use_case,
        query_investigation_reports_use_case=query_investigation_reports_use_case,
        export_investigation_reports_use_case=export_investigation_reports_use_case,
        get_analytics_overview_use_case=get_analytics_overview_use_case,
        run_vehicle_verification_workflow_use_case=run_vehicle_verification_workflow_use_case,
        detect_vehicles_use_case=detect_vehicles_use_case,
        run_selected_vehicles_verification_workflow_use_case=(
            run_selected_vehicles_verification_workflow_use_case
        ),
        get_dashboard_summary_use_case=get_dashboard_summary,
        get_recent_activity_use_case=get_recent_activity,
        get_executive_dashboard_use_case=get_executive_dashboard_use_case,
        export_executive_dashboard_use_case=export_executive_dashboard_use_case,
        list_violation_master_use_case=list_violation_master_use_case,
        lookup_challans_by_registration_use_case=lookup_challans_by_registration_use_case,
        search_vehicle_for_challan_use_case=search_vehicle_for_challan_use_case,
        query_challans_use_case=query_challans_use_case,
        get_challan_use_case=get_challan_use_case,
        create_challan_use_case=create_challan_use_case,
        update_challan_use_case=update_challan_use_case,
        cancel_challan_use_case=cancel_challan_use_case,
        mark_challan_paid_use_case=mark_challan_paid_use_case,
        delete_challan_use_case=delete_challan_use_case,
        get_challan_analytics_use_case=get_challan_analytics_use_case,
        generate_challan_pdf_use_case=generate_challan_pdf_use_case,
        vision_ai_service=vision_ai_service,
    )
