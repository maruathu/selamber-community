from __future__ import annotations

from app.config.settings import settings
from app.utils.text import sanitize_text, slugify


def test_settings_default_values() -> None:
    assert settings.app_name == "Selamber Community"


def test_text_helpers() -> None:
    assert sanitize_text("  hello   world  ") == "hello world"
    assert slugify("Hello World!") == "hello-world"
