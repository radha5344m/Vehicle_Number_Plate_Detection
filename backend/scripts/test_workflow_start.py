"""Quick smoke test for synchronous workflow response."""

from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

JPEG = Path(__file__).with_name("tmp_test.jpg")
JPEG.write_bytes(
    bytes(
        [
            0xFF,
            0xD8,
            0xFF,
            0xD9,
        ]
    )
)


def main() -> None:
    login_req = urllib.request.Request(
        "http://127.0.0.1:8080/v1/auth/login",
        data=json.dumps({"identifier": "AP001", "password": "Officer@123"}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(login_req) as response:
        login = json.loads(response.read())
    token = login["data"]["access_token"]

    boundary = "----bound"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="vehicle_image"; filename="tmp_test.jpg"\r\n'
        "Content-Type: image/jpeg\r\n\r\n"
    ).encode() + JPEG.read_bytes() + f"\r\n--{boundary}--\r\n".encode()

    correlation_id = "test-corr-smoke"
    req = urllib.request.Request(
        "http://127.0.0.1:8080/v1/workflow/vehicle-verification",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "X-Correlation-ID": correlation_id,
        },
        method="POST",
    )
    started = time.perf_counter()
    with urllib.request.urlopen(req, timeout=300) as response:
        payload = json.loads(response.read())
    elapsed = time.perf_counter() - started
    print(f"elapsed_sec={elapsed:.3f}")
    data = payload.get("data", {})
    print(json.dumps(
        {
            "status": data.get("status"),
            "registration_number": data.get("registration_number"),
            "report_id": data.get("report_id"),
            "failed_stage": data.get("failed_stage"),
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
