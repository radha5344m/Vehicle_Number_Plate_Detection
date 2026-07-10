"""Image metadata inspection port."""

from typing import Protocol


class ImageInspectorPort(Protocol):
    """Read image dimensions and format from raw bytes."""

    def get_dimensions(self, content: bytes) -> tuple[int, int]: ...

    def detect_content_type(self, content: bytes, declared_content_type: str) -> str: ...
