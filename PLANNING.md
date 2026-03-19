# Steward — Local Inference Queue Manager / Scheduler

## Project Title
Local inference queue manager / scheduler for my laptop-hosted inference

## Purpose
I want a queueing and scheduling layer in front of my local inference setup so I can manage requests from myself and later from friends/family or other devices. The system should help prioritize requests intelligently, protect my laptop, and provide visibility into what is running.

---

## 1. My initial ideas

- I may want friends and family to be able to send requests to my laptop-hosted inference system.
- I am thinking about building my own queue management solution for this.
- Requests could include optional arguments like:
  - sender
  - message type, such as question, coding, or other complex task
  - message length, excluding extra OpenClaw or agent-config tokens
- The queueing system could use that information to prioritize requests.
- My own requests should usually get highest priority.
- Exception: if another request would take very little inference time, it might make sense to let that complete first.
- Example distinction:
  - a simple question or plan
  - versus a complex coding or tool-call task
- I am also interested in building a menubar viewer later.
- My current thought is that it probably makes more sense to build the queue system first and then build the menubar viewer on top of it.

---

## AI suggestions

- Build a control plane / scheduling layer, not just a plain FIFO queue.
- Treat this as admission control + scheduling + routing + observability.

### What the system should eventually handle:
- request intake
- metadata normalization
- policy
- priority scoring
- concurrency limits
- routing
- cancellation rules
- observability

### Message fields to consider:
- estimated input tokens
- expected output size/band
- task class
- model preference
- whether tool use is expected

### Work classes to define:
- `interactive_light`
- `interactive_heavy`
- `coding`
- `tooling`
- `vision`
- `background`
- `admin`

### Mapping work classes to policies:
- default model
- timeout
- concurrency policy
- whether the job can be preempted
- whether it is allowed on battery

### Early behavior principles:
- Avoid true preemption at first
- Better: prioritize at admission time, reorder queue before start
- Reserve a fast lane for short/light jobs
- Do not interrupt an active generation unless there is a very good reason

### Backpressure and quotas:
- max queue length
- per-user rate limits
- per-user concurrent request limit
- daily token/time budget
- cooldowns for heavy jobs

### Routing (not just ordering):
- short/simple jobs -> fast model
- coding -> coder model
- deeper planning -> stronger model
- vision -> VL model
- optional cloud fallback if appropriate

### Trust and abuse controls:
- auth per client/device
- API keys or client identity
- allowed task types per user
- attachment size limits
- logging/audit trail
- spam protection

### Queue fairness:
- Weighted fairness + short-job bias + aging so old jobs eventually rise in priority

### ETA estimates should factor:
- queue depth
- model choice
- estimated tokens
- moving-average tokens/sec
- whether model loading is required

### Job states:
- `received`
- `validated`
- `queued`
- `admitted`
- `loading_model`
- `prompt_processing`
- `generating`
- `tool_wait`
- `completed`
- `failed`
- `cancelled`

### Machine-state-aware scheduling:
- on battery vs plugged in
- battery percentage
- thermal pressure
- memory pressure
- quiet-hours or similar policies

### v1 milestone:
A small local inference gateway with request metadata, routing, queueing, and a status endpoint

### Then add:
- observability endpoints like `/status`, `/queue`, `/active-jobs`, `/metrics`
- build the menubar viewer on top of that API (not the other way around)

### Suggested principle:
**The queue/scheduler is the real product; the menubar is just a client of it**

### Suggested v1 architecture:
- **Phase 1:** thin queue + policy layer
- **Phase 2:** one worker and simple scheduler
- **Phase 3:** observability API
- **Phase 4:** menubar viewer

### Suggested request fields:
- `request_id`
- `user_id`
- `client_id`
- `task_class`
- `input_tokens_estimate`
- `expected_output_class`
- `tooling_expected`
- `vision_required`
- `preferred_model`
- `can_use_cloud_fallback`
- `latency_sensitive`
- `submitted_at`

### Suggested server-generated fields:
- `priority_score`
- `chosen_backend`
- `chosen_model`
- `state`
- `eta_seconds`

---

## Open source direction

### Important new direction:
This seems like a strong candidate for my first open source project.


- I want to build this so other people can use and configure it, not just me.
- The target audience is likely small but real:
  people who want to serve local models from their own machine to themselves, friends, or family.
- The project should not be designed only as a personal one-off queue.
- It should be designed as a small configurable local inference gateway.

### What this implies:
- My personal scheduling preferences should be represented as configuration or policy, not hardcoded behavior.
- User priority, short-job bias, rate limits, routing rules, and machine-protection rules should all be configurable.
- The system should be backend-agnostic where possible, ideally starting with a generic OpenAI-compatible backend layer rather than being tightly coupled only to LM Studio.
- A strong first public interface should be:
  - config
  - HTTP/API layer
  - status/metrics endpoints
  - logs
- A menubar viewer should be treated as a client of the queue/gateway, not the core product.
- The scheduler should expose explainable reasoning, such as:
  - why a request got its priority
  - why a model/backend was chosen
  - why a request was queued, delayed, or rejected
- v1 should stay small and practical.

### Suggested open-source-oriented v1 scope:
- one worker
- one queue
- configurable policy
- OpenAI-compatible backend adapter
- request metadata
- status endpoint
- no true preemption yet
- no overcomplicated multi-backend orchestration yet
