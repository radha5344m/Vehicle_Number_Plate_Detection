"""Assign detected license plates to the nearest vehicle."""

from __future__ import annotations

from dataclasses import dataclass

from sentinel_anpr.domain.vision.value_objects.normalized_bounding_box import NormalizedBoundingBox


@dataclass(frozen=True)
class VehicleDetectionInput:
    """Vehicle bounding box used for plate assignment."""

    vehicle_id: str
    box: NormalizedBoundingBox


@dataclass(frozen=True)
class PlateDetectionInput:
    """License plate bounding box used for plate assignment."""

    plate_id: str
    box: NormalizedBoundingBox
    confidence: float


@dataclass(frozen=True)
class PlateAssignmentResult:
    """Plate assignment outcome."""

    plate_id: str
    vehicle_id: str | None
    confidence: float
    distance: float


class PlateToVehicleAssignmentPolicy:
    """Assign each plate to exactly one nearest vehicle, or mark it unassigned."""

    _MAX_DISTANCE_RATIO = 0.18

    def assign(
        self,
        vehicles: tuple[VehicleDetectionInput, ...],
        plates: tuple[PlateDetectionInput, ...],
        *,
        image_width: int,
        image_height: int,
    ) -> tuple[PlateAssignmentResult, ...]:
        if not plates:
            return ()

        max_distance = self._max_assignment_distance(image_width, image_height)
        candidates: list[tuple[PlateDetectionInput, VehicleDetectionInput, float, float]] = []

        for plate in plates:
            nearest_vehicle, distance = self._nearest_vehicle(
                plate,
                vehicles,
                image_width=image_width,
                image_height=image_height,
            )
            if nearest_vehicle is None or distance > max_distance:
                continue
            confidence = self._assignment_confidence(plate, nearest_vehicle, distance, max_distance)
            candidates.append((plate, nearest_vehicle, distance, confidence))

        candidates.sort(key=lambda item: item[2])
        assigned_plates: set[str] = set()
        vehicle_to_plate: dict[str, PlateDetectionInput] = {}

        for plate, vehicle, distance, confidence in candidates:
            del distance, confidence
            if plate.plate_id in assigned_plates or vehicle.vehicle_id in vehicle_to_plate:
                continue
            vehicle_to_plate[vehicle.vehicle_id] = plate
            assigned_plates.add(plate.plate_id)

        results: list[PlateAssignmentResult] = []
        for plate in plates:
            vehicle_id = next(
                (
                    assigned_vehicle_id
                    for assigned_vehicle_id, assigned_plate in vehicle_to_plate.items()
                    if assigned_plate.plate_id == plate.plate_id
                ),
                None,
            )
            if vehicle_id is not None:
                _, distance = self._nearest_vehicle(
                    plate,
                    vehicles,
                    image_width=image_width,
                    image_height=image_height,
                )
                results.append(
                    PlateAssignmentResult(
                        plate_id=plate.plate_id,
                        vehicle_id=vehicle_id,
                        confidence=self._assignment_confidence(
                            plate,
                            next(v for v in vehicles if v.vehicle_id == vehicle_id),
                            distance,
                            max_distance,
                        ),
                        distance=distance,
                    )
                )
                continue

            _, distance = self._nearest_vehicle(
                plate,
                vehicles,
                image_width=image_width,
                image_height=image_height,
            )
            results.append(
                PlateAssignmentResult(
                    plate_id=plate.plate_id,
                    vehicle_id=None,
                    confidence=0.0,
                    distance=distance,
                )
            )

        return tuple(results)

    @staticmethod
    def _max_assignment_distance(image_width: int, image_height: int) -> float:
        diagonal = (image_width**2 + image_height**2) ** 0.5
        return diagonal * PlateToVehicleAssignmentPolicy._MAX_DISTANCE_RATIO

    @staticmethod
    def _nearest_vehicle(
        plate: PlateDetectionInput,
        vehicles: tuple[VehicleDetectionInput, ...],
        *,
        image_width: int,
        image_height: int,
    ) -> tuple[VehicleDetectionInput | None, float]:
        if not vehicles:
            return None, 1.0

        best_vehicle: VehicleDetectionInput | None = None
        best_distance = float("inf")
        plate_center = plate.box.center()
        plate_x_px = plate_center.x * image_width
        plate_y_px = plate_center.y * image_height

        for vehicle in vehicles:
            if vehicle.box.contains_point(plate_center.x, plate_center.y):
                return vehicle, 0.0

            distance = vehicle.box.distance_to_point_pixels(
                plate_x_px,
                plate_y_px,
                image_width=image_width,
                image_height=image_height,
            )
            if distance < best_distance:
                best_distance = distance
                best_vehicle = vehicle

        return best_vehicle, best_distance

    @staticmethod
    def _assignment_confidence(
        plate: PlateDetectionInput,
        vehicle: VehicleDetectionInput,
        distance: float,
        max_distance: float,
    ) -> float:
        if vehicle.box.contains_point(plate.box.center().x, plate.box.center().y):
            return min(0.98, max(plate.confidence, 0.75))

        proximity = max(0.0, 1.0 - (distance / max_distance))
        return min(0.95, plate.confidence * 0.6 + proximity * 0.4)
