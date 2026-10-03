"""Shared configuration for the Learning Assistant series.

Single source of truth for region and the Amazon Nova model routing used by
EVERY article. No Anthropic/Claude models are used anywhere in this series.

Models (all via the Converse API, addressed through US cross-Region inference
profiles for throughput):

    Nova Pro   amazon.nova-pro-v1:0    us.amazon.nova-pro-v1:0    primary / reasoning
    Nova Lite  amazon.nova-lite-v1:0   us.amazon.nova-lite-v1:0   fast / cheap default
    Nova Micro amazon.nova-micro-v1:0  us.amazon.nova-micro-v1:0  optional text-only fallback

Override any value with an environment variable (see each field below).
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum


# AgentCore GA region. us-east-1 has the full Nova + AgentCore + KB + Guardrails surface.
AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")


class Task(str, Enum):
    """Logical task tiers → mapped to a concrete Nova model by `model_for`."""

    FAST = "fast"        # routing, classification, short answers, latency-sensitive turns
    REASONING = "reason" # tutoring, grading, multi-tool agent orchestration
    CHEAP = "cheap"      # ultra-cheap text-only classification fallback


@dataclass(frozen=True)
class NovaModel:
    name: str
    model_id: str          # base on-demand model id
    inference_profile: str  # US cross-Region inference profile id (preferred for Converse)
    context_window: int


# Canonical Nova catalog (verified against AWS Nova user guide).
NOVA_PRO = NovaModel(
    name="Amazon Nova Pro",
    model_id="amazon.nova-pro-v1:0",
    inference_profile="us.amazon.nova-pro-v1:0",
    context_window=300_000,
)
NOVA_LITE = NovaModel(
    name="Amazon Nova Lite",
    model_id="amazon.nova-lite-v1:0",
    inference_profile="us.amazon.nova-lite-v1:0",
    context_window=300_000,
)
NOVA_MICRO = NovaModel(
    name="Amazon Nova Micro",
    model_id="amazon.nova-micro-v1:0",
    inference_profile="us.amazon.nova-micro-v1:0",
    context_window=128_000,
)

# Task → model routing. Lite is the default; Pro only where the step needs it.
_ROUTING: dict[Task, NovaModel] = {
    Task.FAST: NOVA_LITE,
    Task.REASONING: NOVA_PRO,
    Task.CHEAP: NOVA_MICRO,
}

# Env overrides for the two primary tiers so an article can pin a specific id.
_ENV_OVERRIDE = {
    Task.REASONING: os.getenv("NOVA_REASONING_MODEL_ID"),
    Task.FAST: os.getenv("NOVA_FAST_MODEL_ID"),
}


def model_for(task: Task = Task.FAST) -> NovaModel:
    """Return the Nova model for a logical task tier."""
    return _ROUTING[task]


def model_id_for(task: Task = Task.FAST, *, use_inference_profile: bool = True) -> str:
    """Return the model id to pass to Converse `modelId`.

    Prefers the US cross-Region inference profile. An env override (if set) wins.
    """
    override = _ENV_OVERRIDE.get(task)
    if override:
        return override
    model = model_for(task)
    return model.inference_profile if use_inference_profile else model.model_id


# Every id this series may invoke — used by the doctor script to check access.
ALL_MODEL_IDS: tuple[str, ...] = (
    NOVA_PRO.model_id,
    NOVA_LITE.model_id,
    NOVA_MICRO.model_id,
)
