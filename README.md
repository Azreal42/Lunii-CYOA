# Lunii-CYOA

Goal: build a pipeline that turns authored choose-your-own-adventure content into Lunii-ready packs.

## Objectives
- Author stories in a TOML format (`toml-specification.md`) that captures nodes, state, assets, and navigation.
- Use a pipeline (Pipelex-based) to generate `story.toml` plus media under `assets/`.
- Compile TOML into an internal representation, expand stateful graphs, and emit Lunii pack formats (FS/STUdio layout, then `.plain.pk`).
- Integrate TTS (e.g., ElevenLabs) and image generation steps where useful, but keep the TOML the single source of truth.

## Key Artifact
- Story schema: `toml-specification.md` (this repo) — normative spec for `story.toml`.

## High-Level Flow
1. Write or generate TOML + assets according to the spec.
2. Validate TOML (guards, effects, asset presence).
3. Expand logical graph into physical nodes (state combinations).
4. Convert media (ffmpeg/ImageMagick targets).
5. Package into Lunii formats and transfer with Lunii tooling.

## Next References
- TOML spec: `toml-specification.md`
- Pack tooling context: see root `README.md` and `Lunii.PACKS.index.md` in the workspace.
