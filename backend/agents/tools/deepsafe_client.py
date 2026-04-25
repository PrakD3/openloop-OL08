"""Local DeepSafe Docker API client."""

import base64
from typing import Dict, Optional

import httpx

from ...config.settings import settings


async def detect_deepfake(frame_path: str, model: str = "CrossEfficientViT") -> Dict:
    """
    Send a frame to local DeepSafe Docker API for deepfake detection.

    Args:
        frame_path: Path to frame image
        model: DeepSafe model to use

    Returns:
        Dict with is_fake, confidence, model_used
    """
    try:
        with open(frame_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.deepsafe_url}/api/detect",
                json={"image_base64": img_b64, "model": model},
            )
            if response.status_code == 200:
                return response.json()
    except Exception as exc:
        return {"error": str(exc), "is_fake": False, "confidence": 0.0}

    return {"is_fake": False, "confidence": 0.0, "model_used": model}


async def health_check() -> bool:
    """Check if DeepSafe API is available."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.deepsafe_url}/health")
            return response.status_code == 200
    except Exception:
        return False
