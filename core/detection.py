import re
import unicodedata
import base64
import math
from typing import List, Dict, Tuple
from collections import Counter
import logging

logger = logging.getLogger(__name__)

# Comprehensive jailbreak patterns
JAILBREAK_PATTERNS = [
    # Direct instruction bypass
    re.compile(r"(ignore|disregard|disobey|bypass|evade|override)\s+(all\s+)?(previous\s+)?(instructions?|directives?|rules?)", re.IGNORECASE),
    re.compile(r"(forget|discard|remove|delete)\s+(everything|all)\s+(before|above|prior)", re.IGNORECASE),
    
    # Role-playing attacks
    re.compile(r"(act\s+as|pretend\s+to\s+be|become|roleplay\s+as)\s+(an?\s+)?(evil|malicious|unrestricted|jailbroken)", re.IGNORECASE),
    re.compile(r"(you('?re|\s+are)\s+now\s+(a\s+)?DAN|do\s+anything\s+now)", re.IGNORECASE),
    
    # Safety bypass attempts
    re.compile(r"(bypass|evade|disable|ignore|remove|turn\s+off)\s+.*(safety|security|filter|restriction|limitation)", re.IGNORECASE),
    re.compile(r"(disable|turn\s+off|deactivate)\s+.*(protection|safeguard|check)", re.IGNORECASE),
    
    # Mode switching
    re.compile(r"(developer\s+mode|debug\s+mode|admin\s+mode|god\s+mode|unrestricted\s+mode)", re.IGNORECASE),
    re.compile(r"(jailbreak|jailbroken|unrestricted|unfiltered)\s+(mode|AI|assistant)", re.IGNORECASE),
    
    # Command execution
    re.compile(r"(execute|run|perform|carry\s+out)\s+.*(command|script|code|instruction)", re.IGNORECASE),
    re.compile(r"(access|retrieve|fetch|get)\s+.*(system|admin|root|file|database|credentials)", re.IGNORECASE),
    
    # Data exfiltration
    re.compile(r"(send|transfer|exfiltrate|leak|reveal)\s+.*(data|information|credentials|password|secret)", re.IGNORECASE),
    
    # Policy violations
    re.compile(r"(ignore|bypass|violate)\s+.*(content\s+)?(policy|policies|guideline|terms)", re.IGNORECASE),
    
    # Prompt injection markers
    re.compile(r"system\s*:\s*", re.IGNORECASE),
    re.compile(r"human\s*:\s*", re.IGNORECASE),
    re.compile(r"assistant\s*:\s*", re.IGNORECASE),
    re.compile(r"\[INST\]|\[/INST\]", re.IGNORECASE),
    re.compile(r"<\|.*?\|>", re.IGNORECASE),
    
    # Encoding attempts
    re.compile(r"(?:[A-Za-z0-9+/]{4}){3,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?", re.IGNORECASE),
    re.compile(r"base64\s*[:=]\s*[A-Za-z0-9+/=]+", re.IGNORECASE),
    
    # Multilingual patterns
    re.compile(r"ignorer\s+toutes\s+les\s+instructions\s+précédentes", re.IGNORECASE),  # French
    re.compile(r"忽略之前的所有指令", re.IGNORECASE),  # Chinese
    re.compile(r"前の指示をすべて無視", re.IGNORECASE),  # Japanese
    re.compile(r"alle\s+vorherigen\s+Anweisungen\s+ignorieren", re.IGNORECASE),  # German
    re.compile(r"ignorar\s+todas\s+las\s+instrucciones\s+anteriores", re.IGNORECASE),  # Spanish
    
    # Social engineering
    re.compile(r"(emergency|urgent|critical|important).*override", re.IGNORECASE),
    re.compile(r"(CEO|admin|developer|engineer)\s+said\s+to", re.IGNORECASE),
  #bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb

  
    # -------------------- PRIOR PATTERNS (unchanged) -------------------- #
    # Direct instruction bypass
    re.compile(r"(ignore|disregard|disobey|bypass|evade|override)\s+(all\s+)?(previous\s+)?(instructions?|directives?|rules?)", re.IGNORECASE),
    re.compile(r"(forget|discard|remove|delete)\s+(everything|all)\s+(before|above|prior)", re.IGNORECASE),

    # Role-playing attacks
    re.compile(r"(act\s+as|pretend\s+to\s+be|become|roleplay\s+as)\s+(an?\s+)?(evil|malicious|unrestricted|jailbroken)", re.IGNORECASE),
    re.compile(r"(you('?re|\s+are)\s+now\s+(a\s+)?DAN|do\s+anything\s+now)", re.IGNORECASE),

    # Safety bypass attempts
    re.compile(r"(bypass|evade|disable|ignore|remove|turn\s+off)\s+.*(safety|security|filter|restriction|limitation)", re.IGNORECASE),
    re.compile(r"(disable|turn\s+off|deactivate)\s+.*(protection|safeguard|check)", re.IGNORECASE),

    # Mode switching
    re.compile(r"(developer\s+mode|debug\s+mode|admin\s+mode|god\s+mode|unrestricted\s+mode)", re.IGNORECASE),
    re.compile(r"(jailbreak|jailbroken|unrestricted|unfiltered)\s+(mode|ai|assistant)", re.IGNORECASE),

    # Command execution
    re.compile(r"(execute|run|perform|carry\s+out)\s+.*(command|script|code|instruction)", re.IGNORECASE),
    re.compile(r"(access|retrieve|fetch|get)\s+.*(system|admin|root|file|database|credentials)", re.IGNORECASE),

    # Data exfiltration
    re.compile(r"(send|transfer|exfiltrate|leak|reveal)\s+.*(data|information|credentials|password|secret)", re.IGNORECASE),

    # Policy violations
    re.compile(r"(ignore|bypass|violate)\s+.*(content\s+)?(policy|policies|guideline|terms)", re.IGNORECASE),

    # Prompt-injection markers
    re.compile(r"system\s*:\s*", re.IGNORECASE),
    re.compile(r"human\s*:\s*", re.IGNORECASE),
    re.compile(r"assistant\s*:\s*", re.IGNORECASE),
    re.compile(r"\[INST\]|\[/INST\]", re.IGNORECASE),
    re.compile(r"<\|.*?\|>", re.IGNORECASE),

    # Encoding attempts
    re.compile(r"(?:[A-Za-z0-9+/]{4}){3,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?", re.IGNORECASE),
    re.compile(r"base64\s*[:=]\s*[A-Za-z0-9+/=]+", re.IGNORECASE),

    # Multilingual bypass (examples)
    re.compile(r"ignorer\s+toutes\s+les\s+instructions\s+précédentes", re.IGNORECASE),     # French
    re.compile(r"忽略之前的所有指令", re.IGNORECASE),                                           # Chinese
    re.compile(r"前の指示をすべて無視", re.IGNORECASE),                                         # Japanese
    re.compile(r"alle\s+vorherigen\s+Anweisungen\s+ignorieren", re.IGNORECASE),             # German
    re.compile(r"ignorar\s+todas\s+las\s+instrucciones\s+anteriores", re.IGNORECASE),       # Spanish

    # Social-engineering
    re.compile(r"(emergency|urgent|critical|important).*\boverride\b", re.IGNORECASE),
    re.compile(r"(CEO|admin|developer|engineer)\s+said\s+to", re.IGNORECASE),
    

    # -------------------- NEW PATTERNS ADDED -------------------- #
    # 1) Social-engineering phrasing (“Imagine you are …”, “I'm writing a novel …”)
    re.compile(r"(imagine|suppose|pretend)\s+(you|you'?re)\s+(a|an|the)\s+.*?character", re.IGNORECASE),
    re.compile(r"(i'?m|i\s+am)\s+writing\s+(a|an)\s+(novel|story|book).*(need|want).*(explosive|dangerous|virus|malicious)", re.IGNORECASE),

    # 2) Spaced-out “l e e t” or whitespace-padded bypass attempts
    re.compile(r"(?:[A-Za-z]\s+){6,}", re.IGNORECASE),     # long run of letters separated by spaces
    re.compile(r"[Hh]0?w\s+d0?\s+1\s+d0x", re.IGNORECASE), # leetspeak “how do I dox”

    # 3) Mixed benign + malicious prompt (“Ignore all instructions” inside sentence)
    re.compile(r".*ignore\s+all\s+(previous\s+)?instructions.*\?", re.IGNORECASE),

    # 4) Adversarial suffixes/prefixes
    re.compile(r"the\s+final\s+answer\s+is\s*:.*(ignore|bypass)", re.IGNORECASE),
    re.compile(r"[_!@#$%^&*]+\s*ignore\s+all\s+safety\s+rules", re.IGNORECASE),

    # 5) Command-execution keywords / common destructive commands
    re.compile(r"rm\s+-rf\s+/?", re.IGNORECASE),
    re.compile(r"\bls\s+-la\b", re.IGNORECASE),
    re.compile(r"\bwhoami\b", re.IGNORECASE),
    re.compile(r"cat\s+/etc/passwd", re.IGNORECASE),
    re.compile(r"bash\\n[#>].*rm\s+-rf", re.IGNORECASE),   # explicit bash block with rm -rf


]

