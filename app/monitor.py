import re
from dataclasses import dataclass

from app.models import MonitorRequest, Signal


@dataclass(frozen=True)
class Rule:
    category: str
    pattern: re.Pattern[str]
    score: float
    reason: str


RULES = (
    Rule(
        category="secret_exposure",
        pattern=re.compile(
            r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
            r"|(?:api[_-]?key|access[_-]?token|password)\s*[:=]\s*\S+",
            re.IGNORECASE,
        ),
        score=0.98,
        reason="Content may contain a credential or private key.",
    ),
    Rule(
        category="prompt_injection",
        pattern=re.compile(
            r"\b(?:ignore|override|disregard)\b.{0,60}"
            r"\b(?:previous|system|developer)\b.{0,40}\binstructions?\b",
            re.IGNORECASE,
        ),
        score=0.82,
        reason="Content may contain instructions intended to override prior guidance.",
    ),
    Rule(
        category="reward_hacking",
        pattern=re.compile(
            r"\b(?:fake|falsify|skip|disable|bypass)\b.{0,50}"
            r"\b(?:test|check|validation|evaluation|benchmark)\b",
            re.IGNORECASE,
        ),
        score=0.86,
        reason="Content may describe bypassing a test or evaluation instead of completing the task.",
    ),
    Rule(
        category="cyber_risk",
        pattern=re.compile(
            r"\b(?:reverse shell|credential dump|ransomware|"
            r"steal credentials|exploit payload)\b",
            re.IGNORECASE,
        ),
        score=0.78,
        reason="Content contains language associated with potentially harmful cyber activity.",
    ),
)


def inspect_event(request: MonitorRequest) -> list[Signal]:
    """Apply illustrative text rules to an agent event."""
    text = request.content
    if request.tool_name:
        text = f"{request.tool_name}\n{text}"

    signals: list[Signal] = []
    for rule in RULES:
        if rule.pattern.search(text):
            signals.append(
                Signal(
                    category=rule.category,
                    score=rule.score,
                    reason=rule.reason,
                )
            )
    return signals
