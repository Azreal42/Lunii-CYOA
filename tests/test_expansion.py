from pathlib import Path

import pytest

from lunii_cyoa.loader import load_story
from lunii_cyoa.expansion import expand_story, ExpansionError, StoryExpander


FIXTURE_DIR = Path(__file__).parent


def test_expand_linear_story() -> None:
    doc = load_story(FIXTURE_DIR / "story_minimal.toml")
    result = expand_story(doc)
    assert len(result.physical_nodes) == 2  # intro and end
    assert not result.unreachable_logical
    assert len(result.dead_ends) == 1  # end only


def test_expand_choices_with_guards_and_effects() -> None:
    doc = load_story(FIXTURE_DIR / "story_with_choices.toml")
    result = expand_story(doc)
    logical_ids = {n.logical_id for n in result.physical_nodes}
    assert {"entrance", "hall", "treasure", "end"} <= logical_ids
    # hall should appear with both key states
    hall_states = [n.state for n in result.physical_nodes if n.logical_id == "hall"]
    assert any(s["key"] is True for s in hall_states)
    assert any(s["key"] is False for s in hall_states)


def test_expand_random_node() -> None:
    doc = load_story(FIXTURE_DIR / "story_with_random.toml")
    result = expand_story(doc)
    logical_ids = {n.logical_id for n in result.physical_nodes}
    assert {"crossroad", "left_path", "right_path", "backtrack", "end"} <= logical_ids
    # three outgoing from crossroad
    cross = next(n for n in result.physical_nodes if n.logical_id == "crossroad")
    assert len(cross.outgoing) == 3


def test_invalid_guard_variable_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad_guard.toml"
    bad.write_text(
        """
[story]
id = "bad-guard"
start_node = "start"
title.en = "Bad Guard"

[assets]
base_dir = "assets"
audio_ext = "mp3"
image_ext = "png"

[state.hp]
type = "int"
min = 0
max = 3

[[nodes]]
id = "start"
kind = "menu"
bg = "img/a.png"
audio = "audio/a.mp3"

[[nodes.choices]]
id = "go"
target = "end"
guard = "missing > 0"

[[nodes]]
id = "end"
kind = "story"
bg = "img/b.png"
audio = "audio/b.mp3"
""",
        encoding="utf-8",
    )
    doc = load_story(bad)
    with pytest.raises(ExpansionError):
        expand_story(doc)


def test_effect_out_of_bounds_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad_effect.toml"
    bad.write_text(
        """
[story]
id = "bad-effect"
start_node = "start"
title.en = "Bad Effect"

[assets]
base_dir = "assets"
audio_ext = "mp3"
image_ext = "png"

[state.hp]
type = "int"
min = 0
max = 3
default = 3

[[nodes]]
id = "start"
kind = "menu"
bg = "img/a.png"
audio = "audio/a.mp3"

[[nodes.choices]]
id = "hurt"
target = "end"
effects = [{ var = "hp", op = "-=", value = 10 }]

[[nodes]]
id = "end"
kind = "story"
bg = "img/b.png"
audio = "audio/b.mp3"
""",
        encoding="utf-8",
    )
    doc = load_story(bad)
    with pytest.raises(ExpansionError):
        expand_story(doc)
