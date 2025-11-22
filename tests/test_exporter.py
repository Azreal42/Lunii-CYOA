import json
from pathlib import Path

import pytest

from lunii_cyoa.exporter import StudioExporter


FIXTURE_DIR = Path(__file__).parent


def test_export_creates_story_json(tmp_path: Path) -> None:
    story_path = FIXTURE_DIR / "story_with_random.toml"
    # create dummy assets
    base = story_path.parent / "assets"
    (base / "img").mkdir(parents=True, exist_ok=True)
    (base / "audio").mkdir(parents=True, exist_ok=True)
    for fname in ["crossroad.png", "left.png", "right.png", "back.png", "end.png"]:
        (base / "img" / fname).write_bytes(b"img")
    for fname in ["crossroad.mp3", "left.mp3", "right.mp3", "back.mp3", "end.mp3"]:
        (base / "audio" / fname).write_bytes(b"aud")

    exporter = StudioExporter(story_path=story_path, output_dir=tmp_path, copy_assets=True)
    story_json_path = exporter.export()

    assert story_json_path.exists()
    data = json.loads(story_json_path.read_text(encoding="utf-8"))
    assert "stageNodes" in data and "actionNodes" in data
    assert len(data["stageNodes"]) >= 4
    # assets copied
    assert (tmp_path / "assets" / "img" / "crossroad.png").exists()
    assert (tmp_path / "assets" / "audio" / "crossroad.mp3").exists()


def test_export_fails_on_missing_story(tmp_path: Path) -> None:
    with pytest.raises(Exception):
        StudioExporter(story_path=tmp_path / "missing.toml", output_dir=tmp_path).export()
