from pathlib import Path

import pytest

from lunii_cyoa.loader import load_story, StoryLoadError
from lunii_cyoa.models import StoryDocument


FIXTURE_DIR = Path(__file__).parent


@pytest.mark.parametrize(
    "filename,expected_start",
    [
        ("story_minimal.toml", "intro"),
        ("story_with_choices.toml", "entrance"),
        ("story_with_random.toml", "crossroad"),
        ("story_with_assets_and_guard.toml", "gate"),
    ],
)
def test_load_valid_stories(filename: str, expected_start: str) -> None:
    path = FIXTURE_DIR / filename
    story = load_story(path)
    assert isinstance(story, StoryDocument)
    assert story.story.start_node == expected_start
    assert story.nodes, "nodes should not be empty"


def test_random_has_uniform_options() -> None:
    path = FIXTURE_DIR / "story_with_random.toml"
    story = load_story(path)
    random_nodes = [n for n in story.nodes if n.kind == "random"]
    assert random_nodes, "expected at least one random node"
    options = random_nodes[0].random.get("options", [])
    assert len(options) == 3
    assert {opt.target for opt in options} == {"left_path", "right_path", "backtrack"}


def test_invalid_reference_raises() -> None:
    bad_toml = FIXTURE_DIR / "bad_missing_target.toml"
    bad_toml.write_text(
        """
[story]
id = "bad"
start_node = "start"
title.en = "Bad"

[assets]
base_dir = "assets"
audio_ext = "mp3"
image_ext = "png"

[[nodes]]
id = "start"
kind = "story"
bg = "img/a.png"
audio = "audio/a.mp3"
target = "missing"
""",
        encoding="utf-8",
    )
    with pytest.raises(StoryLoadError):
        load_story(bad_toml)
    bad_toml.unlink()
