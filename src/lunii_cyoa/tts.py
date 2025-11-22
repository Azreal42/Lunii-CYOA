from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Protocol, runtime_checkable

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

AudioContent = bytes | bytearray | Iterable[bytes]

DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"


@runtime_checkable
class TextToSpeechAPI(Protocol):
    """Protocol for ElevenLabs text-to-speech API surface used by the helper."""

    def convert(self, *, text: str, voice_id: str, model_id: str, output_format: str) -> AudioContent:  # noqa: D401
        """Convert text to speech using the provided ElevenLabs model."""
        ...


@runtime_checkable
class ElevenLabsClient(Protocol):
    """Protocol to describe the ElevenLabs client shape used in this module."""

    @property
    def text_to_speech(self) -> TextToSpeechAPI:
        """Expose the text-to-speech API surface."""
        ...


def build_elevenlabs_client(api_key: str | None = None) -> ElevenLabsClient:
    """Instantiate an ElevenLabs client using the provided or environment API key."""

    load_dotenv()
    resolved_key = api_key or os.getenv("ELEVENLABS_API_KEY")
    if resolved_key is None:
        raise ValueError("ELEVENLABS_API_KEY is not set. Provide api_key or set the environment variable.")
    return ElevenLabs(api_key=resolved_key)


def synthesize_to_file(
    text: str,
    voice_id: str,
    model_id: str,
    output_path: Path,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
    client: ElevenLabsClient | None = None,
) -> Path:
    """Generate speech audio to a file using ElevenLabs."""

    tts_client = client or build_elevenlabs_client()
    audio = tts_client.text_to_speech.convert(text=text, voice_id=voice_id, model_id=model_id, output_format=output_format)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _write_audio_content(audio, output_path)
    return output_path


def _write_audio_content(content: AudioContent, output_path: Path) -> None:
    """Write the provided audio content (bytes or iterable of bytes) to the given path."""

    with output_path.open("wb") as output_file:
        if isinstance(content, (bytes, bytearray)):
            output_file.write(content)
            return

        for chunk in content:
            output_file.write(chunk)
