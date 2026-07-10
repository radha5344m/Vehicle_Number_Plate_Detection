"""OpenCV contour-based vehicle detection (no external model download)."""

from __future__ import annotations

import io
import uuid

import cv2
import numpy as np
from PIL import Image

from sentinel_anpr.application.dto.vehicle_detection_dto import DetectedVehicleDto
from sentinel_anpr.application.ports.vehicle_detection_service import VehicleDetectionService

_MIN_AREA_RATIO = 0.015
_MAX_AREA_RATIO = 0.42
_MIN_BOX_PX = 36
_PADDING_PX = 15
_NMS_IOU_THRESHOLD = 0.22


class OpenCvVehicleDetectionService(VehicleDetectionService):
    """Detect likely vehicle regions using classical computer vision."""

    def detect_vehicles(self, image_bytes: bytes) -> tuple[DetectedVehicleDto, ...]:
        image = self._load_bgr_image(image_bytes)
        height, width = image.shape[:2]
        candidates = self._find_vehicle_candidates(image, width, height)
        if not candidates:
            return self._fallback_single_vehicle(width, height)

        candidates.sort(key=lambda item: item[4], reverse=True)
        selected = self._non_max_suppression(candidates)
        vehicles = tuple(
            self._to_detected_vehicle(left, top, box_width, box_height, confidence, width, height)
            for left, top, box_width, box_height, confidence in selected
        )
        return vehicles or self._fallback_single_vehicle(width, height)

    def _to_detected_vehicle(
        self,
        left: int,
        top: int,
        box_width: int,
        box_height: int,
        confidence: float,
        image_width: int,
        image_height: int,
    ) -> DetectedVehicleDto:
        padded_left, padded_top, padded_width, padded_height = self._apply_padding(
            left,
            top,
            box_width,
            box_height,
            image_width,
            image_height,
        )
        return DetectedVehicleDto(
            vehicle_id=str(uuid.uuid4()),
            x=padded_left / image_width,
            y=padded_top / image_height,
            width=padded_width / image_width,
            height=padded_height / image_height,
            confidence=round(confidence, 4),
            vehicle_type=self._classify_vehicle_type(box_width, box_height, image_width, image_height),
        )

    @staticmethod
    def _apply_padding(
        left: int,
        top: int,
        box_width: int,
        box_height: int,
        image_width: int,
        image_height: int,
        padding_px: int = _PADDING_PX,
    ) -> tuple[int, int, int, int]:
        padded_left = max(0, left - padding_px)
        padded_top = max(0, top - padding_px)
        padded_right = min(image_width, left + box_width + padding_px)
        padded_bottom = min(image_height, top + box_height + padding_px)
        return (
            padded_left,
            padded_top,
            max(1, padded_right - padded_left),
            max(1, padded_bottom - padded_top),
        )

    def _find_vehicle_candidates(
        self,
        image: np.ndarray,
        width: int,
        height: int,
    ) -> list[tuple[int, int, int, int, float]]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 40, 140)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        image_area = width * height
        candidates: list[tuple[int, int, int, int, float]] = []
        for contour in contours:
            candidate = self._evaluate_contour(contour, image_area)
            if candidate is not None:
                candidates.append(candidate)

        if candidates:
            return candidates

        thresh = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            21,
            5,
        )
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            candidate = self._evaluate_contour(contour, image_area, min_area_ratio=0.03)
            if candidate is not None:
                candidates.append(candidate)

        return candidates

    def _evaluate_contour(
        self,
        contour: np.ndarray,
        image_area: int,
        *,
        min_area_ratio: float = _MIN_AREA_RATIO,
    ) -> tuple[int, int, int, int, float] | None:
        left, top, box_width, box_height = cv2.boundingRect(contour)
        area = box_width * box_height
        if area < image_area * min_area_ratio or area > image_area * _MAX_AREA_RATIO:
            return None
        if box_width < _MIN_BOX_PX or box_height < _MIN_BOX_PX:
            return None

        aspect_ratio = box_width / box_height if box_height else 0
        if aspect_ratio < 0.35 or aspect_ratio > 3.8:
            return None

        confidence = min(0.92, 0.4 + (area / image_area))
        return left, top, box_width, box_height, confidence

    @staticmethod
    def _non_max_suppression(
        boxes: list[tuple[int, int, int, int, float]],
        overlap_threshold: float = _NMS_IOU_THRESHOLD,
    ) -> list[tuple[int, int, int, int, float]]:
        if not boxes:
            return []

        ordered = sorted(boxes, key=lambda item: item[4], reverse=True)
        selected: list[tuple[int, int, int, int, float]] = []
        for candidate in ordered:
            left, top, box_width, box_height, confidence = candidate
            overlaps_existing = any(
                OpenCvVehicleDetectionService._intersection_over_union(
                    (left, top, box_width, box_height),
                    (item[0], item[1], item[2], item[3]),
                )
                > overlap_threshold
                or OpenCvVehicleDetectionService._contains_center(
                    (left, top, box_width, box_height),
                    (item[0], item[1], item[2], item[3]),
                )
                or OpenCvVehicleDetectionService._contains_center(
                    (item[0], item[1], item[2], item[3]),
                    (left, top, box_width, box_height),
                )
                for item in selected
            )
            if overlaps_existing:
                continue
            selected.append(candidate)
        return selected

    @staticmethod
    def _contains_center(outer: tuple[int, int, int, int], inner: tuple[int, int, int, int]) -> bool:
        inner_left, inner_top, inner_width, inner_height = inner
        center_x = inner_left + (inner_width / 2)
        center_y = inner_top + (inner_height / 2)
        outer_left, outer_top, outer_width, outer_height = outer
        return (
            outer_left <= center_x <= outer_left + outer_width
            and outer_top <= center_y <= outer_top + outer_height
        )

    @staticmethod
    def _intersection_over_union(
        first: tuple[int, int, int, int],
        second: tuple[int, int, int, int],
    ) -> float:
        left_a, top_a, width_a, height_a = first
        left_b, top_b, width_b, height_b = second
        right_a = left_a + width_a
        bottom_a = top_a + height_a
        right_b = left_b + width_b
        bottom_b = top_b + height_b

        inter_left = max(left_a, left_b)
        inter_top = max(top_a, top_b)
        inter_right = min(right_a, right_b)
        inter_bottom = min(bottom_a, bottom_b)
        if inter_right <= inter_left or inter_bottom <= inter_top:
            return 0.0

        inter_area = (inter_right - inter_left) * (inter_bottom - inter_top)
        union_area = (width_a * height_a) + (width_b * height_b) - inter_area
        if union_area <= 0:
            return 0.0
        return inter_area / union_area

    @staticmethod
    def _classify_vehicle_type(box_width: int, box_height: int, image_width: int, image_height: int) -> str:
        aspect_ratio = box_width / box_height if box_height else 1.0
        relative_width = box_width / image_width if image_width else 0
        relative_height = box_height / image_height if image_height else 0

        if aspect_ratio < 0.75:
            return "scooter" if box_width < box_height * 0.65 else "motorcycle"
        if aspect_ratio > 2.4 and relative_height > 0.35:
            return "bus" if relative_width > 0.55 else "truck"
        if aspect_ratio >= 1.1 and relative_width > 0.4:
            return "suv"
        return "car"

    @staticmethod
    def _load_bgr_image(image_bytes: bytes) -> np.ndarray:
        with Image.open(io.BytesIO(image_bytes)) as image:
            rgb = np.array(image.convert("RGB"))
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    def _fallback_single_vehicle(self, image_width: int, image_height: int) -> tuple[DetectedVehicleDto, ...]:
        margin_x = max(_PADDING_PX, int(image_width * 0.08))
        margin_y = max(_PADDING_PX, int(image_height * 0.08))
        left = margin_x
        top = margin_y
        box_width = max(1, image_width - (2 * margin_x))
        box_height = max(1, image_height - (2 * margin_y))
        return (
            self._to_detected_vehicle(
                left,
                top,
                box_width,
                box_height,
                0.5,
                image_width,
                image_height,
            ),
        )
