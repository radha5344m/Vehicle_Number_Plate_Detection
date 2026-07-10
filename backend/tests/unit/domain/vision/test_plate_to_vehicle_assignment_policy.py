"""Plate-to-vehicle assignment policy tests."""

from sentinel_anpr.domain.vision.services.plate_to_vehicle_assignment_policy import (
    PlateDetectionInput,
    PlateToVehicleAssignmentPolicy,
    VehicleDetectionInput,
)
from sentinel_anpr.domain.vision.value_objects.normalized_bounding_box import NormalizedBoundingBox


def test_assigns_plate_to_nearest_vehicle() -> None:
    policy = PlateToVehicleAssignmentPolicy()
    vehicles = (
        VehicleDetectionInput(
            vehicle_id="vehicle-1",
            box=NormalizedBoundingBox(x=0.1, y=0.2, width=0.3, height=0.4),
        ),
        VehicleDetectionInput(
            vehicle_id="vehicle-2",
            box=NormalizedBoundingBox(x=0.55, y=0.2, width=0.3, height=0.4),
        ),
    )
    plates = (
        PlateDetectionInput(
            plate_id="plate-1",
            box=NormalizedBoundingBox(x=0.18, y=0.5, width=0.14, height=0.05),
            confidence=0.9,
        ),
        PlateDetectionInput(
            plate_id="plate-2",
            box=NormalizedBoundingBox(x=0.62, y=0.52, width=0.13, height=0.05),
            confidence=0.88,
        ),
    )

    assignments = policy.assign(vehicles, plates, image_width=1280, image_height=960)

    by_plate = {assignment.plate_id: assignment for assignment in assignments}
    assert by_plate["plate-1"].vehicle_id == "vehicle-1"
    assert by_plate["plate-2"].vehicle_id == "vehicle-2"


def test_marks_distant_plate_as_unassigned() -> None:
    policy = PlateToVehicleAssignmentPolicy()
    vehicles = (
        VehicleDetectionInput(
            vehicle_id="vehicle-1",
            box=NormalizedBoundingBox(x=0.1, y=0.2, width=0.2, height=0.3),
        ),
    )
    plates = (
        PlateDetectionInput(
            plate_id="plate-1",
            box=NormalizedBoundingBox(x=0.8, y=0.8, width=0.1, height=0.04),
            confidence=0.7,
        ),
    )

    assignments = policy.assign(vehicles, plates, image_width=1280, image_height=960)

    assert assignments[0].vehicle_id is None
