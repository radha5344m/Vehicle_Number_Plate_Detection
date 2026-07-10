"""Run verification for officer-selected vehicle regions only."""

from __future__ import annotations

import uuid

from sentinel_anpr.application.dto.vehicle_detection_dto import SelectedVehicleRegionDto
from sentinel_anpr.application.dto.workflow_dto import (
    RunVehicleVerificationWorkflowBatchResult,
    RunVehicleVerificationWorkflowCommand,
    RunVehicleVerificationWorkflowResult,
    WorkflowStatus,
)
from sentinel_anpr.application.ports.intelligent_scene_detection_service import IntelligentSceneDetectionService
from sentinel_anpr.application.ports.outbound.logging_port import LoggingPort
from sentinel_anpr.application.use_cases.orchestration.run_vision_verification_workflow_use_case import (
    RunVisionVerificationWorkflowUseCase,
)
from sentinel_anpr.infrastructure.ai.image_crop import prepare_isolated_vehicle_image


class RunSelectedVehiclesVerificationWorkflowUseCase:
    """Isolate each selected vehicle, then run one independent investigation per crop."""

    def __init__(
        self,
        single_vehicle_workflow: RunVisionVerificationWorkflowUseCase,
        scene_detection_service: IntelligentSceneDetectionService,
        logger: LoggingPort,
    ) -> None:
        self._single_vehicle_workflow = single_vehicle_workflow
        self._scene_detection = scene_detection_service
        self._logger = logger

    def execute(
        self,
        command: RunVehicleVerificationWorkflowCommand,
    ) -> RunVehicleVerificationWorkflowBatchResult:
        workflow_id = command.correlation_id or str(uuid.uuid4())
        regions = command.selected_regions

        if not regions:
            investigation = self._single_vehicle_workflow.execute(command)
            return RunVehicleVerificationWorkflowBatchResult(
                workflow_id=workflow_id,
                investigations=(investigation,),
            )

        investigations: list[RunVehicleVerificationWorkflowResult] = []
        scene_context = self._scene_detection.analyze_scene(command.image_bytes)
        for index, region in enumerate(regions, start=1):
            mask_regions = self._scene_detection.mask_regions_for_selection(
                command.image_bytes,
                region.vehicle_id,
                scene_context=scene_context,
            )
            isolated_bytes = prepare_isolated_vehicle_image(
                command.image_bytes,
                region,
                mask_regions,
            )
            self._logger.info(
                "vehicle_region_isolated",
                workflow_id=workflow_id,
                vehicle_id=region.vehicle_id,
                region_index=index,
                isolated_bytes=len(isolated_bytes),
                masked_regions=len(mask_regions),
                detail="Masked other vehicles/plates and cropped selected vehicle for vision analysis",
            )
            sub_command = RunVehicleVerificationWorkflowCommand(
                officer_id=command.officer_id,
                officer_name=command.officer_name,
                badge_number=command.badge_number,
                officer_rank=command.officer_rank,
                image_bytes=isolated_bytes,
                content_type="image/jpeg",
                original_filename=self._cropped_filename(command.original_filename, index),
                location_label=command.location_label,
                correlation_id=f"{workflow_id}-{region.vehicle_id}",
                selected_regions=None,
                vehicle_region_id=region.vehicle_id,
            )
            investigations.append(self._single_vehicle_workflow.execute(sub_command))

        return RunVehicleVerificationWorkflowBatchResult(
            workflow_id=workflow_id,
            investigations=tuple(investigations),
        )

    @staticmethod
    def _cropped_filename(original_filename: str, index: int) -> str:
        stem = original_filename.rsplit(".", 1)[0] if "." in original_filename else original_filename
        return f"{stem}-vehicle-{index}.jpg"

    @staticmethod
    def summarize_status(
        investigations: tuple[RunVehicleVerificationWorkflowResult, ...],
    ) -> WorkflowStatus:
        if not investigations:
            return WorkflowStatus.FAILED
        if all(item.status == WorkflowStatus.COMPLETED for item in investigations):
            return WorkflowStatus.COMPLETED
        if any(item.status == WorkflowStatus.COMPLETED for item in investigations):
            return WorkflowStatus.COMPLETED
        return WorkflowStatus.FAILED
