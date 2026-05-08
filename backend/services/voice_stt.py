"""Транскрипция голоса через OpenAI Whisper (синхронный SDK в thread pool)."""

from __future__ import annotations

import asyncio
import io
import logging

from openai import OpenAI

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "whisper-1"


async def transcribe_audio(
    *,
    api_key: str,
    audio_bytes: bytes,
    filename: str,
    model: str = _DEFAULT_MODEL,
) -> str:
    if not api_key:
        msg = "OPENAI_API_KEY is not configured"
        raise RuntimeError(msg)

    def _run() -> str:
        bio = io.BytesIO(audio_bytes)
        bio.name = filename or "audio.webm"
        client = OpenAI(api_key=api_key)
        result = client.audio.transcriptions.create(
            model=model,
            file=bio,
        )
        text = getattr(result, "text", None) or ""
        return text.strip()

    try:
        return await asyncio.to_thread(_run)
    except Exception:
        logger.exception("voice_stt_failed filename=%s bytes=%s", filename, len(audio_bytes))
        raise
