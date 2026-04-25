"""EXIF and metadata extraction tools."""

import json
import subprocess
from typing import Dict, Optional


def extract_video_metadata(video_path: str) -> Dict:
    """
    Extract metadata from a video file using exiftool.

    Args:
        video_path: Path to video file

    Returns:
        Dict of metadata fields
    """
    try:
        result = subprocess.run(
            ["exiftool", "-json", video_path],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data[0] if data else {}
    except Exception:
        pass
    return {}


def extract_gps(metadata: Dict) -> Optional[Dict]:
    """Extract GPS coordinates from metadata dict."""
    lat = metadata.get("GPSLatitude")
    lon = metadata.get("GPSLongitude")
    if lat and lon:
        return {"lat": lat, "lon": lon}
    return None
