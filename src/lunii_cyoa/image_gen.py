"""Thin helper around Google Gemini image generation."""

from __future__ import annotations

from pathlib import Path
import os
from typing import Any

from google import genai
from PIL import Image


def generate_gemini_image(
    prompt: str,
    output_path: str | Path = "generated_image.png",
    model: str = "gemini-2.5-flash-image",
    api_key: str | None = None,
) -> Path:
    """Generate an image with Gemini and save it to disk.

    Args:
        prompt: Natural-language description for the image.
        output_path: Where to write the image (directories are created).
        model: Gemini image model handle (defaults to gemini-2.5-flash-image).
        api_key: Explicit Gemini API key; falls back to env `GEMINI_API_KEY` then `GOOGLE_API_KEY`.

    Returns:
        Path to the written image.

    Raises:
        RuntimeError: If the response contains no inline image data.
    """
    key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    client = genai.Client(api_key=key) if key else genai.Client()
    response = client.models.generate_content(model=model, contents=[prompt])

    for part in response.parts:
        if getattr(part, "inline_data", None) is None:
            continue
        image: Image.Image = part.as_image()
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path)
        return path

    raise RuntimeError("Gemini response contained no image data.")
