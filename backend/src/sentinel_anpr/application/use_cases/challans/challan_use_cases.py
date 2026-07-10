"""Challan management use cases."""

from __future__ import annotations

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.dto.challan_dto import (
    ChallanAnalyticsResult,
    ChallanDetailDto,
    ChallanFilters,
    ChallanListItemDto,
    ChallanMutationResult,
    ChallanSummaryDto,
    CreateChallanCommand,
    QueryChallansResult,
    UpdateChallanCommand,
    VehicleChallanSearchResult,
)
from sentinel_anpr.application.dto.vehicle_dto import LookupVehicleCommand
from sentinel_anpr.application.ports.outbound.challan_pdf_generator_port import ChallanPdfGeneratorPort
from sentinel_anpr.application.ports.outbound.challan_repository_port import ChallanRepositoryPort
from sentinel_anpr.application.services.challan_access_policy import (
    can_delete_challans,
    can_edit_challan,
    resolve_challan_access_scope,
)
from sentinel_anpr.application.use_cases.authentication.get_current_officer_use_case import (
    GetCurrentOfficerUseCase,
)
from sentinel_anpr.application.use_cases.vehicle.lookup_vehicle_use_case import LookupVehicleUseCase
from sentinel_anpr.domain.challans.challan_status import ChallanPaymentStatus
from sentinel_anpr.domain.challans.errors import ChallanAccessDeniedError, ChallanNotFoundError
from sentinel_anpr.domain.common.value_objects.plate_text_normalizer import (
    normalize_registration_number,
)

_ALLOWED_PAYMENT_STATUSES = {
    ChallanPaymentStatus.PENDING.value,
    ChallanPaymentStatus.PAID.value,
    ChallanPaymentStatus.CANCELLED.value,
    ChallanPaymentStatus.WAIVED.value,
}


class ChallanPortalContext:
    def __init__(self, get_current_officer_use_case: GetCurrentOfficerUseCase) -> None:
        self._get_current_officer_use_case = get_current_officer_use_case

    def officer_and_scope(self, principal: AuthPrincipal):
        officer = self._get_current_officer_use_case.execute(principal).officer
        scope = resolve_challan_access_scope(principal, officer.station_id)
        return officer, scope


class ListViolationMasterUseCase:
    def __init__(self, repository: ChallanRepositoryPort) -> None:
        self._repository = repository

    def execute(self):
        return self._repository.list_violations()


class LookupChallansByRegistrationUseCase:
    def __init__(self, repository: ChallanRepositoryPort) -> None:
        self._repository = repository

    def execute(self, registration_number: str) -> ChallanSummaryDto:
        return self._repository.summarize_by_registration(registration_number)


class SearchVehicleForChallanUseCase:
    def __init__(
        self,
        repository: ChallanRepositoryPort,
        lookup_vehicle_use_case: LookupVehicleUseCase,
    ) -> None:
        self._repository = repository
        self._lookup = lookup_vehicle_use_case

    def execute(self, registration_number: str) -> VehicleChallanSearchResult:
        registration = normalize_registration_number(registration_number)
        lookup = self._lookup.execute(LookupVehicleCommand(plate=registration))
        summary = self._repository.summarize_by_registration(registration)
        existing_details = self._repository.list_by_registration(registration)
        existing = tuple(
            ChallanListItemDto(
                id=item.id,
                challan_number=item.challan_number,
                registration_number=item.registration_number,
                owner_name=item.owner_name,
                violation_type=item.violation_type,
                violation_description=item.violation_description,
                fine_amount=item.fine_amount,
                payment_status=item.payment_status,
                officer_id=item.officer_id,
                officer_name=item.officer_name,
                station_id=item.station_id,
                station_name=item.station_name,
                issued_at=item.issued_at,
            )
            for item in existing_details
        )
        previous_violations = tuple(dict.fromkeys(item.violation_type for item in existing_details))
        vehicle = lookup.vehicle
        return VehicleChallanSearchResult(
            registration_number=registration,
            vehicle_found=lookup.lookup_status.value == "found",
            owner_name=vehicle.registered_owner if vehicle else None,
            vehicle_name=(f"{vehicle.make} {vehicle.model}".strip() if vehicle else None),
            brand=vehicle.make if vehicle else None,
            model=vehicle.model if vehicle else None,
            color=vehicle.color if vehicle else None,
            vehicle_type=vehicle.vehicle_type if vehicle else None,
            rc_status=vehicle.registration_status if vehicle else None,
            insurance_status="Unknown",
            pollution_status="Unknown",
            risk_level=None,
            outstanding_fine_inr=summary.outstanding_fine_inr,
            pending_challans_count=summary.pending_challans_count,
            previous_violations=previous_violations,
            existing_challans=existing,
            challan_summary=summary,
        )


class QueryChallansUseCase:
    def __init__(self, repository: ChallanRepositoryPort, context: ChallanPortalContext) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal, filters: ChallanFilters) -> QueryChallansResult:
        _, scope = self._context.officer_and_scope(principal)
        return self._repository.query_challans(filters, scope)


