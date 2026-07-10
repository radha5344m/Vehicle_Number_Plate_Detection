from sentinel_anpr.application.services.temporary_password_service import generate_temporary_password


def test_generate_temporary_password_meets_complexity_rules() -> None:
    password = generate_temporary_password()
    assert len(password) == 12
    assert any(char.islower() for char in password)
    assert any(char.isupper() for char in password)
    assert any(char.isdigit() for char in password)
    assert any(char in "@#$%!" for char in password)
