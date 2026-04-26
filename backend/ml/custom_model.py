"""Custom trained deepfake detection model integration."""

import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

# Path to your friend's model — set via env or place in backend/ml/weights/
MODEL_PATH = Path(__file__).parent / "weights" / "custom_deepfake_detector"


def load_model():
    """
    Auto-detect model format and load. Supports:
    - PyTorch checkpoint (.pt / .pth)
    - scikit-learn pickle (.pkl / .joblib)
    - ONNX (.onnx) — recommended for cross-platform use
    - HuggingFace local directory
    """
    if not MODEL_PATH.exists():
        logger.warning(f"[CUSTOM_MODEL] No model found at {MODEL_PATH} — will skip custom scoring")
        return None, None

    # Check for ONNX (fastest, no framework dependency)
    onnx_path = list(MODEL_PATH.glob("*.onnx"))
    if onnx_path:
        try:
            import onnxruntime as ort

            session = ort.InferenceSession(str(onnx_path[0]))
            logger.info(f"[CUSTOM_MODEL] Loaded ONNX model: {onnx_path[0].name}")
            return session, "onnx"
        except ImportError:
            logger.warning("[CUSTOM_MODEL] onnxruntime not installed — falling back")

    # Check for PyTorch checkpoint
    pt_paths = list(MODEL_PATH.glob("*.pt")) + list(MODEL_PATH.glob("*.pth"))
    if pt_paths:
        try:
            import torch

            model = torch.load(pt_paths[0], map_location="cpu")
            model.eval()
            logger.info(f"[CUSTOM_MODEL] Loaded PyTorch model: {pt_paths[0].name}")
            return model, "pytorch"
        except Exception as e:
            logger.error(f"[CUSTOM_MODEL] PyTorch load failed: {e}")

    # Check for sklearn pickle
    pkl_paths = list(MODEL_PATH.glob("*.pkl")) + list(MODEL_PATH.glob("*.joblib"))
    if pkl_paths:
        try:
            import joblib

            model = joblib.load(pkl_paths[0])
            logger.info(f"[CUSTOM_MODEL] Loaded sklearn model: {pkl_paths[0].name}")
            return model, "sklearn"
        except Exception as e:
            logger.error(f"[CUSTOM_MODEL] sklearn load failed: {e}")

    logger.warning("[CUSTOM_MODEL] No loadable model found in weights directory")
    return None, None


def score_frames_with_custom_model(
    frame_paths: list,
    model,
    model_type: str,
) -> float | None:
    """
    Run inference on keyframes and return a single deepfake probability (0.0-1.0).
    Returns None if model unavailable or inference fails.
    0.0 = definitely real, 1.0 = definitely AI-generated.
    """
    if model is None or not frame_paths:
        return None

    try:
        import torchvision.transforms as T
        from PIL import Image

        transform = T.Compose(
            [
                T.Resize((224, 224)),
                T.ToTensor(),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )

        scores = []
        for fp in frame_paths[:5]:
            if not Path(fp).exists():
                continue
            img = Image.open(fp).convert("RGB")
            tensor = transform(img).unsqueeze(0)

            if model_type == "pytorch":
                import torch

                with torch.no_grad():
                    output = model(tensor)
                    if output.shape[-1] == 1:
                        prob = torch.sigmoid(output).item()
                    else:
                        prob = torch.softmax(output, dim=-1)[0][1].item()
                scores.append(prob)

            elif model_type == "onnx":
                input_name = model.get_inputs()[0].name
                output = model.run(None, {input_name: tensor.numpy()})
                # Assume output[0] is logit or probability
                raw = float(output[0].flatten()[0])
                prob = 1 / (1 + np.exp(-raw)) if raw > 1 else raw
                scores.append(prob)

        if not scores:
            return None

        avg_score = sum(scores) / len(scores)
        logger.info(
            f"[CUSTOM_MODEL] Inference on {len(scores)} frames: avg_fake_prob={avg_score:.3f}"
        )
        return avg_score

    except Exception as e:
        logger.error(f"[CUSTOM_MODEL] Inference failed: {e}")
        return None


# Load model at module import time (cached for lifetime of process)
_model, _model_type = load_model()


def get_custom_deepfake_score(frame_paths: list) -> float | None:
    """Public interface — call this from scoring engine."""
    return score_frames_with_custom_model(frame_paths, _model, _model_type)