class GetChallanUseCase:
    def __init__(self, repository: ChallanRepositoryPort, context: ChallanPortalContext) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal, challan_id: str) -> ChallanDetailDto:
        officer, scope = self._context.officer_and_scope(principal)
        challan = self._repository.get_challan(challan_id)
        if challan is None:
            raise ChallanNotFoundError()
        if not scope.all_access:
            if scope.station_id and challan.station_id != scope.station_id:
                raise ChallanAccessDeniedError()
            if scope.officer_id and challan.officer_id != scope.officer_id:
                raise ChallanAccessDeniedError()
        return challan


class CreateChallanUseCase:
    def __init__(self, repository: ChallanRepositoryPort, context: ChallanPortalContext) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal, command: CreateChallanCommand) -> ChallanMutationResult:
        officer, _ = self._context.officer_and_scope(principal)
        violation = self._repository.get_violation(command.violation_type)
        if violation is None:
            raise ValueError("Invalid violation type")
        fine_amount = command.fine_amount
        if not violation.amount_editable and fine_amount != violation.default_fine_amount:
            fine_amount = violation.default_fine_amount
        challan_number = self._repository.next_challan_number()
        normalized = CreateChallanCommand(
            registration_number=command.registration_number,
            owner_name=command.owner_name,
            vehicle_id=command.vehicle_id,
            investigation_id=command.investigation_id,
            violation_type=violation.violation_code,
            violation_description=command.violation_description or violation.violation_name,
            fine_amount=fine_amount,
            remarks=command.remarks,
            location_label=command.location_label,
            gps_coordinates=command.gps_coordinates,
            evidence_image_path=command.evidence_image_path,
            officer_id=officer.officer_id,
            officer_name=f"{officer.first_name} {officer.last_name}".strip(),
            station_id=officer.station_id,
            station_name=officer.station_name,
        )
        challan = self._repository.create_challan(normalized, challan_number)
        return ChallanMutationResult(
            challan=challan,
            pdf_download_url=f"/v1/challans/{challan.id}/download",
        )


class UpdateChallanUseCase:
    def __init__(self, repository: ChallanRepositoryPort, context: ChallanPortalContext) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal, command: UpdateChallanCommand) -> ChallanMutationResult:
        officer, _ = self._context.officer_and_scope(principal)
        existing = self._repository.get_challan(command.challan_id)
        if existing is None:
            raise ChallanNotFoundError()
        if not can_edit_challan(
            principal,
            officer_id=existing.officer_id,
            station_id=existing.station_id,
            caller_station_id=officer.station_id,
        ):
            raise ChallanAccessDeniedError()
        challan = self._repository.update_challan(command)
        return ChallanMutationResult(challan=challan)


class CancelChallanUseCase:
    def __init__(self, repository: ChallanRepositoryPort, context: ChallanPortalContext) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal, challan_id: str) -> ChallanMutationResult:
        officer, _ = self._context.officer_and_scope(principal)
        existing = self._repository.get_challan(challan_id)
        if existing is None:
            raise ChallanNotFoundError()
        if not can_edit_challan(
            principal,
            officer_id=existing.officer_id,
            station_id=existing.station_id,
            caller_station_id=officer.station_id,
        ):
            raise ChallanAccessDeniedError()
        challan = self._repository.set_payment_status(challan_id, ChallanPaymentStatus.CANCELLED.value)
        return ChallanMutationResult(challan=challan)


class MarkChallanPaidUseCase:
    def __init__(self, repository: ChallanRepositoryPort, context: ChallanPortalContext) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal, challan_id: str) -> ChallanMutationResult:
        officer, _ = self._context.officer_and_scope(principal)
        existing = self._repository.get_challan(challan_id)
        if existing is None:
            raise ChallanNotFoundError()
        if not can_edit_challan(
            principal,
            officer_id=existing.officer_id,
            station_id=existing.station_id,
            caller_station_id=officer.station_id,
        ):
            raise ChallanAccessDeniedError()
        challan = self._repository.set_payment_status(challan_id, ChallanPaymentStatus.PAID.value)
        return ChallanMutationResult(challan=challan)


class DeleteChallanUseCase:
    def __init__(self, repository: ChallanRepositoryPort, context: ChallanPortalContext) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal, challan_id: str) -> None:
        if not can_delete_challans(principal):
            raise ChallanAccessDeniedError()
        existing = self._repository.get_challan(challan_id)
        if existing is None:
            raise ChallanNotFoundError()
        self._repository.soft_delete_challan(challan_id)


class GetChallanAnalyticsUseCase:
    def __init__(self, repository: ChallanRepositoryPort, context: ChallanPortalContext) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal) -> ChallanAnalyticsResult:
        _, scope = self._context.officer_and_scope(principal)
        return self._repository.get_analytics(scope)


class GenerateChallanPdfUseCase:
    def __init__(
        self,
        repository: ChallanRepositoryPort,
        pdf_generator: ChallanPdfGeneratorPort,
        context: ChallanPortalContext,
    ) -> None:
        self._repository = repository
        self._pdf_generator = pdf_generator
        self._context = context

    def execute(self, principal: AuthPrincipal, challan_id: str) -> tuple[ChallanDetailDto, bytes]:
        challan = GetChallanUseCase(self._repository, self._context).execute(principal, challan_id)
        pdf_bytes = self._pdf_generator.generate_challan_pdf(challan)
        return challan, pdf_bytes
