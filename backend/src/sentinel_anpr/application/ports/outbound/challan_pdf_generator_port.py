"""Challan PDF generation port."""

from typing import Protocol

from sentinel_anpr.application.dto.challan_dto import ChallanDetailDto


class ChallanPdfGeneratorPort(Protocol):
    def generate_challan_pdf(self, challan: ChallanDetailDto) -> bytes: ...
