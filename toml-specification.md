# CYOA Story TOML Specification

Purpose: define the TOML schema that expresses a choose-your-own-adventure story before compilation to Lunii formats.

## Encoding & General Rules
- File MUST be valid TOML 1.0 encoded in UTF-8.
- Paths are relative to the TOML file unless otherwise stated.
- Identifiers (`id`, file names) are case-sensitive; prefer lower snake_case for node ids.
- Duplicate logical ids (nodes or choices) are invalid.
- Dangling targets (choice/random targets that do not exist) are invalid.

## Top-Level Sections
- `[story]` — story metadata.
- `[assets]` — asset configuration and conversion hints.
- `[state.*]` — declared state variables (int/bool/enum).
- `[[nodes]]` — logical graph nodes.

## `[story]`
Required:
- `id` (string) — stable identifier.
- `title` (table) — localized titles, e.g. `title.en = "Dungeon"`; at least one language entry.
- `start_node` (string) — logical id of the starting node.

Optional:
- `version` (string) — semantic or arbitrary version.
- `thumbnail` (string) — path under `assets.base_dir`.
- `output_uuid` (string, 8 hex chars) — fixed UUID to embed; generated if absent.
- `default_value_<var>` (int) — initial value for a declared int variable (falls back to its `min` if omitted).

## `[assets]`
- `base_dir` (string) — root directory for media assets.
- `audio_ext` (string) — extension used in TOML references (e.g., `"mp3"`).
- `image_ext` (string) — extension used in TOML references (e.g., `"png"`).
- `audio_target` (string) — conversion target (e.g., `"mp3_44k1_mono_64kbps"`).
- `image_target` (string) — conversion target (e.g., `"bmp_320x240_4bpp"`).
- Tool hints: `ffmpeg`, `imagemagick` (string) — executable names if non-default.
- `auto_generate_menu_audio` / `auto_generate_menu_image` (bool) — allow toolchain to fill missing menu assets.

## State declarations `[state.<name>]`
- `type` (string): `"int"`, `"bool"`, or `"enum"`.
- For `int`: `min` (int), `max` (int), optional `default` (int; defaults to `min` or `default_value_<name>` from `[story]`).
- For `bool`: no extra fields; defaults to `false`.
- For `enum`: `values` (array of strings), optional `default` (string; defaults to first value).

## Logical nodes `[[nodes]]`
Common fields:
- `id` (string) — unique logical identifier.
- `kind` (string) — `"story"`, `"menu"`, `"branch"`, or `"random"`.
- `bg` (string) — background image path (under `assets.base_dir`).
- `audio` (string) — narration audio path.

### Menu / Branch choices
Add `[[nodes.choices]]` entries:
- `id` (string) — unique within the node.
- `label_audio` (string, optional) — audio for the choice label.
- `label_text` (string, optional) — text label for debugging/tooling.
- `target` (string) — logical node id to jump to.
- `effects` (array of tables, optional) — state mutations applied on transition.
- `guard` (string, optional) — boolean expression evaluated in the current state.

Effects:
- Table fields: `var` (string), `op` (one of `"="`, `"+="`, `"-="`), `value` (type-compatible).
- Effects are applied in order; resulting state must remain within declared bounds.

Guards:
- Literals: integers, `true`, `false`.
- Operators: `==`, `!=`, `<`, `<=`, `>`, `>=`, `&&`, `||`, `!`.
- Parentheses allowed; precedence: `!` > comparisons > `&&` > `||`.

### Random nodes
- `kind = "random"` uses `[[nodes.random.options]]`.
- Each option: `target` (string) — logical node id.
- Selection is uniform across options; weights are not supported by Lunii.

### Story nodes
- `kind = "story"` may optionally include `target` (string) for auto-advance; if absent, it is terminal.

## Validation expectations
- All referenced assets must exist after applying `assets.base_dir` and extensions.
- Guards must reference declared state variables.
- Every logical node must be reachable from `start_node` after state expansion; unreachable nodes should trigger a warning or error depending on tooling policy.

## Minimal example
```toml
[story]
id = "dungeon-three-hearts"
start_node = "entrance"
title.en = "Dungeon of Three Hearts"

[assets]
base_dir = "assets"
audio_ext = "mp3"
image_ext = "png"
audio_target = "mp3_44k1_mono_64kbps"
image_target = "bmp_320x240_4bpp"

[state.hp]
type = "int"
min = 0
max = 3
default = 3

[state.key]
type = "bool"

[[nodes]]
id = "entrance"
kind = "menu"
bg = "img/entrance.png"
audio = "audio/entrance.mp3"

[[nodes.choices]]
id = "to_goblin"
label_text = "Goblin room"
target = "goblin"
effects = [{ var = "hp", op = "-=", value = 1 }]

[[nodes]]
id = "goblin"
kind = "random"
bg = "img/goblin.png"
audio = "audio/goblin_intro.mp3"

[[nodes.random.options]]
target = "treasure_small"

[[nodes.random.options]]
target = "treasure_big"
```
