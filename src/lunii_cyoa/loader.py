from __future__ import annotations

from pathlib import Path
import tomlkit
from pydantic import ValidationError

from .models import StoryDocument


class StoryLoadError(Exception):
    """Raised when a TOML story cannot be loaded or validated."""


def load_story(path: Path) -> StoryDocument:
    """
    Load and validate a story TOML file into a StoryDocument.

    Args:
        path: Path to the TOML file.

    Returns:
        StoryDocument parsed from the TOML.

    Raises:
        StoryLoadError: if the file cannot be read or validation fails.
    """
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise StoryLoadError(f"Failed to read TOML file '{path}': {exc}") from exc

    try:
        parsed = tomlkit.parse(content)
    except Exception as exc:  # tomlkit raises generic Exception subclasses
        raise StoryLoadError(f"Failed to parse TOML file '{path}': {exc}") from exc

    try:
        return StoryDocument.model_validate(parsed)
    except ValidationError as exc:
        raise StoryLoadError(f"Validation error in '{path}': {exc}") from exc
