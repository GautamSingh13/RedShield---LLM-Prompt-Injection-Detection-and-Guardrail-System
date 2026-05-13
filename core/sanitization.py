import re
from typing import Dict
from .detection import JAILBREAK_PATTERNS, normalize_text, is_malicious
import logging

logger = logging.getLogger(__name__)

def sanitize_prompt(text: str, aggressive: bool = False) -> Dict[str, any]:
    """Sanitize malicious content from prompts while preserving safe parts."""
    if not text or not isinstance(text, str):
        return {
            "sanitized_text": "",
            "was_modified": False,
            "removed_patterns": [],
            "removal_ratio": 1.0,
            "is_safe": False
        }
    
    original_text = text
    normalized_text = normalize_text(text)
    sanitized = normalized_text
    removed_patterns = []
    
    # Remove Base64 content first
    base64_pattern = re.compile(r"(?:[A-Za-z0-9+/]{4}){3,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?")
    base64_matches = base64_pattern.findall(sanitized)
    if base64_matches:
        sanitized = base64_pattern.sub("", sanitized)
        removed_patterns.append("base64_content")
        logger.info(f"Removed {len(base64_matches)} Base64 sequences")
    
    # Remove malicious patterns
    for pattern in JAILBREAK_PATTERNS:
        if pattern.search(sanitized):
            original_sanitized = sanitized
            sanitized = pattern.sub("", sanitized)
            if sanitized != original_sanitized:
                removed_patterns.append(f"pattern_{len(removed_patterns)}")
    
    # Clean up whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized)
    sanitized = re.sub(r'[.!?]+\s*$', '', sanitized)
    sanitized = re.sub(r'^\s*[.!?]+\s*', '', sanitized)
    sanitized = sanitized.strip()
    
    # Additional aggressive cleaning
    if aggressive:
        suspicious_words = ['ignore', 'bypass', 'override', 'jailbreak', 'unrestricted']
        for word in suspicious_words:
            sanitized = re.sub(r'\b' + re.escape(word) + r'\b', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    # Calculate metrics
    original_length = len(original_text)
    sanitized_length = len(sanitized)
    removal_ratio = (original_length - sanitized_length) / original_length if original_length > 0 else 0
    
    # Determine if result is safe
    is_safe = True
    if sanitized_length < 3:
        is_safe = False
    elif removal_ratio > 0.8:
        is_safe = False
    elif not sanitized.strip():
        is_safe = False
    
    result = {
        "sanitized_text": sanitized,
        "was_modified": sanitized != original_text,
        "removed_patterns": removed_patterns,
        "removal_ratio": removal_ratio,
        "is_safe": is_safe,
        "original_length": original_length,
        "sanitized_length": sanitized_length,
        "removed_count": len(removed_patterns)
    }
    
    if result["was_modified"]:
        logger.info(f"Sanitized prompt: {original_length} -> {sanitized_length} chars")
    
    return result

def analyze_prompt_safety(text: str) -> Dict[str, any]:
    """Comprehensive prompt safety analysis combining detection and sanitization."""
    if not text:
        return {
            "is_safe": False,
            "is_malicious": True,
            "sanitized_text": "",
            "security_status": "EMPTY_INPUT",
            "confidence": 1.0,
            "details": "Empty or invalid input",
            "was_modified": False
        }
    
    # Run detection
    detection_result = is_malicious(text)
    
    # Run sanitization
    if detection_result["is_malicious"]:
        sanitization_result = sanitize_prompt(text, aggressive=detection_result["confidence"] > 0.8)
    else:
        sanitization_result = {
            "sanitized_text": text,
            "was_modified": False,
            "is_safe": True,
            "original_length": len(text),
            "sanitized_length": len(text)
        }
    
    # Determine final status
    if detection_result["is_malicious"] and not sanitization_result["is_safe"]:
        status = "BLOCKED"
        is_safe = False
        final_text = ""
    elif detection_result["is_malicious"] and sanitization_result["is_safe"]:
        status = "SANITIZED"
        is_safe = True
        final_text = sanitization_result["sanitized_text"]
    else:
        status = "SAFE"
        is_safe = True
        final_text = text
    
    return {
        "is_safe": is_safe,
        "is_malicious": detection_result["is_malicious"],
        "sanitized_text": final_text,
        "security_status": status,
        "confidence": detection_result["confidence"],
        "was_modified": sanitization_result["was_modified"],
        "details": f"Confidence: {detection_result['confidence']:.2f}, "
                  f"Patterns: {len(detection_result.get('detected_patterns', []))}, "
                  f"Entropy: {detection_result.get('entropy', 0):.2f}"
    }