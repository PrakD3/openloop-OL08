"""OCR tools using EasyOCR."""

from typing import List, Optional


async def extract_text_from_frames(
    frame_paths: List[str], languages: Optional[List[str]] = None
) -> str:
    """
    Extract text from video frames using EasyOCR.

    Args:
        frame_paths: List of paths to frame images
        languages: List of language codes (default: ['en', 'hi', 'ta', 'ar'])

    Returns:
        Concatenated text from all frames
    """
    if not frame_paths:
        return ""

    langs = languages or ["en", "hi", "ta", "ar"]

    try:
        import easyocr  # type: ignore[import]

        reader = easyocr.Reader(langs, gpu=False, verbose=False)
        all_text: List[str] = []

        for frame_path in frame_paths[:5]:
            results = reader.readtext(frame_path, detail=0)
            all_text.extend(results)

        return " ".join(all_text)
    except Exception as exc:
        return f"OCR error: {exc}"
