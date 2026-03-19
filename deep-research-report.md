# Open-source foundations for a home-hosted inference gateway

## Executive summary

There are several credible open-source “LLM gateway / proxy” projects that already solve the boring but essential parts of a family-and-friends inference service: multi-backend routing, virtual keys, budget/rate-limit enforcement, request logging, and metrics. citeturn11view0turn20view0turn16view0turn36view0turn12view0

What’s missing across the landscape is exactly what you described as the differentiator: a **priority queue with ETA/progress visibility** that is tailored to a single “home inference box” and exposed in a menubar/desktop client. Most gateways can show spend/usage and basic request metrics; very few provide “queue depth + per-request progress” in a way that’s ready to ship to friends/family without custom work. citeturn24view2turn36view2turn20view0turn18view0

If you want the lowest-effort, most-aligned foundations to build on, my top picks are:

- **any-llm-gateway** for “home + friends” governance: virtual keys, per-user spend tracking, budgets, and a clean API, plus explicit support for LM Studio / vLLM / Ollama providers in its provider catalog. citeturn11view0turn12view0turn13search2turn18view0  
- **LiteLLM Proxy** for maximal ecosystem reach and a mature request lifecycle (virtual keys + budgets + team/user rate limits + router + retries/fallbacks), plus first-class “OpenAI-compatible endpoint” support. citeturn20view0turn37view3turn17search2turn37view0  
- **Bifrost** if you want a Go-based gateway with a built-in UI and Prometheus telemetry, and you like the idea of extending via plugins while keeping latency overhead small; it also supports custom base URLs for self-hosted/OpenAI-compatible backends (vLLM/Ollama/etc.). citeturn16view0turn21search1turn36view2turn36view0  

AI suggestions: Treat any of these as the “provider + auth + observability substrate,” then build your **queue/control-plane + menubar client** as a separate layer (or as a plugin/middleware if the gateway supports it cleanly). That division keeps the open-source project modular and makes it useful to others regardless of which gateway/backend they run.

## Candidate landscape

Most relevant projects fall into three buckets:

Gateway/proxy with governance: these typically implement “OpenAI-compatible in, many providers out,” plus virtual keys and usage tracking. Examples include entity["organization","any-llm","mozilla ai sdk"]’s gateway component, entity["organization","LiteLLM","llm proxy library"] Proxy, and entity["organization","Bifrost","maxim ai gateway"]. citeturn11view0turn20view0turn16view0

API-gateway infrastructure pattern: entity["organization","Envoy AI Gateway","envoy gateway llm traffic"] is a strong architecture for orgs already invested in entity["organization","Envoy Gateway","cncf api gateway"] / Kubernetes and a two-tier gateway model (tier-one auth/rate-limit; tier-two self-hosted model ingress). It’s generally overkill for a single MacBook “home inference server,” but it’s worth knowing for future scale-out. citeturn31view1turn31view0

Backend observability as the source of “queue depth”: if you use entity["organization","vLLM","open source inference server"] as a backend, its `/metrics` endpoint exposes “running vs waiting requests” and latency histograms, which are directly useful for a queue/ETA UI; most local GUI servers (LM Studio / Ollama) don’t expose comparable queue metrics today. citeturn24view1turn24view2

## Comparison table

