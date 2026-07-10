"""OpenCV heuristic license plate detection."""

from __future__ import annotations

import io
import uuid

import cv2
import numpy as np
from PIL import Image

from sentinel_anpr.application.dto.plate_detection_dto import DetectedPlateDto
from sentinel_anpr.application.ports.license_plate_detection_service import LicensePlateDetectionService

_MIN_ASPECT = 1.8
_MAX_ASPECT = 7.5
_MIN_AREA_RATIO = 0.0008
_MAX_AREA_RATIO = 0.08
_MIN_WIDTH_PX = 28
_NMS_IOU_THRESHOLD = 0.35


class OpenCvLicensePlateDetectionService(LicensePlateDetectionService):
    """Detect rectangular plate-like regions using contour heuristics."""

    def detect_plates(self, image_bytes: bytes) -> tuple[DetectedPlateDto, ...]:
        image = self._load_bgr_image(image_bytes)
        height, width = image.shape[:2]
        candidates = self._find_plate_candidates(image, width, height)
        if not candidates:
            return ()

        candidates.sort(key=lambda item: item[4], reverse=True)
        selected = self._non_max_suppression(candidates)
        return tuple(
            DetectedPlateDto(
                plate_id=str(uuid.uuid4()),
                x=left / width,
                y=top / height,
                width=box_width / width,
                height=box_height / height,
                confidence=round(confidence, 4),
                text=None,
            )
            for left, top, box_width, box_height, confidence in selected
        )

    def _find_plate_candidates(
        self,
        image: np.ndarray,
        width: int,
        height: int,
    ) -> list[tuple[int, int, int, int, float]]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 60, 180)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        image_area = width * height
        candidates: list[tuple[int, int, int, int, float]] = []
        for contour in contours:
            candidate = self._evaluate_contour(contour, image_area)
            if candidate is not None:
                candidates.append(candidate)

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        bright_mask = cv2.inRange(hsv, (0, 0, 145), (180, 90, 255))
        bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_CLOSE, kernel, iterations=1)
        contours, _ = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            candidate = self._evaluate_contour(contour, image_area, min_confidence=0.45)
            if candidate is not None:
                candidates.append(candidate)

        return candidates

    def _evaluate_contour(
        self,
        contour: np.ndarray,
        image_area: int,
        *,
        min_confidence: float = 0.5,
    ) -> tuple[int, int, int, int, float] | None:
        left, top, box_width, box_height = cv2.boundingRect(contour)
        area = box_width * box_height
        if area < image_area * _MIN_AREA_RATIO or area > image_area * _MAX_AREA_RATIO:
            return None
        if box_width < _MIN_WIDTH_PX or box_height < 8:
            return None

        aspect_ratio = box_width / box_height if box_height else 0
        if aspect_ratio < _MIN_ASPECT or aspect_ratio > _MAX_ASPECT:
            return None

        confidence = min(0.93, min_confidence + (area / image_area) * 4)
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
            overlaps = any(
                OpenCvLicensePlateDetectionService._intersection_over_union(
                    (left, top, box_width, box_height),
                    (item[0], item[1], item[2], item[3]),
                )
                > overlap_threshold
                for item in selected
            )
            if overlaps:
                continue
            selected.append(candidate)
        return selected

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
    def _load_bgr_image(image_bytes: bytes) -> np.ndarray:
        with Image.open(io.BytesIO(image_bytes)) as image:
            rgb = np.array(image.convert("RGB"))
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
