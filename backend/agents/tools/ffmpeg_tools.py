"""FFmpeg tools for keyframe extraction and audio extraction."""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import List, Optional


async def extract_keyframes(
    source: str, interval_seconds: int = 2, max_frames: int = 10
) -> List[str]:
    """
    Extract keyframes from a video file or URL.

    Args:
        source: Local file path or URL
        interval_seconds: Extract one frame every N seconds
        max_frames: Maximum number of frames to extract

    Returns:
        List of paths to extracted frame images
    """
    if not source:
        return []

    output_dir = tempfile.mkdtemp(prefix="vigilens_frames_")
    output_pattern = os.path.join(output_dir, "frame_%04d.jpg")

    cmd = [
        "ffmpeg",
        "-i",
        source,
        "-vf",
        f"fps=1/{interval_seconds}",
        "-frames:v",
        str(max_frames),
        "-q:v",
        "2",
        output_pattern,
        "-y",
        "-loglevel",
        "error",
    ]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await asyncio.wait_for(proc.communicate(), timeout=60)
    except Exception:
        return []

    frames = sorted(Path(output_dir).glob("frame_*.jpg"))
    return [str(f) for f in frames]


async def extract_audio(source: str) -> Optional[str]:
    """
    Extract audio track from a video file or URL.

    Args:
        source: Local file path or URL

    Returns:
        Path to extracted WAV file, or None
    """
    if not source:
        return None

    output_file = os.path.join(tempfile.mkdtemp(prefix="vigilens_audio_"), "audio.wav")

    cmd = [
        "ffmpeg",
        "-i",
        source,
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        output_file,
        "-y",
        "-loglevel",
        "error",
    ]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await asyncio.wait_for(proc.communicate(), timeout=60)
        return output_file if Path(output_file).exists() else None
    except Exception:
        return None
