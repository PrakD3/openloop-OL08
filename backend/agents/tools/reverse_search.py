"""Reverse image search tools."""

import base64
from pathlib import Path
from typing import Dict, List, Optional

import httpx

from ...config.settings import settings


async def phash_keyframes(frame_paths: List[str]) -> List[str]:
    """
    Compute perceptual hashes for keyframes.

    Args:
        frame_paths: List of paths to frame images

    Returns:
        List of pHash strings
    """
    hashes: List[str] = []
    try:
        import imagehash  # type: ignore[import]
        from PIL import Image

        for path in frame_paths:
            img = Image.open(path)
            phash = imagehash.phash(img)
            hashes.append(str(phash))
    except Exception:
        pass
    return hashes


async def google_vision_reverse_search(frame_path: str) -> Dict:
    """
    Perform reverse image search via Google Vision API.

    Returns:
        Dict with web entities and matching pages
    """
    if not settings.google_vision_api_key:
        return {"error": "Google Vision API key not configured"}

    try:
        with open(frame_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"https://vision.googleapis.com/v1/images:annotate?key={settings.google_vision_api_key}",
                json={
                    "requests": [
                        {
                            "image": {"content": img_b64},
                            "features": [{"type": "WEB_DETECTION"}],
                        }
                    ]
                },
            )
            if response.status_code == 200:
                return response.json().get("responses", [{}])[0].get("webDetection", {})
    except Exception as exc:
        return {"error": str(exc)}

    return {}
