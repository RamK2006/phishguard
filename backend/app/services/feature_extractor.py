"""PhishGuard — 47-Feature URL Feature Extractor.

Extracts lexical, domain, entropy, homograph, and structural features
from URLs for ML inference.
"""

import re
import math
import hashlib
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Optional
import structlog

logger = structlog.get_logger()

# ─── TLD Risk Scores (pre-built lookup) ───
TLD_RISK_SCORES = {
    ".com": 0.1, ".org": 0.15, ".net": 0.15, ".edu": 0.05, ".gov": 0.02,
    ".tk": 0.9, ".ml": 0.85, ".ga": 0.85, ".cf": 0.85, ".gq": 0.85,
    ".xyz": 0.7, ".top": 0.75, ".buzz": 0.8, ".club": 0.6, ".online": 0.65,
    ".site": 0.7, ".info": 0.5, ".biz": 0.55, ".work": 0.6, ".click": 0.8,
    ".link": 0.65, ".win": 0.8, ".review": 0.75, ".stream": 0.7, ".racing": 0.75,
    ".loan": 0.8, ".download": 0.75, ".date": 0.7, ".faith": 0.7, ".party": 0.7,
    ".science": 0.65, ".cricket": 0.7, ".bid": 0.7, ".trade": 0.65, ".webcam": 0.75,
    ".accountant": 0.7, ".co": 0.3, ".io": 0.2, ".dev": 0.15, ".app": 0.15,
    ".me": 0.35, ".us": 0.3, ".uk": 0.15, ".de": 0.15, ".fr": 0.15,
}

# ─── Top 200 Brand Domains for Homograph Detection ───
TOP_BRANDS = [
    "google.com", "facebook.com", "apple.com", "amazon.com", "microsoft.com",
    "netflix.com", "paypal.com", "instagram.com", "twitter.com", "linkedin.com",
    "dropbox.com", "chase.com", "wellsfargo.com", "bankofamerica.com", "citibank.com",
    "outlook.com", "yahoo.com", "gmail.com", "icloud.com", "office.com",
    "adobe.com", "spotify.com", "github.com", "stackoverflow.com", "reddit.com",
    "twitch.tv", "discord.com", "zoom.us", "slack.com", "salesforce.com",
    "shopify.com", "ebay.com", "walmart.com", "target.com", "bestbuy.com",
    "ups.com", "fedex.com", "usps.com", "dhl.com", "americanexpress.com",
    "visa.com", "mastercard.com", "coinbase.com", "binance.com", "robinhood.com",
    "steam.com", "epicgames.com", "playstation.com", "xbox.com", "nintendo.com",
]

# ─── Homoglyph mapping (Cyrillic/Greek → Latin) ───
HOMOGLYPHS = {
    "\u0430": "a", "\u0435": "e", "\u043e": "o", "\u0440": "p", "\u0441": "c",
    "\u0443": "y", "\u0445": "x", "\u0456": "i", "\u043a": "k", "\u043c": "m",
    "\u043d": "n", "\u0442": "t", "\u03b1": "a", "\u03bf": "o", "\u03c1": "p",
    "\u03c4": "t", "\u03b5": "e", "\u0405": "s", "\u0392": "b", "\u0397": "h",
}


