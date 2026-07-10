"""Validate and store a vehicle image."""

from datetime import UTC, datetime

from sentinel_anpr.application.dto.upload_dto import UploadImageCommand, UploadImageResult
from sentinel_anpr.application.ports.outbound.image_inspector_port import ImageInspectorPort
from sentinel_anpr.application.ports.outbound.image_storage_port import ImageStoragePort
from sentinel_anpr.domain.ingestion.validators.image_validator import validate_vehicle_image


class UploadVehicleImageUseCase:
    """Store vehicle image bytes without AI or OCR."""

    def __init__(
        self,
        image_inspector: ImageInspectorPort,
        image_storage: ImageStoragePort,
    ) -> None:
        self._image_inspector = image_inspector
        self._image_storage = image_storage

    def execute(self, command: UploadImageCommand) -> UploadImageResult:
        content_type = self._image_inspector.detect_content_type(
            command.content,
            command.content_type,
        )
        width, height = self._image_inspector.get_dimensions(command.content)
        validate_vehicle_image(
            content_type=content_type,
            size_bytes=len(command.content),
            width=width,
            height=height,
        )

        stored = self._image_storage.store(
            officer_id=command.officer_id,
            content=command.content,
            content_type=content_type,
            original_filename=command.original_filename,
            width=width,
            height=height,
        )

        return UploadImageResult(
            upload_id=stored.upload_id,
            storage_key=stored.storage_key,
            original_filename=command.original_filename,
            content_type=stored.content_type,
            size_bytes=stored.size_bytes,
            width=stored.width,
            height=stored.height,
            uploaded_at=datetime.now(UTC),
        )