| Candidate | Best fit | Backends (local + cloud) | Auth + attribution | Budgets / rate limits / policy | Observability & ETA hooks | Queue/prioritization readiness |
|---|---|---|---|---|---|---|
| **entity["organization","any-llm-gateway","fastapi llm gateway"]** (Apache-2.0; ~1.8k★) | “governance-first” home/team gateway | Provider catalog explicitly includes LM Studio, Ollama, vLLM, OpenAI, and many others. citeturn13search2turn11view0 | Master key + virtual keys; user attribution required when using master key; virtual keys simplify attribution. citeturn12view0turn18view0 | Budget enforcement + usage analytics; config example includes per-user RPM limit option. citeturn11view0turn12view2turn35view0 | Usage endpoints (e.g., per-user spend) via API; not Prometheus, but easy to poll for menubar dashboards. citeturn18view0 | No native priority queue; best as control-plane substrate (you add queue + ETA). |
| **entity["organization","LiteLLM Proxy","litellm gateway server"]** (MIT core; ~39k★) | “does everything” proxy, wide integration | OpenAI-compatible upstreams via `api_base`, plus provider modules (including LM Studio). citeturn37view3turn17search2turn26view0 | Virtual keys checked against budgets; request flow includes user/team rate limiting. citeturn20view0 | RPM/TPM at global/key/user/team; router strategies, cooldowns, retries/fallbacks; “priority reservation” exists for throughput partitioning. citeturn20view0turn37view0turn37view1 | Rich logging integrations and `/model/info` style endpoints; not “progress,” but plenty of hooks. citeturn20view0turn17search1 | No first-class weighted queue; you can approximate priority via reserved capacity, but not full queue semantics. citeturn37view0turn20view0 |
| **entity["organization","Bifrost","maxim ai gateway"]** (Apache-2.0; ~2.9k★) | “fast gateway + UI + Prometheus” | Multi-provider; supports custom base URL for OpenAI-compatible/self-hosted endpoints; explicit docs for vLLM and Ollama. citeturn16view0turn21search1turn21search7turn21search22 | Virtual keys supported via multiple header styles; can enforce the governance header. citeturn36view0 | Governance docs describe budgets/rate-limits via virtual keys with hierarchy (customers/teams/keys). citeturn36view1turn33search0 | Built-in Prometheus `/metrics`, streaming metrics, and log querying APIs—good raw material for ETA and dashboards. citeturn36view2turn21search4 | Still no explicit “priority queue,” but telemetry makes implementing ETA/queue UX easier than most. citeturn36view2turn24view2 |
| **entity["organization","Squirrel LLM Gateway","mylxsw llm gateway"]** (MIT; ~35★) | “rule-based routing + dashboard” | Proxies OpenAI/Anthropic-compatible APIs; explicitly mentions local models (Ollama, vLLM, LocalAI). citeturn7view3turn8view0turn32view4 | Generates gateway API keys; admin endpoints and optional admin creds. citeturn7view1turn8view0 | Rule-based routing + load balancing strategies; built-in rate-limiting toggle. citeturn7view0turn8view0 | Logs + token tracking + cost analytics + dashboard; good for “who used what,” less for ETA. citeturn7view1turn7view3 | Not a queue product; would need custom queue/ETA layer. |
| **entity["organization","Envoy AI Gateway","envoy gateway llm traffic"]** (Apache-2.0; ~1.4k★) | “Kubernetes-native gateway pattern” | Cloud provider focus; architecture supports self-hosted model clusters behind tier-two gateway. citeturn31view1turn31view0 | Tier-one handles auth + global rate limiting; tier-two handles self-hosted cluster access. citeturn31view1 | Strong for routing/authn/rate-limit in K8s; not targeted at single-host home setups. citeturn31view1 | Observability depends on Envoy/Gateway stack; not “progress.” | Not a queue solution; it’s an infra gateway. |
| **entity["company","Helicone AI Gateway","helicone rust gateway"]** (GPL-3.0; ~549★) | “Rust gateway + routing strategies” | Unified OpenAI-style interface to many providers; supports retries. citeturn4view1turn5search17turn5search3 | Optional “control plane API key” for auth (per docs). citeturn5search3 | Focus is routing and reliability; licensing may be a dealbreaker for your own open-source foundations in some ecosystems. citeturn10view1turn32view0 | Gateway + observability product ecosystem; not queue/progress. citeturn4view2turn5search10 | No priority queue; GPL may constrain remixing. |
| **entity["organization","LLM-API-Key-Proxy","mirrowel proxy project"]** (MIT + LGPL parts; ~424★) | “key rotation + resilience” | “OpenAI-compatible endpoint for all providers,” uses LiteLLM fallback; more cloud-key-management oriented. citeturn14view0turn5search16 | Proxy API key required; supports multiple auth styles for providers; strong logging/sanitization. citeturn14view2turn6view2 | Concurrency limits per key/provider, retries, cooldowns; not really “budgets for family,” more “keep calls working.” citeturn14view1turn14view0 | Logs/per-request metadata exist; not queue/progress. citeturn14view3 | Not a queue product; and less aligned with LM Studio-first home inference. |
| **entity["organization","any_gateway","garricklin ai gateway"]** (~17★) | “small self-hosted gateway” | Multi-backend providers (OpenAI/Anthropic/Gemini) with user mgmt/quota/audit logging per README summary. citeturn32view2turn3view2 | User management present (per repo description). citeturn32view2 | Quota control + audit logging implied; maturity low. citeturn32view2 | Unknown depth of metrics/progress; likely basic. | Too small to bet your project on without deep inspection. |
| **entity["organization","Jan Server","janhq microservices llm api"]** (license varies; check repo) | “full platform: auth + gateway + tools + dashboards” | Wizard can select local vLLM or a remote OpenAI-compatible endpoint; includes an API gateway and tool services. citeturn29view0 | OAuth/OIDC via Keycloak enforced by Kong gateway. citeturn29view0 | Full observability stack called out (Prometheus/Grafana/Jaeger/OTel). citeturn29view0 | Rich monitoring stack; still not a “priority queue + ETA” product. citeturn29view0turn24view2 | Heavyweight; good if you want an all-in-one platform, not a lightweight home queue layer. |

