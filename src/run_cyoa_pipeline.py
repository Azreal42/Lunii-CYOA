"""Interactive runner for the CYOA Pipelex pipeline."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict

from pipelex import pretty_print
from pipelex.pipe_run.pipe_run_mode import PipeRunMode
from pipelex.pipelex import Pipelex
from pipelex.pipeline.execute import execute_pipeline
from pipelex.system.runtime import IntegrationMode


def prompt_text(prompt: str, default: str | None = None, required: bool = True) -> str | None:
    """Prompt for a text value; return None when optional and left blank."""
    suffix = f" [{default}]" if default else ""
    while True:
        raw = input(f"{prompt}{suffix}: ").strip()
        if raw:
            return raw
        if default is not None:
            return default
        if not required:
            return None
        print("This value is required.")


def prompt_int(prompt: str, default: int | None = None, min_value: int | None = None) -> int:
    """Prompt for an integer with optional default and lower bound."""
    suffix = f" [{default}]" if default is not None else ""
    while True:
        raw = input(f"{prompt}{suffix}: ").strip()
        if not raw:
            if default is not None:
                return default
            print("Please enter a number.")
            continue
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a valid integer.")
            continue
        if min_value is not None and value < min_value:
            print(f"Value must be at least {min_value}.")
            continue
        return value


def prompt_bool(prompt: str, default: bool = False) -> bool:
    """Prompt for a boolean value with a default."""
    default_hint = "Y/n" if default else "y/N"
    while True:
        raw = input(f"{prompt} ({default_hint}): ").strip().lower()
        if not raw:
            return default
        if raw in {"y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False
        print("Please answer yes or no.")


def collect_story_brief() -> Dict[str, str]:
    """Collect StoryBrief inputs required by the pipeline."""
    brief: Dict[str, str] = {
        "native_prompt": prompt_text("Story idea / brief", required=True) or "",
        "language": prompt_text("Language (BCP-47, e.g., en, fr)", default="en", required=True) or "en",
    }
    for field in ("audience", "genre", "working_title"):
        value = prompt_text(f"{field.replace('_', ' ').title()} (optional)", required=False)
        if value:
            brief[field] = value
    return brief


def collect_settings() -> Dict[str, Any]:
    """Collect Settings inputs with sensible defaults."""
    return {
        "target_runtime_min": prompt_int("Target runtime (minutes)", default=60, min_value=1),
        "max_states_hint": prompt_int("Max logical states hint", default=200, min_value=1),
        "debug": prompt_bool("Enable debug artifacts", default=True),
        "out_dir": prompt_text("Output directory", default="out", required=True) or "out",
        "audio_ext": prompt_text("Audio extension", default="mp3", required=True) or "mp3",
        "image_ext": prompt_text("Image extension", default="png", required=True) or "png",
    }


def load_plx_content() -> str:
    """Load the bundled CYOA pipeline definition."""
    plx_path = Path(__file__).resolve().parent / "pipelines" / "cyoa.plx"
    if not plx_path.exists():
        print(f"Cannot find pipeline bundle at {plx_path}")
        sys.exit(1)
    return plx_path.read_text(encoding="utf-8")


async def run_pipeline(plx_content: str, inputs: Dict[str, Any]) -> None:
    """Execute the pipeline and pretty-print the output."""
    pipe_output = await execute_pipeline(
        plx_content=plx_content,
        inputs=inputs,
        pipe_run_mode=PipeRunMode.LIVE,
        search_domains=["cyoa"],
    )
    pretty_print(pipe_output, title="CYOA bundle output")


def main() -> None:
    """Entry point: gather inputs then run the CYOA pipeline."""
    print("CYOA pipeline runner (Pipelex)")
    brief = collect_story_brief()
    settings = collect_settings()
    plx_content = load_plx_content()

    Pipelex.make(integration_mode=IntegrationMode.PYTHON)
    asyncio.run(run_pipeline(plx_content=plx_content, inputs={"brief": brief, "settings": settings}))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled by user.")