def _shannon_entropy(text: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not text:
        return 0.0
    freq = {}
    for char in text:
        freq[char] = freq.get(char, 0) + 1
    length = len(text)
    entropy = -sum(
        (count / length) * math.log2(count / length)
        for count in freq.values()
    )
    return round(entropy, 4)


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Compute Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row
    return prev_row[-1]


def _detect_homoglyphs(domain: str) -> int:
    """Count homoglyph characters in a domain."""
    count = 0
    for char in domain:
        if char in HOMOGLYPHS:
            count += 1
    return count


def _keyboard_proximity_score(domain: str, brand: str) -> float:
    """Score based on keyboard-proximity typosquatting detection."""
    KEYBOARD_NEIGHBORS = {
        'q': 'wa', 'w': 'qeas', 'e': 'wrds', 'r': 'etdf', 't': 'ryfg',
        'y': 'tugh', 'u': 'yijh', 'i': 'uokj', 'o': 'iplk', 'p': 'ol',
        'a': 'qwsz', 's': 'awedxz', 'd': 'serfcx', 'f': 'drtgvc',
        'g': 'ftyhbv', 'h': 'gyujnb', 'j': 'huikmn', 'k': 'jiolm',
        'l': 'kop', 'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb',
        'b': 'vghn', 'n': 'bhjm', 'm': 'njk',
    }
    if len(domain) != len(brand):
        return 0.0
    proximity_matches = 0
    differences = 0
    for d_char, b_char in zip(domain.lower(), brand.lower()):
        if d_char != b_char:
            differences += 1
            if d_char in KEYBOARD_NEIGHBORS.get(b_char, ''):
                proximity_matches += 1
    if differences == 0:
        return 0.0
    return proximity_matches / max(differences, 1)


def extract_features(url: str) -> Dict[str, float]:
    """Extract all 47 features from a URL.

    Returns a dictionary with feature names as keys and float values.
    """
    features = {}

    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        path = parsed.path or ""
        query = parsed.query or ""
        fragment = parsed.fragment or ""

        # ─── URL Lexical Features (18) ───
        features["url_length"] = float(len(url))
        features["digit_count"] = float(sum(c.isdigit() for c in url))
        features["digit_ratio"] = features["digit_count"] / max(len(url), 1)
        features["letter_count"] = float(sum(c.isalpha() for c in url))
        features["special_char_count"] = float(
            sum(c in "-_@?=&!#$%^*()+" for c in url)
        )
        features["dot_count"] = float(url.count("."))
        features["hyphen_count"] = float(url.count("-"))
        features["at_sign_present"] = float("@" in url)
        features["double_slash_count"] = float(url.count("//"))
        features["slash_count"] = float(url.count("/"))
        features["path_depth"] = float(len([p for p in path.split("/") if p]))
        features["query_param_count"] = float(len(parse_qs(query)))
        features["fragment_present"] = float(bool(fragment))
        features["has_port"] = float(bool(parsed.port))
        features["has_encoded_chars"] = float(bool(re.search(r"%[0-9a-fA-F]{2}", url)))
        features["url_has_ip"] = float(bool(re.match(r"\d+\.\d+\.\d+\.\d+", hostname)))
        features["starts_with_https"] = float(parsed.scheme == "https")
        features["suspicious_words"] = float(
            sum(
                word in url.lower()
                for word in [
                    "login", "signin", "verify", "secure", "account", "update",
                    "confirm", "banking", "suspend", "password", "credential",
                ]
            )
        )

        # ─── Domain Features (12) ───
        features["domain_length"] = float(len(hostname))
        subdomains = hostname.split(".")
        features["subdomain_count"] = float(max(len(subdomains) - 2, 0))
        features["is_ip_address"] = float(
            bool(re.match(r"^\d+\.\d+\.\d+\.\d+$", hostname))
        )

        # TLD risk score
        tld = "." + subdomains[-1] if subdomains else ""
        features["tld_risk_score"] = TLD_RISK_SCORES.get(tld, 0.4)

        # Domain age placeholders (require async WHOIS — computed separately)
        features["domain_age_days"] = -1.0  # -1 means not computed
        features["is_new_domain"] = 0.0
        features["registrar_reputation"] = 0.5  # neutral default

        # Security headers placeholders
        features["has_spf"] = 0.0
        features["has_dmarc"] = 0.0
        features["has_dkim"] = 0.0
        features["domain_has_mx"] = 0.0
        features["domain_registration_length"] = -1.0

        # ─── Entropy Features (4) ───
        features["url_entropy"] = _shannon_entropy(url)
        features["hostname_entropy"] = _shannon_entropy(hostname)
        features["path_entropy"] = _shannon_entropy(path)
        features["query_entropy"] = _shannon_entropy(query)

        # ─── Homograph / Typosquat Features (8) ───
        min_levenshtein = float("inf")
        best_brand_match = ""
        max_keyboard_prox = 0.0
        domain_base = ".".join(subdomains[:-1]) if len(subdomains) > 1 else hostname

        for brand in TOP_BRANDS:
            brand_base = brand.split(".")[0]
            dist = _levenshtein_distance(domain_base, brand_base)
            if dist < min_levenshtein:
                min_levenshtein = dist
                best_brand_match = brand_base
            prox = _keyboard_proximity_score(domain_base, brand_base)
            if prox > max_keyboard_prox:
                max_keyboard_prox = prox

        features["min_brand_levenshtein"] = float(
            min_levenshtein if min_levenshtein != float("inf") else 100
        )
        features["keyboard_proximity_score"] = max_keyboard_prox
        features["homoglyph_count"] = float(_detect_homoglyphs(hostname))
        features["has_homoglyphs"] = float(features["homoglyph_count"] > 0)
        features["lookalike_tld"] = float(
            tld in [".co", ".cm", ".om", ".ne", ".corn"]
        )
        features["brand_in_subdomain"] = float(
            any(brand.split(".")[0] in hostname for brand in TOP_BRANDS[:20])
            and not any(hostname.endswith(brand) for brand in TOP_BRANDS[:20])
        )
        features["punycode_present"] = float("xn--" in hostname)
        features["suspicious_brand_distance"] = float(
            1.0 if 1 <= min_levenshtein <= 3 else 0.0
        )

        # ─── Structural Features (5) ───
        features["has_redirect_chain"] = 0.0  # Computed at scan time
        features["https_present"] = float(parsed.scheme == "https")
        features["cert_age_days"] = -1.0  # Computed at scan time
        features["cert_issuer_trust"] = 0.5  # Default neutral
        features["http_response_code"] = 200.0  # Default, updated at scan time

    except Exception as e:
        logger.error("feature_extraction_failed", url=url, error=str(e))
        # Return minimal features on error
        features = {f"feature_{i}": 0.0 for i in range(47)}

    return features


def features_to_vector(features: Dict[str, float]) -> List[float]:
    """Convert feature dict to ordered vector for ML model input."""
    feature_order = [
        "url_length", "digit_count", "digit_ratio", "letter_count",
        "special_char_count", "dot_count", "hyphen_count", "at_sign_present",
        "double_slash_count", "slash_count", "path_depth", "query_param_count",
        "fragment_present", "has_port", "has_encoded_chars", "url_has_ip",
        "starts_with_https", "suspicious_words",
        "domain_length", "subdomain_count", "is_ip_address", "tld_risk_score",
        "domain_age_days", "is_new_domain", "registrar_reputation",
        "has_spf", "has_dmarc", "has_dkim", "domain_has_mx",
        "domain_registration_length",
        "url_entropy", "hostname_entropy", "path_entropy", "query_entropy",
        "min_brand_levenshtein", "keyboard_proximity_score", "homoglyph_count",
        "has_homoglyphs", "lookalike_tld", "brand_in_subdomain",
        "punycode_present", "suspicious_brand_distance",
        "has_redirect_chain", "https_present", "cert_age_days",
        "cert_issuer_trust", "http_response_code",
    ]
    return [features.get(name, 0.0) for name in feature_order]
