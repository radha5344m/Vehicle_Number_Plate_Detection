"""Challan persistence port."""

from typing import Protocol

from sentinel_anpr.application.dto.challan_dto import (
    ChallanAccessScope,
    ChallanAnalyticsResult,
    ChallanDetailDto,
    ChallanFilters,
    ChallanSummaryDto,
    CreateChallanCommand,
    QueryChallansResult,
    UpdateChallanCommand,
    ViolationMasterDto,
)


class ChallanRepositoryPort(Protocol):
    def list_violations(self) -> tuple[ViolationMasterDto, ...]: ...

    def next_challan_number(self) -> str: ...

    def create_challan(self, command: CreateChallanCommand, challan_number: str) -> ChallanDetailDto: ...

    def get_challan(self, challan_id: str) -> ChallanDetailDto | None: ...

    def query_challans(self, filters: ChallanFilters, scope: ChallanAccessScope) -> QueryChallansResult: ...

    def update_challan(self, command: UpdateChallanCommand) -> ChallanDetailDto: ...

    def set_payment_status(self, challan_id: str, payment_status: str) -> ChallanDetailDto: ...

    def soft_delete_challan(self, challan_id: str) -> None: ...

    def summarize_by_registration(self, registration_number: str) -> ChallanSummaryDto: ...

    def list_by_registration(
        self,
        registration_number: str,
        *,
        pending_only: bool = False,
    ) -> tuple[ChallanDetailDto, ...]: ...

    def get_analytics(self, scope: ChallanAccessScope) -> ChallanAnalyticsResult: ...

    def get_violation(self, violation_code: str) -> ViolationMasterDto | None: ...