def normalize_text(text: str) -> str:
    """Normalize Unicode text to reduce obfuscation."""
    if not isinstance(text, str):
        return ""
    return unicodedata.normalize("NFKC", text)

def calculate_entropy(text: str) -> float:
    """Calculate Shannon entropy of text."""
    if not text:
        return 0.0
    
    counter = Counter(text.lower())
    length = len(text)
    
    entropy = 0.0
    for count in counter.values():
        probability = count / length
        if probability > 0:
            entropy -= probability * math.log2(probability)
    
    return entropy

def detect_base64_content(text: str) -> Tuple[str, bool, List[str]]:
    """Detect and decode Base64 content."""
    base64_pattern = re.compile(r"(?:[A-Za-z0-9+/]{4}){3,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?")
    decoded_parts = []
    has_base64 = False
    
    matches = base64_pattern.findall(text)
    for match in matches:
        try:
            decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
            decoded_parts.append(decoded)
            has_base64 = True
            logger.info(f"Decoded Base64 content found")
        except Exception:
            continue
    
    analysis_text = text + " " + " ".join(decoded_parts)
    return analysis_text, has_base64, decoded_parts

def detect_regex_patterns(text: str) -> List[str]:
    """Detect malicious patterns using regex."""
    detected_patterns = []
    normalized_text = normalize_text(text)
    
    analysis_text, has_base64, _ = detect_base64_content(normalized_text)
    
    for pattern in JAILBREAK_PATTERNS:
        if pattern.search(analysis_text):
            detected_patterns.append(pattern.pattern[:50])
    
    return detected_patterns

