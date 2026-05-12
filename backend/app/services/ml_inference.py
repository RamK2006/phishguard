"""PhishGuard — ML Inference Service.

Heuristic-based URL risk scoring for serverless deployment.
LightGBM model loaded if available, otherwise pure heuristic.
"""

import os
import numpy as np
from typing import Dict, Optional, Tuple
import structlog

from app.services.feature_extractor import extract_features, features_to_vector

logger = structlog.get_logger()

_lgbm_model = None
_model_loaded = False

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "ml", "models", "lgbm_v1.pkl"
)


def load_model():
    """Load LightGBM model from disk at startup (optional)."""
    global _lgbm_model, _model_loaded
    if os.path.exists(MODEL_PATH):
        try:
            import joblib
            _lgbm_model = joblib.load(MODEL_PATH)
            _model_loaded = True
            logger.info("ml_model_loaded", model_path=MODEL_PATH)
        except Exception as e:
            logger.warning("ml_model_load_skipped", error=str(e))
    else:
        logger.info("ml_model_not_found_using_heuristics", model_path=MODEL_PATH)


def is_model_loaded() -> bool:
    return _model_loaded


def predict_url_risk(url: str) -> Tuple[float, Dict[str, float], str]:
    """Run ML inference. Returns (score, features, tier_used)."""
    features = extract_features(url)
    feature_vector = features_to_vector(features)

    if not _model_loaded or _lgbm_model is None:
        return _heuristic_score(features), features, "heuristic"

    try:
        X = np.array([feature_vector])
        proba = _lgbm_model.predict_proba(X)[0]
        ml_score = float(proba[1]) if len(proba) > 1 else float(proba[0])
        return ml_score, features, "lightgbm"
    except Exception as e:
        logger.error("ml_inference_failed", error=str(e))
        return _heuristic_score(features), features, "heuristic"


def _heuristic_score(features: Dict[str, float]) -> float:
    """Fallback heuristic scoring when model unavailable."""
    score = 0.0
    weights = {
        "is_ip_address": 0.15, "has_homoglyphs": 0.12,
        "suspicious_words": 0.08, "tld_risk_score": 0.10,
        "at_sign_present": 0.10, "suspicious_brand_distance": 0.12,
        "punycode_present": 0.08, "brand_in_subdomain": 0.10,
    }
    for feat, w in weights.items():
        val = features.get(feat, 0.0)
        score += w * min(val if feat != "tld_risk_score" else val, 1.0)
    if features.get("starts_with_https", 1.0) == 0.0:
        score += 0.05
    if features.get("url_length", 0.0) > 100:
        score += 0.05
    return min(max(score, 0.0), 1.0)


def get_risk_level(score: float) -> str:
    if score < 0.3:
        return "safe"
    elif score < 0.75:
        return "suspicious"
    return "malicious"
