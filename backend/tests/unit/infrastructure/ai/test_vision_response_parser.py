"""Unit tests for vision response JSON parsing."""

from sentinel_anpr.infrastructure.ai.vision_response_parser import parse_vision_json


def test_parse_valid_json() -> None:
    payload = parse_vision_json(
        '{"registration_number":"KL02AR4411","vehicle_color":"white",'
        '"vehicle_type":"car","brand":"Toyota","model":"Innova",'
        '"confidence":0.91,"explanation":"Clear front plate"}'
    )
    assert payload is not None
    assert payload["registration_number"] == "KL02AR4411"
    assert payload["confidence"] == 0.91


def test_parse_markdown_fenced_json() -> None:
    payload = parse_vision_json(
        "```json\n"
        '{"registration_number":"AP09AB1234","vehicle_color":"black",'
        '"vehicle_type":"car","brand":"Honda","model":"City",'
        '"confidence":0.8,"explanation":"ok"}\n'
        "```"
    )
    assert payload is not None
    assert payload["brand"] == "Honda"


def test_parse_truncated_json_fragment() -> None:
    payload = parse_vision_json(
        '{"registration_number":"AP09AB1234","vehicle_color":"white",'
        '"vehicle_type":"car","brand":"Toyota","model":"Innova",'
        '"confidence":0.91,"explanation":"Clear front plate"}\n}'
    )
    assert payload is not None
    assert payload["registration_number"] == "AP09AB1234"
