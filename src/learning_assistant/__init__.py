"""learning_assistant — shared package for the Bedrock Learning Assistant series.

Article 1 ships only configuration + a doctor. Later articles add the Converse
client (Art. 2), prompt management (Art. 3), KB retrieval (Art. 5), guardrails
(Art. 8), and the AgentCore-hosted agent (Art. 10+).
"""
from __future__ import annotations

from .config import (
    ALL_MODEL_IDS,
    AWS_REGION,
    NOVA_LITE,
    NOVA_MICRO,
    NOVA_PRO,
    NovaModel,
    Task,
    model_for,
    model_id_for,
)

__all__ = [
    "ALL_MODEL_IDS",
    "AWS_REGION",
    "NOVA_LITE",
    "NOVA_MICRO",
    "NOVA_PRO",
    "NovaModel",
    "Task",
    "model_for",
    "model_id_for",
]
