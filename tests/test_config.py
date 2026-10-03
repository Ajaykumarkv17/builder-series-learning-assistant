"""Offline tests for the Nova routing config — no AWS calls, safe to run anywhere."""
from __future__ import annotations

from learning_assistant.config import (
    ALL_MODEL_IDS,
    NOVA_LITE,
    NOVA_PRO,
    Task,
    model_for,
    model_id_for,
)


def test_no_anthropic_models_anywhere():
    for mid in ALL_MODEL_IDS:
        assert "anthropic" not in mid.lower()
        assert "claude" not in mid.lower()
        assert mid.startswith("amazon.nova-")


def test_fast_tier_is_nova_lite():
    assert model_for(Task.FAST) is NOVA_LITE
    assert model_id_for(Task.FAST) == "us.amazon.nova-lite-v1:0"


def test_reasoning_tier_is_nova_pro():
    assert model_for(Task.REASONING) is NOVA_PRO
    assert model_id_for(Task.REASONING) == "us.amazon.nova-pro-v1:0"


def test_base_model_id_available_when_profile_disabled():
    assert model_id_for(Task.REASONING, use_inference_profile=False) == "amazon.nova-pro-v1:0"
