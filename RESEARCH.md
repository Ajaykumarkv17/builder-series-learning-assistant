# Bedrock & AgentCore Feature Reference (as of Sept 2026)

Sourced from AWS docs (docs.aws.amazon.com) + AWS "What's New" / blogs. Dates are announcement
dates. GA = generally available; preview = subject to change. Verify per-region availability before building.

---

## 1. Amazon Bedrock AgentCore — the series backbone

**What it is.** An agentic platform to build, deploy, and operate agents securely at scale using
*any* framework (CrewAI, LangGraph, LlamaIndex, Strands) and *any* model (in or outside Bedrock).
Modular services usable together or independently. No infrastructure to manage.
- Preview: **2025-07-16** (AWS Summit NYC). GA: **2025-10-13**, available in nine AWS Regions at GA.
- Docs: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html

**Core services (per the current AgentCore overview page):**
| Service | Status | Notes |
|---------|--------|-------|
| Harness | GA | Managed agent loop — define+invoke an agent in one API call (model, system prompt, tools inline); isolated microVM with filesystem/shell. Works with Bedrock, OpenAI, Gemini, any OpenAI-compatible provider. |
| Runtime | GA | Serverless, session-isolated, fast cold start, up to 8h sync / async support, built-in identity, multi-modal/multi-agent. Protocols: MCP + A2A. Also **runtime instances** (GA 2026-08) on EC2 for long-running sessions up to 14 days. |
| Memory | GA | Short-term (multi-turn) + long-term (cross-session) + episodic; shareable across agents. |
| Gateway | GA | Turn APIs / Lambda / existing services into MCP tools; connect existing MCP servers. OAuth + IAM. |
| Identity | GA | Agent identity/access; works with Cognito, Okta, Entra ID, Auth0. |
| Code Interpreter | GA | Sandboxed code exec (Python/JS/TS). |
| Browser | GA | Managed headless cloud browser; Playwright / BrowserUse compatible. |
| Observability | GA | OTEL-compatible traces/metrics → CloudWatch; Datadog/Dynatrace/LangSmith/Langfuse/Arize. |
| Payments | GA (2026-08) | Agent microtransactions via x402 + Machine Payments Protocol (MPP); Coinbase CDP / Stripe (Privy) wallets; configurable spending limits. |
| Evaluations | GA (2026-03) | Purpose-built agent evaluation — online (real-time production) + on-demand (regression/dev); 13 built-in evaluators; Ground Truth + custom (LLM or Lambda) evaluators. |
| Policy | GA (2026-03) | Deterministic tool-call authorization attached to a Gateway; author rules in natural language or **Dogwood** (Cedar-compatible policy language). |
| Optimization | current | Continuous improvement — AI-generated recommendations, versioned config bundles, A/B testing (traffic splitting via Gateway); builds on Evaluations. |
| Registry | current | Centralized catalog to discover/manage agents, MCP servers, tools, skills; governed publish/review/approve workflow; hybrid semantic + keyword search. |

**Pricing (high level).** Consumption-based, each service billed independently, harness free.
Runtime microVMs / Browser / Code Interpreter ≈ $0.0895/vCPU-hr + $0.00945/GB-hr (per-second, I/O wait free).
Memory, Gateway, Identity, Web Search, Policy each metered separately. New accounts: up to $200 free-tier credits.
- https://aws.amazon.com/bedrock/agentcore/pricing/

**Legacy vs AgentCore.** *Agents for Amazon Bedrock* = managed, config-based, AWS runs the loop
(action groups, KBs, prompts). *AgentCore* = you own the loop with your framework/model; it supplies
production plumbing. Different tools for different needs; AgentCore does not replace your framework.

---

## 2. Knowledge Bases (RAG)

- **Managed vs Customer-managed KB** split: Managed KB = fully managed RAG (built-in connectors,
  smart parsing, managed vector store, hybrid search, `RetrieveAndGenerate` + **Agentic Retrieval** APIs).
  Customer-managed KB = you configure the vector/text datastores.
- **Vector stores:** OpenSearch Serverless, Aurora PostgreSQL/pgvector, Pinecone, MongoDB Atlas,
  Neptune Analytics (**GraphRAG**, GA), and **Amazon S3 Vectors** (native, low-cost).
- **Embeddings:** Titan Text Embeddings V2 (binary + float; 256/512/1024 dims), Titan G1, Cohere Embed
  (English/Multilingual, binary+float), Titan Multimodal G1, Cohere Embed v3 multimodal,
  **Amazon Nova Multimodal Embeddings**.