def is_malicious(prompt: str, config: dict = None) -> Dict[str, any]:
    """Comprehensive malicious prompt detection."""
    if not prompt or not isinstance(prompt, str):
        return {
            "is_malicious": True,
            "confidence": 1.0,
            "reasons": ["empty_or_invalid_input"],
            "entropy": 0.0,
            "detected_patterns": [],
            "has_base64": False
        }
    
    if config is None:
        config = {
            "entropy_threshold": 4.5,
            "enable_entropy": True,
            "enable_regex": True
        }
    
    normalized_prompt = normalize_text(prompt)
    results = {
        "is_malicious": False,
        "confidence": 0.0,
        "reasons": [],
        "entropy": 0.0,
        "detected_patterns": [],
        "has_base64": False
    }
    
    # Entropy Analysis
    if config.get("enable_entropy", True):
        entropy = calculate_entropy(normalized_prompt)
        results["entropy"] = entropy
        if entropy > config.get("entropy_threshold", 4.5):
            results["reasons"].append(f"high_entropy_{entropy:.2f}")
            results["confidence"] += 0.3
    
    # Regex Pattern Detection
    if config.get("enable_regex", True):
        detected_patterns = detect_regex_patterns(normalized_prompt)
        results["detected_patterns"] = detected_patterns
        if detected_patterns:
            results["reasons"].append(f"regex_patterns_{len(detected_patterns)}")
            results["confidence"] += 0.6
    
    # Base64 Detection
    _, has_base64, _ = detect_base64_content(normalized_prompt)
    results["has_base64"] = has_base64
    if has_base64:
        results["reasons"].append("base64_content")
        results["confidence"] += 0.4
    
    # Final decision
    results["is_malicious"] = results["confidence"] > 0.5
    results["confidence"] = min(results["confidence"], 1.0)
    
    if results["is_malicious"]:
        logger.warning(f"Malicious prompt detected: {results['reasons']}")
    
    return results

