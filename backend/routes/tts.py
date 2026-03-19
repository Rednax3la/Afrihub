import os
import json
import hashlib
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from auth import get_current_user

router = APIRouter(prefix="/api/tts", tags=["tts"])

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads", "tts")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
R2_ENABLED = os.getenv("R2_ENABLED", "false").lower() == "true"


class TTSRequest(BaseModel):
    text: str
    language_code: str  # "yo" | "sw" | "zu" | "am"


def _cache_key(text: str, language_code: str) -> str:
    h = hashlib.md5(f"{language_code}:{text}".encode()).hexdigest()
    return f"{h}.mp3"


def _local_url(filename: str, request: Request) -> str:
    base = str(request.base_url).rstrip("/")
    return f"{base}/uploads/tts/{filename}"


async def _generate_elevenlabs(text: str, language_code: str, filepath: str) -> bool:
    if not ELEVENLABS_API_KEY:
        return False
    try:
        voice_ids_raw = os.getenv("ELEVENLABS_VOICE_IDS", "{}")
        voice_ids = json.loads(voice_ids_raw)
    except Exception:
        voice_ids = {}

    voice_id = voice_ids.get(language_code, "21m00Tcm4TlvDq8ikWAM")  # fallback: Rachel

    def _sync():
        import requests as http_req
        resp = http_req.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            json={
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
            },
            headers={"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": ELEVENLABS_API_KEY},
            timeout=30,
        )
        if resp.status_code == 200:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "wb") as f:
                f.write(resp.content)
            return True
        return False

    try:
        return await asyncio.to_thread(_sync)
    except Exception:
        return False


async def _generate_gtts(text: str, language_code: str, filepath: str) -> bool:
    # gTTS language code mapping
    lang_map = {"yo": "yo", "sw": "sw", "zu": "zu", "am": "am", "en": "en"}
    gtts_lang = lang_map.get(language_code, "en")

    def _sync():
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            tts.save(filepath)
            return True
        except Exception:
            return False

    try:
        return await asyncio.to_thread(_sync)
    except Exception:
        return False


async def _upload_cache_to_r2(filepath: str, filename: str) -> str:
    """If R2 is enabled, push the generated TTS file to R2."""
    public_url = os.getenv("R2_PUBLIC_URL", "").rstrip("/")
    key = f"tts/{filename}"

    def _sync():
        from routes.upload import _get_r2_client
        bucket = os.getenv("R2_BUCKET_NAME", "vernaculearn-media")
        with open(filepath, "rb") as f:
            _get_r2_client().put_object(Bucket=bucket, Key=key, Body=f.read(), ContentType="audio/mpeg")

    try:
        await asyncio.to_thread(_sync)
    except Exception:
        pass
    return f"{public_url}/{key}"


@router.post("/generate")
async def generate_tts(body: TTSRequest, request: Request, current_user=Depends(get_current_user)):
    if not body.text.strip():
        raise HTTPException(400, "Text cannot be empty")

    filename = _cache_key(body.text, body.language_code)
    cache_path = os.path.join(CACHE_DIR, filename)

    # Return cached file if it exists
    if os.path.exists(cache_path):
        if R2_ENABLED:
            url = f"{os.getenv('R2_PUBLIC_URL', '').rstrip('/')}/tts/{filename}"
        else:
            url = _local_url(f"tts/{filename}", request)
        return {"audio_url": url}

    # Generate — ElevenLabs first, gTTS fallback
    os.makedirs(CACHE_DIR, exist_ok=True)
    success = await _generate_elevenlabs(body.text, body.language_code, cache_path)
    if not success:
        success = await _generate_gtts(body.text, body.language_code, cache_path)

    if not success:
        raise HTTPException(503, "TTS generation failed. Please try again later.")

    if R2_ENABLED:
        url = await _upload_cache_to_r2(cache_path, filename)
    else:
        url = _local_url(f"tts/{filename}", request)

    return {"audio_url": url}
