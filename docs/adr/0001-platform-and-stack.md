# ADR-0001: Platform and stack for the Learning Assistant

- Status: Accepted
- Date: 2026-10-03

## Context
We are building one learning assistant across an 18-article series, adding one Bedrock capability per
article. The foundational decisions below must stay constant so every later article is consistent and
runnable.

## Decisions

1. **Platform: Amazon Bedrock AgentCore** (not legacy "Agents for Amazon Bedrock").
   AgentCore is unopinionated infrastructure — we own the orchestration loop and wire in its modular
   services (Runtime, Memory, Gateway, Identity, Observability, Policy, Evaluations, Code Interpreter,
   Browser). Legacy Agents hides the loop, defeating the series' goal of seeing every layer. GA 2025-10-13.

2. **Agent framework: Strands Agents** (AWS-native, first-class AgentCore integration).
   LangGraph is the documented swap-in alternative; the series notes where it differs.

3. **Models: the Amazon Nova family ONLY — no Anthropic/Claude models anywhere in the series.**
   | Tier | Model | Model ID | US inference profile |
   |------|-------|----------|----------------------|
   | reasoning (primary) | Nova Pro | `amazon.nova-pro-v1:0` | `us.amazon.nova-pro-v1:0` |
   | fast (default) | Nova Lite | `amazon.nova-lite-v1:0` | `us.amazon.nova-lite-v1:0` |
   | cheap (optional) | Nova Micro | `amazon.nova-micro-v1:0` | `us.amazon.nova-micro-v1:0` |
   All invoked via the **Converse API** through **inference profiles** for cross-Region throughput.
   Nova Pro/Lite are multimodal (text/image/video → text), 300K context, and optimized for agentic +
   RAG workflows — the exact shape this series builds. Route by task: Lite by default, Pro when needed.

4. **Region: `us-east-1`** (alternative `us-west-2`). Has the full Nova + AgentCore + KB + Guardrails
   surface. Per-region feature availability is re-checked before each build.

5. **Language/tooling: Python 3.12+, `boto3`, AgentCore starter toolkit.**

6. **Vector store: start on Amazon S3 Vectors** (low-cost, native); revisit OpenSearch Serverless in Article 6.

## Consequences
- Model routing is centralized in `learning_assistant/config.py` (`Task` → Nova model), so a tier can be
  retuned in one place.
- A CI/local guard test asserts no `claude`/`anthropic` id can appear in the model catalog.
- Changing any decision above requires a superseding ADR and propagation across article code.
