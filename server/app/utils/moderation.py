"""Rules-based pre-publish moderation (Phase 9 roadmap item).

Deliberately NOT ML — a small, tunable keyword list that routes a
suspicious posting to admin review instead of auto-publishing it.
Tune HIGH_RISK_PHRASES from real flagged content once there's usage
data; that's the intended maintenance loop, not a one-time list.
"""

import re

# Phrases that suggest academic dishonesty (sitting an exam for pay,
# ghostwriting assignments) rather than legitimate tutoring/editing
# help. Matched case-insensitively against title + description.
HIGH_RISK_PHRASES = [
    r"\bsit\s+(my|his|her|their|the)\s+(exam|test|cat)\b",
    r"\btake\s+(my|his|her|their|the)\s+(exam|test|cat)\s+for\s+me\b",
    r"\bwrite\s+(my|his|her|their|the)\s+(exam|test|assignment|essay|thesis)\s+for\s+me\b",
    r"\bdo\s+(my|his|her|their|the)\s+(assignment|homework|exam|cat)\s+for\s+me\b",
    r"\bimpersonat",
    r"\bghost.?writ",
    r"\bpretend\s+to\s+be\s+me\b",
]

_COMPILED = [re.compile(pattern, re.IGNORECASE) for pattern in HIGH_RISK_PHRASES]


def screen_gig_content(title: str, description: str) -> str | None:
    """Returns a human-readable flag reason if the content matches a
    high-risk pattern, otherwise None. Checking title and description
    together catches phrasing split across both fields."""
    combined = f"{title}\n{description}"
    for pattern in _COMPILED:
        if pattern.search(combined):
            return (
                "Auto-flagged: possible academic-integrity violation "
                f"(matched pattern: {pattern.pattern})"
            )
    return None