AI suggestions: For your specific “friends/family queue + menubar viewer” goal, pick a gateway with (a) easy local-backend configuration, (b) virtual keys, and (c) some observable hooks (logs/metrics). any-llm-gateway + LiteLLM Proxy are the two cleanest “home-friendly” options; Bifrost is the best “UI + Prometheus” option if you like Go and want metrics-native dashboards.

## Pros, cons, and realistic adoption recommendations

**any-llm-gateway**  
It is explicitly positioned as a FastAPI proxy that adds budget enforcement, API key management, usage analytics, and multi-tenant support, and it exposes an OpenAI-compatible API. citeturn11view0turn6view3 It also documents master key vs virtual key flows and requires a `user` field when authenticating with the master key for correct spend attribution. citeturn12view0turn18view0 The provider catalog includes LM Studio, Ollama, and vLLM entries, which is unusually aligned to your setup. citeturn13search2  
Adoption recommendation: use as-is for auth/spend governance + provider abstraction, then build your own queue/ETA viewer as a separate service that stores request metadata and polls backend metrics where available.

**LiteLLM Proxy**  
Its “life of a request” architecture is one of the clearest documented: virtual key validation (including budget), global/key/user/team RPM/TPM checks, router-based retries/fallbacks/load balancing, and async logging/spend updates. citeturn20view0 It also has explicit “OpenAI-compatible endpoint” configuration patterns via `api_base` and a config-driven model list, making it easy to point at LM Studio / vLLM / other local servers. citeturn37view3turn17search4 It additionally provides a way to reserve throughput across key priorities (“priority reservation”), which can partly approximate “prod > dev” style prioritization. citeturn37view0  
Adoption recommendation: extend via “control plane” rather than forking. Build a small queue service that issues/uses LiteLLM virtual keys per user, and use its logs + routing to implement policy; don’t try to contort LiteLLM into a full scheduling system.

