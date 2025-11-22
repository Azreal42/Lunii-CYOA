from pathlib import Path
from typing import Iterable

from lunii_cyoa.tts import DEFAULT_OUTPUT_FORMAT, synthesize_to_file


class FakeTextToSpeech:
    def __init__(self, chunks: Iterable[bytes]) -> None:
        self.chunks = list(chunks)
        self.calls: list[dict[str, str]] = []

    def convert(self, *, text: str, voice_id: str, model_id: str, output_format: str) -> Iterable[bytes]:
        self.calls.append({"text": text, "voice_id": voice_id, "model_id": model_id, "output_format": output_format})
        return self.chunks


class FakeElevenLabsClient:
    def __init__(self, chunks: Iterable[bytes]) -> None:
        self._text_to_speech = FakeTextToSpeech(chunks)

    @property
    def text_to_speech(self) -> FakeTextToSpeech:
        return self._text_to_speech


def test_synthesize_to_file_writes_output(tmp_path: Path) -> None:
    audio_chunks = [b"hello ", b"world"]
    client = FakeElevenLabsClient(audio_chunks)
    output_path = tmp_path / "sample.mp3"

    synthesize_to_file(
        text="Hello!",
        voice_id="voice-123",
        model_id="eleven_multilingual_v2",
        output_path=output_path,
        client=client,
    )

    assert output_path.exists()
    assert output_path.read_bytes() == b"hello world"
    assert client.text_to_speech.calls == [
        {"text": "Hello!", "voice_id": "voice-123", "model_id": "eleven_multilingual_v2", "output_format": DEFAULT_OUTPUT_FORMAT},
    ]
