"""
ai.device_features
-------------------
Integration points for features that need real device hardware or a paid
external service to actually work: camera OCR, voice I/O, and cloud backup.

These are deliberately NOT faked. A stub that silently returns a fixed
string when you point the camera at an equation would be worse than no
feature at all — it would look like it works and then be wrong on real
input. Each function below raises NotImplementedError with a note on what
real integration it needs, so the UI layer can catch that and show
tr("..._coming_soon") instead of misleading the user.

To make these real:

OCR (camera equation scanner):
    - Use `plyer.camera` (cross-platform Kivy camera access) to capture a frame
    - Send the image to a math-OCR model. Two realistic options:
        a) Mathpix API (https://mathpix.com/ocr) - purpose-built for math OCR,
           returns LaTeX directly. Paid API, needs an API key.
        b) A local on-device model (e.g. a fine-tuned TrOCR) - works offline
           but needs a real training/eval pipeline, not a stub.
    - Feed the returned LaTeX/text into core.cas (once built) via
      sympy.parsing.latex.parse_latex()

Voice input/output:
    - Input: `plyer.stt` or Android's SpeechRecognizer / iOS Speech framework
      via pyjnius/pyobjus bridges - genuinely platform-specific, no pure-Python
      cross-platform option exists today.
    - Output: `plyer.tts` for basic playback, or a proper TTS engine if you
      want it to read out formulas rather than raw text.

Cloud backup:
    - Needs an actual backend: Firebase, a small FastAPI service + Postgres,
      or similar. This is a product decision (which provider, auth model,
      free-tier limits) as much as a coding task - I've left the interface
      shape below so the local HistoryStore can be swapped for a synced
      backend without changing UI code, but the backend itself has to be
      built and provisioned by you.
"""
from __future__ import annotations


class FeatureNotAvailable(Exception):
    """Raised by device-feature stubs. UI layer should catch this and show a friendly message."""


def scan_equation_from_camera() -> str:
    """Capture a photo and OCR it into a math expression. Returns LaTeX string."""
    raise FeatureNotAvailable(
        "Camera OCR requires a math-OCR backend (e.g. Mathpix API) and camera "
        "permission wiring via plyer.camera. Not wired up in this scaffold."
    )


def listen_for_expression() -> str:
    """Record voice input and transcribe it into an expression string."""
    raise FeatureNotAvailable(
        "Voice input requires a platform speech-recognition bridge "
        "(Android SpeechRecognizer / iOS Speech framework). Not wired up in this scaffold."
    )


def speak(text: str) -> None:
    """Read a result out loud."""
    raise FeatureNotAvailable(
        "Voice output requires plyer.tts or a platform TTS bridge. Not wired up in this scaffold."
    )


class CloudSyncBackend:
    """Interface a real cloud backend should implement to replace/extend HistoryStore."""

    def push(self, entries: list[dict]) -> None:
        raise FeatureNotAvailable("No cloud backend configured. See module docstring for setup options.")

    def pull(self) -> list[dict]:
        raise FeatureNotAvailable("No cloud backend configured. See module docstring for setup options.")