**Bifrost**  
It is explicitly shipped as an OpenAI-compatible gateway with a built-in UI and broad features (fallbacks, load balancing, semantic caching, plugins). citeturn16view0turn21search21 The docs clearly distinguish open-source features from enterprise features in some areas, but governance (virtual keys, budgets/limits) and telemetry are documented as available. citeturn36view0turn36view2turn36view1 Its telemetry page is especially relevant to your “menubar status” idea: Prometheus `/metrics`, cost monitoring, streaming metrics, and label injection via headers. citeturn36view2  
Adoption recommendation: consider it if you want the menubar client to be “metrics-driven” from day one. If you want the simplest “LM Studio proxy + virtual keys + usage,” any-llm-gateway is lower overhead conceptually.

**Squirrel LLM Gateway**  
It has a very practical feature set for small teams: OpenAI/Responses/Anthropic protocol compatibility, routing strategies (round-robin, priority-based, weight-based, cost-based), retries/failover, token tracking, and a dashboard that includes API key lifecycle management and log viewing. citeturn7view0turn7view1turn8view0 It also includes a built-in rate limiting middleware toggle. citeturn8view0  
Adoption recommendation: viable as a foundation if you like its Python+Next approach, but it’s comparatively early (small community). I’d only build your open-source queue project on it if you plan to actually contribute upstream or vendor it.

**Envoy AI Gateway**  
It’s the most “industry standard” architecture, but for a home-hosted MacBook gateway it’s more complexity than value unless you’re already using K8s and want the two-tier model (tier-one auth/rate limits; tier-two self-hosted inference cluster ingress). citeturn31view1  
Adoption recommendation: keep it as a future scale-out reference, not a starting foundation.

**Helicone AI Gateway**  
The repository positioning is a high-performance Rust gateway with “smart routing,” but the **license file is GPLv3**, which can be a practical barrier if you want to reuse/extend the code as a foundation for a permissively licensed open-source project. citeturn10view1turn32view0  
Adoption recommendation: better as a service you deploy and use than as a codebase you build your foundational OSS on, unless you’re comfortable with GPL constraints.

**LLM-API-Key-Proxy / any_gateway / smaller proxies**  
These can be useful references (especially for key rotation and resilience patterns), but they generally don’t provide the “home queue + progress/ETA” story and most have smaller user bases. citeturn14view0turn32view2  
Adoption recommendation: mine for ideas; don’t anchor your “first OSS project” on them unless you’re ready to become the maintainer-of-last-resort.

## Minimal integration paths for the top candidates

### any-llm-gateway minimal path

Goal: one endpoint, per-user virtual keys, LM Studio for local inference, optional cloud fallback later.

1) Run the gateway with docker-compose and a config file; the quick start shows the expected layout and endpoints (health, users, chat completions). citeturn18view0turn12view1

2) Configure providers and pricing in `config.yml`; the docs show the `providers:` and `pricing:` structure, and the supported providers table shows that “lmstudio” exists as a provider ID. citeturn34search0turn13search2

Example `config.yml` (adapt the model IDs to what LM Studio exposes):

```yaml
database_url: "postgresql://gateway:gateway@postgres:5432/gateway"
host: "0.0.0.0"
port: 8000
master_key: "REPLACE_ME_WITH_GENERATED_MASTER_KEY"

# Optional: simple per-user request-per-minute limit (documented in example config)
rate_limit_rpm: 60

providers:
  lmstudio:
    # If your LM Studio server is OpenAI-compatible, set the base URL to its /v1
    api_base: "http://inference.example.ts.net:1234/v1"
    api_key: "ignored-or-blank-if-not-needed"

pricing:
  lmstudio:your-model-id:
    input_price_per_million: 0.0
    output_price_per_million: 0.0
```

The existence and semantics of `rate_limit_rpm` come from the shipped example configuration. citeturn35view0

3) Create users and keys using the API; authentication docs show the “master key + user field” and “virtual key” flows. citeturn12view0turn18view0

```bash
export GATEWAY_MASTER_KEY="REPLACE_ME"
curl -X POST http://localhost:8000/v1/users \
  -H "X-AnyLLM-Key: Bearer ${GATEWAY_MASTER_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"dad","alias":"Dad"}'

curl -X POST http://localhost:8000/v1/keys \
  -H "X-AnyLLM-Key: Bearer ${GATEWAY_MASTER_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"key_name":"dad-iphone"}'
```

