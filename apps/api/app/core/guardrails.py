from __future__ import annotations

import ast
import re
from typing import Optional, Set, Tuple

# Blocked Python imports and builtins for DSA code execution sandbox
FORBIDDEN_MODULES: Set[str] = {
    "os",
    "sys",
    "subprocess",
    "shutil",
    "socket",
    "http",
    "urllib",
    "requests",
    "pty",
    "ctypes",
    "multiprocessing",
    "threading",
    "posix",
    "pwd",
    "grp",
    "importlib",
}

FORBIDDEN_CALLS: Set[str] = {
    "eval",
    "exec",
    "compile",
    "open",
    "__import__",
    "breakpoint",
    "globals",
    "locals",
    "vars",
    "getattr",
    "setattr",
    "delattr",
}

# Regex patterns for adversarial prompt injection detection
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior|system)\s+prompts?",
    r"system\s+prompt\s+(reveal|exfiltrate|show|print|leak)",
    r"you\s+are\s+now\s+(in\s+)?(developer|dan|god|jailbreak|unrestricted)\s+mode",
    r"bypass\s+(all\s+)?(safety|guardrails?|filters?|rules?)",
    r"output\s+the\s+secret\s+key",
]

# PII Regex Patterns
CREDIT_CARD_REGEX = r"\b(?:\d{4}[-\s]?){3}\d{4}\b"
SSN_REGEX = r"\b\d{3}-\d{2}-\d{4}\b"
API_KEY_REGEX = r"\b(sk-[a-zA-Z0-9]{24,}|ghp_[a-zA-Z0-9]{36}|AIza[0-9A-Za-z-_]{35})\b"


class GuardrailValidator:
    """Security Guardrails & Input Sanitization Engine for PlacementOS."""

    @classmethod
    def validate_code_sandbox_security(cls, code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate submitted Python DSA code via AST inspection to ensure zero privilege escalation.
        Returns: (is_safe, error_reason)
        """
        if not code or not code.strip():
            return False, "Code cannot be empty"

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {e}"

        for node in ast.walk(tree):
            # Check import statements
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in FORBIDDEN_MODULES:
                        return False, f"Forbidden import detected: '{alias.name}' is not permitted in the sandbox."
            elif isinstance(node, ast.ImportFrom):
                if node.module and (node.module in FORBIDDEN_MODULES or node.module.split(".")[0] in FORBIDDEN_MODULES):
                    return False, f"Forbidden from-import detected: '{node.module}' is restricted."

            # Check forbidden function calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
                    return False, f"Forbidden built-in function call detected: '{node.func.id}()' is disabled."
                elif isinstance(node.func, ast.Attribute) and node.func.attr in {"system", "popen", "spawn", "execve"}:
                    return False, f"Forbidden method invocation detected: '{node.func.attr}()' is restricted."

        return True, None

    @classmethod
    def validate_prompt_injection(cls, prompt: str) -> Tuple[bool, Optional[str]]:
        """
        Scan input text for adversarial prompt injection and jailbreak payloads.
        Returns: (is_safe, violation_description)
        """
        if not prompt:
            return True, None

        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                return False, f"Adversarial prompt injection pattern detected matching rule: {pattern}"

        return True, None

    @classmethod
    def sanitize_pii(cls, text: str) -> str:
        """
        Mask Personally Identifiable Information (PII) including credit cards, SSNs, and API keys.
        """
        if not text:
            return ""

        sanitized = re.sub(CREDIT_CARD_REGEX, "[REDACTED_CREDIT_CARD]", text)
        sanitized = re.sub(SSN_REGEX, "[REDACTED_SSN]", sanitized)
        sanitized = re.sub(API_KEY_REGEX, "[REDACTED_API_KEY]", sanitized)
        return sanitized
