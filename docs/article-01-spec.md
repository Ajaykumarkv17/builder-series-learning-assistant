# Article 1 — Intro & Architecture: What We're Building and Why AgentCore

*Series: Build a Learning Assistant on Amazon Bedrock · Article 1 of 18*

## What we're building

Across this series we build **one** thing: a **learning assistant** — an AI tutor that answers a
learner's questions about a course, grounded in the actual course material, that remembers the
learner across sessions, grades submissions, refuses to hallucinate, and is authenticated,
authorized, measured, and observable in production.

We build it the way you'd build real software: one capability per article, each shipping a working
increment that plugs into the same app. By the end you have a governed, production-grade agent — and
you understand every layer because you added them one at a time.

## The one decision that shapes everything: AgentCore, not legacy Agents

Amazon Bedrock gives you **two** ways to build an agent, and they are not the same product:

| | **Agents for Amazon Bedrock** (legacy) | **Amazon Bedrock AgentCore** |
|---|---|---|
| Model | Managed, **config-based** | **Unopinionated infrastructure** |
| Orchestration loop | **AWS runs it** | **You own it** (your framework + model) |
| You define | Action groups, KBs, prompts | Your agent code; wire in AgentCore services |
| Framework | Bedrock-coupled | Any: Strands, LangGraph, CrewAI, LlamaIndex |
| Model | Bedrock models | **Any** model, in or outside Bedrock |
| Best for | Quick, opinionated agents | Production agents you control end-to-end |

AgentCore went **GA on 2025-10-13** (preview 2025-07-16). It is a set of modular services you use
together or independently:

- **Runtime** — serverless, session-isolated compute (fast cold start, up to 8h, MCP + A2A)
- **Memory** — short-term + long-term + episodic
- **Gateway** — turn APIs / Lambda / MCP servers into agent tools
- **Identity** — agent identity + OAuth token vault (Cognito / Okta / Entra ID)
- **Code Interpreter** + **Browser** — sandboxed code and web tools
- **Observability** — OTEL traces/metrics → CloudWatch
- **Evaluations** (GA) · **Policy** (GA, Dogwood/Cedar) · **Payments** (GA) · **Harness** · **Optimization** · **Registry**

**Why we choose AgentCore for this series:** a learning assistant needs per-learner auth, tool
authorization, memory, evaluation, and observability — production concerns AgentCore provides as
composable infrastructure while we keep full control of the orchestration loop and model choice.
Legacy Agents would hide that loop from us, and the whole point of the series is to *see* each layer.

## End-state architecture

```
   Learner ── HTTPS ──▶  AgentCore Runtime  (serverless, session-isolated, up to 8h)
                          └─ Agent (Strands / LangGraph) · Amazon Nova (Pro + Lite)
                               • Converse API + inference profiles
                               • Prompt Management + Prompt Caching
                                   │            │              │
                          Knowledge Bases   AgentCore      AgentCore
                          (RAG) + Guardrails  Gateway        Memory
                                   │         (tools/MCP)   (S/T + L/T)
                          Identity · Policy (Cedar) · Observability (OTEL)
                          Evaluations · Code Interpreter · Browser tool
```

We'll grow this diagram one box per article.

## Architecture Decision Record (ADR-001)

Decisions we lock now so every later article is consistent:

1. **Platform: AgentCore** (not legacy Agents) — rationale above.
2. **Agent framework: Strands Agents** — AWS-native, minimal boilerplate, first-class AgentCore
   integration. (LangGraph is the swap-in alternative; the series notes where it differs.)
3. **Models: the Amazon Nova family — no Anthropic/Claude anywhere in the series.**
   - **Nova Pro** (`amazon.nova-pro-v1:0`, inference profile `us.amazon.nova-pro-v1:0`) — the primary
     "reasoning" model: complex tutoring, grading, multi-tool agent orchestration. 300K context, multimodal
     (text/image/video in → text out).
   - **Nova Lite** (`amazon.nova-lite-v1:0`, profile `us.amazon.nova-lite-v1:0`) — the fast/cheap tier for
     routing, classification, short answers, and latency-sensitive agent turns. 300K context, multimodal.
   - **Nova Micro** (`amazon.nova-micro-v1:0`) — optional text-only fallback for ultra-cheap classification.
   All addressed through **inference profiles** for cross-Region throughput, via the **Converse API** (both
   Nova Pro and Nova Lite support Converse, streaming, tool use, and batch inference). Model *ids* are pinned
   per-article so samples stay runnable. We route by task: Lite by default, Pro when the step needs it.
4. **Region: one AgentCore GA region** — `us-east-1` (alt `us-west-2`). AgentCore + KB + Guardrails
   feature availability is checked per region before each build.
5. **Language/tooling: Python 3.12+, `boto3`, AgentCore starter toolkit.**
6. **Vector store: start on Amazon S3 Vectors** (low-cost, native) — revisit OpenSearch Serverless in Article 6.

## Cost model (how to reason about the bill)

Bedrock/AgentCore is **consumption-based**; each service is metered independently and the AgentCore
harness itself is free — you pay for underlying resources.

- **Model inference** — per input/output token (Converse). Biggest lever early; **Prompt Caching**
  (Article 4) cuts repeated-prefix cost ~90%.
- **Runtime / Browser / Code Interpreter** — active consumption (~$0.0895/vCPU-hr + $0.00945/GB-hr,
  per-second, I/O wait free).
- **Memory / Gateway / Identity / Web Search / Policy** — each metered separately.
- **Knowledge Bases** — embedding + vector-store cost + retrieval calls.
- New accounts get up to **$200** in free-tier credits.

Every article ends with a **cost note** so the running total is never a surprise.

## What ships in Article 1

- Repo scaffold: `articles/NN-slug/{README.md,code/}`, shared `infra/`, pinned Python env.
- This ADR committed as `docs/adr/0001-platform-and-stack.md`.
- A `make check` / doctor script that verifies AWS creds, region, and Bedrock model access
  (`aws bedrock list-foundation-models`).

## What's next

**Article 2 — Your first call:** the Converse API, streaming, model selection, and inference
profiles — a CLI that answers a single learner question. That's the seed the whole assistant grows from.

---

### Sources
- Amazon Nova models (IDs, context, modalities): https://docs.aws.amazon.com/nova/latest/userguide/what-is-nova.html
- AgentCore overview: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html
- AgentCore GA (2025-10-13): https://aws.amazon.com/about-aws/whats-new/2025/10/amazon-bedrock-agentcore-available
- AgentCore pricing: https://aws.amazon.com/bedrock/agentcore/pricing/
- Legacy vs AgentCore framing: https://repost.aws/questions/QUjkf4WbikQ6WrpuH9sppjnw/bedrock-agents-vs-bedrock-agentcore