4) Your applications (Zed/OpenClaw/menubar client) call the gateway with the virtual key and you get attribution automatically. citeturn12view0turn18view0

AI suggestions: Put “queue metadata” (sender, estimated size class, etc.) into a dedicated request header or into the `user`/metadata fields, then have your queue service read logs from the gateway DB and build an ETA model.

### LiteLLM Proxy minimal path

Goal: keep your existing OpenAI-compatible client tooling, but point it to one proxy that routes to LM Studio / other providers.

1) Configure an OpenAI-compatible upstream in `config.yaml` by setting `model: openai/<name>` and a custom `api_base`. citeturn37view3turn17search4

```yaml
model_list:
  - model_name: local-qwen
    litellm_params:
      model: openai/qwen3-coder-next
      api_base: http://inference.example.ts.net:1234/v1
      api_key: "sk-anything"
```

2) Start the proxy:

```bash
litellm --config ./config.yaml
```

3) Call it using OpenAI SDK conventions; the docs show that you only need to change `base_url` and `api_key` (proxy key if you enable virtual keys). citeturn37view3turn5search5turn20view0

4) If you want lightweight “prioritization,” use priority reservation to carve out capacity between “you” and “everyone else.” This is not a queue, but it is a practical gate. citeturn37view0

AI suggestions: Use LiteLLM’s proxy as the “provider router,” and implement your queue as a **front proxy** that holds requests until your policy selects them, then forwards them to LiteLLM. That avoids hacking LiteLLM internals while still getting its provider ecosystem.

### Bifrost minimal path

Goal: single endpoint with UI-based configuration + Prometheus telemetry for status panels.

1) Run it locally (npx or Docker) as documented in the repo README. citeturn16view0

```bash
npx -y @maximhq/bifrost
# or
docker run -p 8080:8080 maximhq/bifrost
```

2) Configure a provider with a custom base URL to point at your local OpenAI-compatible server (vLLM/Ollama/LiteLLM are explicitly called out as examples). citeturn21search1turn21search0

3) Enable/promote virtual keys for per-user governance; the docs describe supported headers and enforcement options. citeturn36view0

4) For menubar dashboards, scrape `/metrics` and/or query logs using the documented log API endpoints. citeturn36view2turn21search4

AI suggestions: You can implement “queue depth” in two ways: (a) your own queue service keeps canonical queue state, (b) if using vLLM behind Bifrost, also read vLLM’s `num_requests_waiting` style gauges to show backend congestion. citeturn24view1turn24view2turn21search1

## Reference architecture and proxy-backend-menubar interaction

```mermaid
sequenceDiagram
  autonumber
  participant Client as Friend/Family Client
  participant Queue as Home Queue + Policy Service
  participant Proxy as LLM Gateway/Proxy
  participant Backend as Local Inference Backend
  participant Menu as Menubar Status Client

  Client->>Queue: POST /request (message + metadata + user key)
  Queue->>Menu: WebSocket/SSE: queue_len, active_user, eta
  loop scheduling
    Queue->>Proxy: Forward next request (stream=true)
    Proxy->>Backend: OpenAI-compatible call (stream)
    Backend-->>Proxy: SSE tokens + usage
    Proxy-->>Queue: SSE tokens
    Queue-->>Client: SSE tokens
    Queue->>Menu: progress %, tokens/sec, eta updates
  end
```

AI suggestions: If you truly care about progress %, you’ll get the cleanest signal by counting streamed output tokens/chunks and estimating completion based on user-provided `max_tokens` (or empirically derived “typical token count for this request class”), then correcting ETA in real time using observed tokens/sec. If you use vLLM as a backend, you can enrich the menubar with “waiting vs running requests” gauges from `/metrics`. citeturn24view1turn24view2