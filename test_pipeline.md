# CYOA Chapter Details Test Pipeline

This describes how to run a focused test pipeline that lives in `experiments/cyoa_chapter_details_test.plx`. It uses the same `cyoa` domain as the main pipeline, reuses the existing pipes, and persists outputs via existing Python stubs.

## What it does
Sequence (`test_chapter_details`):
1. `design_blueprint`
2. `character_bible`
3. `chapterize`
4. `chapters_to_outline_items`
5. `chapters_outline_to_text`
6. `expand_chapters_sequential` (uses outline text + character bible for continuity)
7. `persist_chapter_details` (writes `chapter_details.json`)
8. `persist_planning_artifacts` (writes blueprint/characters/chapters JSON)

All concepts are from the main `cyoa` domain; no duplicate concepts are defined here.

## How to run
Example `uv run pipelex execute` inputs:
```json
{
  "brief": {
    "concept": "cyoa.StoryBrief",
    "content": {
      "native_prompt": "A playful fox guides a lost child through a neon forest to find home before midnight.",
      "language": "en",
      "audience": "7-9",
      "genre": "adventure",
      "working_title": "Neon Trails"
    }
  },
  "settings": {
    "concept": "cyoa.Settings",
    "content": {
      "target_runtime_min": 12,
      "advisory_max_states": 30,
      "debug": false,
      "out_dir": "results/planning_demo",
      "text_dir": "results/planning_demo/texts",
      "assets_dir": "results/planning_demo/assets",
      "image_width": 768,
      "image_height": 576,
      "img_guidance": 5.0,
      "img_steps": 25
    }
  }
}
```
Run (PowerShell):
```powershell
$env:PYTHONIOENCODING = 'utf-8'
uv run pipelex execute experiments/cyoa_chapter_details_test.plx --inputs-file inputs.json
```

## Outputs
- `out_dir/planning/<timestamp>/chapter_details.json` (from `persist_chapter_details`)
- `out_dir/planning/<timestamp>/blueprint.json`, `characters.json`, `chapters.json` (from `persist_planning_artifacts`)

## Notes
- Uses existing stubs/helpers from `src/lunii_cyoa/pipe_funcs.py` (`chapters_to_outline_items`, `chapters_outline_to_text`, `persist_chapter_details`, `persist_planning_artifacts`).
- The test pipeline keeps the domain `cyoa` so it can call all main pipes directly without redefining concepts.
- If you want to avoid LLM calls, swap in the stub `cyoa_stub_*` functions in the plx before running.***
