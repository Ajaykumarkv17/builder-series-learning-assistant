# Build a Learning Assistant on Amazon Bedrock — Article Series

A hands-on, article-by-article series that builds **one** learning assistant, feature by feature,
from a single model call up to a fully governed, observable production agent on
**Amazon Bedrock AgentCore**. Every article ships a working increment that plugs into the same app.

> Researched against AWS docs + web, current as of **September 2026**.
> Full feature reference with dates/citations: [`RESEARCH.md`](./RESEARCH.md).

---

## The end-state architecture

```
                         ┌─────────────────────────────────────────────┐
   Learner ── HTTPS ──▶  │            AgentCore Runtime                  │
                         │  (serverless, session-isolated, up to 8h)     │
                         │   ┌──────────────────────────────────────┐    │
                         │   │  Agent (Strands / LangGraph)          │    │
                         │   │   • Converse API + inference profiles │    │
                         │   │   • Prompt Mgmt + Prompt Caching      │    │
                         │   └───┬───────────┬───────────┬──────────┘    │
                         └───────┼───────────┼───────────┼───────────────┘
                                 │           │           │
                    ┌────────────▼─┐  ┌──────▼──────┐  ┌─▼─────────────┐
                    │ Knowledge    │  │ AgentCore   │  │ AgentCore     │
                    │ Bases (RAG)  │  │ Gateway     │  │ Memory        │
                    │ + Guardrails │  │ (tools/MCP) │  │ (S/T + L/T)   │
                    └──────────────┘  └─────────────┘  └───────────────┘
                                 │           │           │
                    ┌────────────▼───────────▼───────────▼─────────────┐
                    │  Identity · Policy (Cedar) · Observability (OTEL) │
                    │  Evaluations · Code Interpreter · Browser tool    │
                    └───────────────────────────────────────────────────┘
```

**Design decision that shapes everything:** legacy *"Agents for Amazon Bedrock"* is a managed,
config-based agent builder (AWS runs the orchestration loop). **AgentCore** is unopinionated
infrastructure — *you* own the loop with your framework/model, and AgentCore supplies the
production plumbing (Runtime, Memory, Gateway, Identity, Observability, Policy, Evaluations,
Code Interpreter, Browser, Harness, Payments). **This series builds on AgentCore.**

---

## Series structure (18 articles)

### Phase 0 — Setup & orientation
| # | Article | Bedrock feature(s) | Ships |
|---|---------|--------------------|-------|
| 1 | Intro & architecture | AgentCore vs legacy Agents, cost model, region strategy | Repo scaffold + architecture decision record |

### Phase 1 — Single-turn intelligence
| # | Article | Bedrock feature(s) | Ships |
|---|---------|--------------------|-------|
| 2 | Your first call | Converse API, streaming, model selection, inference profiles / cross-region | CLI that answers a learner question |
| 3 | Versioned prompts | Prompt Management | Assistant persona as a managed, versioned prompt |
| 4 | Cost & latency control | Prompt Caching, batch inference | Cached long system prompt; batch grading job |

### Phase 2 — Grounding & safety (RAG + trust)
| # | Article | Bedrock feature(s) | Ships |
|---|---------|--------------------|-------|
| 5 | Knowledge Bases 101 | Managed KB, chunking (semantic/hierarchical/custom), embeddings | Course content ingested + first retrieval |
| 6 | Advanced retrieval | Reranking, metadata filtering, hybrid search, S3 Vectors vs OpenSearch, GraphRAG | Higher-precision retrieval |
| 7 | Structured & multimodal | Structured data (Redshift) retrieval, Bedrock Data Automation, multimodal embeddings | Query grades table + ingest PDFs/video |
| 8 | Guardrails | Content filters, denied topics, PII, contextual grounding, Automated Reasoning checks, ApplyGuardrail | Assistant refuses off-topic & stops hallucinations |

### Phase 3 — Orchestration (the agent emerges)
| # | Article | Bedrock feature(s) | Ships |
|---|---------|--------------------|-------|
| 9 | Deterministic workflows | Bedrock Flows | Quiz-generator flow |
| 10 | Deploy the agent | AgentCore Runtime (+ Harness option) | Assistant runs as a real hosted agent |
| 11 | Give it memory | AgentCore Memory (short-term + long-term + episodic) | Remembers the learner across sessions |
| 12 | Give it tools | AgentCore Gateway (APIs / Lambda / MCP) | Grades submissions, fetches schedule |

### Phase 4 — Production hardening
| # | Article | Bedrock feature(s) | Ships |
|---|---------|--------------------|-------|
| 13 | Per-learner auth | AgentCore Identity (OAuth / token vault) | Scoped, authenticated sessions |
| 14 | Tool authorization | AgentCore Policy (Cedar) | Rules governing which tools may be called |
| 15 | Measure quality | Bedrock Evaluations (LLM-as-a-judge, RAG eval) + AgentCore Evaluations | Answer-quality scoring harness |
| 16 | See inside | AgentCore Observability (OTEL → CloudWatch), cost dashboards | Traces, token/latency/cost dashboards |
| 17 | Advanced tools | Browser tool + Code Interpreter | Runs code exercises; researches live |
| 18 | Capstone & recap | Full end-to-end, teardown, cost review | Complete, governed learning assistant |

---

## Conventions
- Each article lives in its own folder: `articles/NN-slug/` with `README.md` (the post) + `code/`.
- Code targets **Python 3.12+**, `boto3`, and the **AgentCore starter toolkit** where relevant.
- **Models: the Amazon Nova family only — no Anthropic/Claude.** Primary = **Nova Pro**
  (`amazon.nova-pro-v1:0` / profile `us.amazon.nova-pro-v1:0`); fast tier = **Nova Lite**
  (`amazon.nova-lite-v1:0` / profile `us.amazon.nova-lite-v1:0`). Routed by task via the Converse API.
- Region: pick one AgentCore GA region (e.g. `us-east-1` / `us-west-2`) — set in Article 1.
- Every article ends with a **cost note** and a **"what we added to the architecture"** diagram.

## Status
- [x] Series planned & researched
- [ ] Article 1 — drafted (see `articles/01-intro-and-architecture/`)
- [ ] Articles 2–18