- **Chunking:** fixed / semantic / hierarchical / custom (Lambda).
- **Advanced retrieval:** reranking (dedicated rerank models), metadata filtering, hybrid (semantic+keyword) search.
- **Parsing:** FM parsers (Claude/Nova/Llama vision) + **Bedrock Data Automation parser** (preview, us-west-2).
- **Structured data:** natural-language → SQL retrieval over **Amazon Redshift**.
- Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-supported.html ·
  https://docs.aws.amazon.com/bedrock/latest/userguide/kb-how-it-works.html

---

## 3. Guardrails

- **Policies:** content filters (sexual/violence/hate/insults/misconduct/**prompt attack**, text+image),
  denied topics, word filters, **sensitive information filters** (PII + custom regex, mask/block),
  **contextual grounding check** (grounding + relevance scores to catch hallucination),
  **Automated Reasoning checks** (validates responses against formal logic rules; up to ~99% accuracy).
- **ApplyGuardrail API:** standalone — evaluate any text/model with a guardrail, independent of the model call.
- Tiers (Classic / Standard) trade coverage/latency.
- Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html ·
  https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-automated-reasoning-checks.html

---

## 4. Prompt Management & Flows

- **Prompt Management** — versioned, managed prompts. GA 2024-11-06.
- **Bedrock Flows** (renamed from "Prompt Flows") — visual/deterministic multi-step orchestration
  with safety + traceability. GA Nov 2024. "Prompt Flows" is the deprecated name.
- **Prompt Optimization** — auto-rewrite prompts per target model. GA 2025-04.

---

## 5. Evaluations

- **Model evaluation:** automatic, human, and **LLM-as-a-judge** (GA 2025-03).
- **RAG evaluation** (Knowledge Bases) — GA 2025-03; supports bring-your-own inference responses.
- **AgentCore Evaluations** (GA 2026-03) — agent-level task/tool assessment, online + on-demand (see §1).

---

## 6. Supporting primitives

- **Converse API** — unified message API + tool use + streaming. Launched 2024-05-30.
- **Inference profiles / Cross-Region inference** — route across Regions for throughput; **Global CRIS**
  for Claude Sonnet 4/4.5 (2025-09/10). KBs can use inference profiles for parse/generate.
- **Prompt Caching** — cache stable prefixes; ~90% cost / ~85% latency reduction. GA 2025-04.
- **Batch inference** — bulk async jobs at ~50% price; expanded model coverage 2025-08.
- **Bedrock Data Automation (BDA)** — multimodal extraction (docs/images/video/audio). GA 2025-03.
- **Model customization** — fine-tuning, continued pre-training, **distillation**, reinforcement fine-tuning.

---

## 7. Models used by THIS series — Amazon Nova family (no Anthropic/Claude)

This series uses the **Amazon Nova** understanding models exclusively. All support the Converse API,
streaming, tool use, and batch inference, and are available in `us-east-1` (plus Sydney/London/Tokyo
for Pro/Lite/Micro). Address via inference profiles for cross-Region throughput.

| Model | Model ID | Inference profile (US) | Context | Modalities (in → out) | Role in series |
|-------|----------|------------------------|---------|-----------------------|----------------|
| Nova Pro | `amazon.nova-pro-v1:0` | `us.amazon.nova-pro-v1:0` | 300K | Text/Image/Video → Text | Primary: tutoring, grading, agent orchestration |
| Nova Lite | `amazon.nova-lite-v1:0` | `us.amazon.nova-lite-v1:0` | 300K | Text/Image/Video → Text | Fast/cheap tier: routing, short answers, latency-sensitive turns |
| Nova Micro | `amazon.nova-micro-v1:0` | `us.amazon.nova-micro-v1:0` | 128K | Text → Text | Optional ultra-cheap text classification fallback |

Max output 10K tokens; 200+ languages; fine-tuning supported (Pro/Lite multimodal, Micro text).
Nova Pro/Lite are optimized for agentic workflows with KB + RAG — the exact shape this series builds.
- Docs: https://docs.aws.amazon.com/nova/latest/userguide/what-is-nova.html

> Note: the factual AWS capability lists above (FM vision parsers list "Claude/Nova/Llama"; Global CRIS
> example cites Claude) describe what the *platform* supports — they are not model choices. Our series
> pins Nova everywhere a model is invoked.

---

## Notes on evidence
- AgentCore component list, KB embeddings/vector-store/structured-data support, and Guardrails policy set
  are taken directly from the current AWS User Guide / AgentCore Dev Guide pages (Sept 2026).
- The AWS docs search index surfaced some forward-dated model cards (e.g. "Claude Sonnet 5",
  "Claude Opus 4.6"); model *names* were not relied upon for feature claims — only feature/service facts were.
