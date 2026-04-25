import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import List, Optional


async def _resolve_url(url: str, audio_only: bool = False) -> str:
    """
    Use yt-dlp to get a direct stream URL if the source is a web URL.

    audio_only=False (default): requests the best video stream.
      yt-dlp -g with a combined format (bestvideo+bestaudio) outputs TWO lines:
        line[0] = video-only stream URL
        line[1] = audio-only stream URL   ← we take line[0] for video
    audio_only=True: requests the best audio-only stream.
      This is required for platforms like Reddit that use CMAF/DASH where
      video and audio are served as completely separate streams. Passing the
      video URL to FFmpeg's -vn flag yields "no audio stream" because there
      literally isn't one in that file.
    """
    if not url.startswith(("http://", "https://")):
        return url

    if audio_only:
        # Prefer m4a (AAC) then webm/opus then anything — stay away from video formats
        fmt = "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio"
        stream_label = "audio"
    else:
        # Combined selector: yt-dlp prints video URL on line 0, audio URL on line 1
        fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        stream_label = "video"

    print(f"[PREPROCESS] Resolving {stream_label} URL with yt-dlp: {url}")
    try:
        cmd = [
            "yt-dlp",
            "-g",  # Print direct URL(s) only
            "-f",
            fmt,
            "--user-agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "--no-check-certificates",
            url,
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            lines = [l for l in stdout.decode().strip().split("\n") if l.strip()]
            # For audio_only format there is only one line; for combined format
            # line[0]=video, line[-1]=audio — so we always want line[0] for video
            # and line[-1] for audio (works correctly whether 1 or 2 lines).
            resolved = lines[-1] if audio_only else lines[0]
            print(
                f"[PREPROCESS] [SUCCESS] {stream_label} URL resolved to stream: {resolved[:60]}..."
            )
            return resolved
        else:
            err_msg = stderr.decode().strip()
            print(f"[PREPROCESS] [FAILURE] yt-dlp could not resolve {stream_label} URL.")
            print(f"[PREPROCESS] [REASON] {err_msg if err_msg else 'Empty stderr/Process crashed'}")
            return url  # Fallback to original
    except Exception as e:
        print(f"[PREPROCESS] [FAILURE] Exception during resolution: {str(e)}")
        return url


async def extract_keyframes(
    source: str, interval_seconds: int = 2, max_frames: int = 10
) -> List[str]:
    """
    Extract keyframes from a video file or URL.
    """
    if not source:
        return []

    resolved_source = await _resolve_url(source)
    output_dir = tempfile.mkdtemp(prefix="vigilens_frames_")
    output_pattern = os.path.join(output_dir, "frame_%04d.jpg")

    print(f"[PREPROCESS] Extracting keyframes from: {source[:50]}...")

    # Check if ffmpeg exists in PATH
    import shutil

    if not shutil.which("ffmpeg"):
        print("\n" + "!" * 50, flush=True)
        print("[CRITICAL ERROR] FFmpeg NOT FOUND ON WINDOWS!", flush=True)
        print("[ACTION REQUIRED] Install FFmpeg locally on Windows.", flush=True)
        print("[ACTION REQUIRED] Visit: https://www.gyan.dev/ffmpeg/builds/", flush=True)
        print("!" * 50 + "\n", flush=True)
        return []

    cmd = [
        "ffmpeg",
        "-i",
        resolved_source,
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
        print(f"[DEBUG] FFmpeg Command: {' '.join(cmd)}", flush=True)
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=45)

        if proc.returncode != 0:
            err_msg = stderr.decode()
            print(f"[ERROR] FFmpeg failed (Code {proc.returncode})", flush=True)
            print(f"[ERROR] FFmpeg Stderr: {err_msg}", flush=True)
            return []

    except Exception as e:
        print(f"[ERROR] FFmpeg system exception: {str(e)}", flush=True)
        import traceback

        traceback.print_exc()
        return []

    frames = sorted(Path(output_dir).glob("frame_*.jpg"))
    print(f"[PREPROCESS] [SUCCESS] Extracted {len(frames)} keyframes.", flush=True)
    return [str(f) for f in frames]


async def extract_audio(source: str) -> Optional[str]:
    """
    Extract audio track from a video file or URL.
    """
    if not source:
        return None

    # Request the audio-only stream URL — on platforms like Reddit that use
    # CMAF/DASH, the video and audio are separate streams. Resolving with the
    # default video format gives a video-only URL that contains no audio track,
    # causing FFmpeg to error with "Output file does not contain any stream".
    resolved_source = await _resolve_url(source, audio_only=True)
    output_file = os.path.join(tempfile.mkdtemp(prefix="vigilens_audio_"), "audio.wav")

    print(f"[PREPROCESS] Extracting audio from resolved stream...")
    cmd = [
        "ffmpeg",
        "-i",
        resolved_source,
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
        _, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)

        if proc.returncode != 0:
            stderr_text = stderr.decode()
            if "does not contain any stream" in stderr_text or "Invalid argument" in stderr_text:
                print(
                    f"[PREPROCESS] [INFO] No audio stream found in this video — audio analysis will be skipped."
                )
            else:
                print(f"[ERROR] FFmpeg audio extraction failed.")
                print(f"[ERROR] Stderr: {stderr_text}")
            return None

        return output_file if Path(output_file).exists() else None
    except Exception as e:
        # Don't log full traceback for missing audio, it's common
        if "Output file does not contain any stream" in str(e):
            print(
                f"[PREPROCESS] [INFO] No audio stream found in video. Skipping audio analysis.",
                flush=True,
            )
        else:
            print(f"[PREPROCESS] [WARNING] Audio extraction skipped: {e}", flush=True)
        return None
