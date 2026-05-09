"""PhishGuard — LLM Explainer Service.

Groq API (Llama 3.1 70B) for human-readable risk explanations.
Returns structured JSON with risk_factors, recommended_action, confidence.
"""

from typing import Dict, Any, Optional
import json
import structlog

from app.core.config import settings

logger = structlog.get_logger()


async def generate_explanation(
    url: str,
    risk_score: float,
    features: Dict[str, float],
    cti_results: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Generate LLM-powered risk explanation using Groq."""
    if risk_score < 0.4:
        return _safe_explanation(url, risk_score)

    try:
        from groq import AsyncGroq

        client = AsyncGroq(api_key=settings.groq_api_key)

        # Build context for the prompt
        suspicious_features = {
            k: v for k, v in features.items()
            if v > 0.5 and k in [
                "is_ip_address", "has_homoglyphs", "suspicious_words",
                "tld_risk_score", "at_sign_present", "suspicious_brand_distance",
                "punycode_present", "brand_in_subdomain", "url_entropy",
            ]
        }

        cti_summary = "No CTI data available."
        if cti_results:
            sources = cti_results.get("sources", [])
            cti_parts = []
            for s in sources:
                if s.get("available"):
                    cti_parts.append(f"{s['source']}: score={s.get('score', 0):.2f}")
            if cti_parts:
                cti_summary = ", ".join(cti_parts)

        prompt = f"""Analyze this URL for phishing risk and provide a structured explanation.

URL: {url}
ML Risk Score: {risk_score:.3f}
Suspicious Features: {json.dumps(suspicious_features)}
Threat Intelligence: {cti_summary}

Respond in JSON format with exactly these fields:
{{
  "risk_factors": ["list of 3-5 specific risk factors found"],
  "recommended_action": "clear action recommendation for the user",
  "confidence": 0.0-1.0,
  "summary": "2-3 sentence summary of the threat assessment"
}}"""

        response = await client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a cybersecurity analyst. Analyze URLs for phishing risk. Always respond with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=500,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        explanation = json.loads(content)

        return {
            "risk_factors": explanation.get("risk_factors", []),
            "recommended_action": explanation.get("recommended_action", "Exercise caution"),
            "confidence": explanation.get("confidence", risk_score),
            "summary": explanation.get("summary", ""),
            "llm_generated": True,
        }

    except Exception as e:
        logger.warning("llm_explanation_failed", error=str(e))
        return _fallback_explanation(url, risk_score, features)


def _safe_explanation(url: str, score: float) -> Dict[str, Any]:
    """Generate explanation for safe URLs without LLM call."""
    return {
        "risk_factors": [],
        "recommended_action": "This URL appears safe to visit.",
        "confidence": 1.0 - score,
        "summary": f"The URL has a low risk score of {score:.2f}. No significant threats detected.",
        "llm_generated": False,
    }


def _fallback_explanation(
    url: str, score: float, features: Dict[str, float]
) -> Dict[str, Any]:
    """Generate rule-based explanation when LLM is unavailable."""
    risk_factors = []

    if features.get("is_ip_address", 0) > 0:
        risk_factors.append("URL uses IP address instead of domain name")
    if features.get("has_homoglyphs", 0) > 0:
        risk_factors.append("Domain contains homoglyph characters (lookalike letters)")
    if features.get("suspicious_words", 0) > 0:
        risk_factors.append("URL contains suspicious keywords (login, verify, secure)")
    if features.get("tld_risk_score", 0) > 0.6:
        risk_factors.append("High-risk top-level domain")
    if features.get("brand_in_subdomain", 0) > 0:
        risk_factors.append("Known brand name used in subdomain (potential impersonation)")
    if features.get("url_entropy", 0) > 4.0:
        risk_factors.append("High URL entropy suggesting randomized/obfuscated path")
    if features.get("suspicious_brand_distance", 0) > 0:
        risk_factors.append("Domain is suspiciously similar to a known brand")

    if not risk_factors:
        risk_factors.append("Multiple heuristic signals indicate elevated risk")

    action = "Block this URL" if score > 0.75 else "Proceed with caution"

    return {
        "risk_factors": risk_factors[:5],
        "recommended_action": action,
        "confidence": score,
        "summary": f"Risk score: {score:.2f}. {len(risk_factors)} risk factor(s) identified.",
        "llm_generated": False,
    }
