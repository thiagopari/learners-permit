# Track F: measurements of our own running system (ShiftLead on the Dell Pro Max GB10)

Measured 2026-10-03, 14:31-14:49 ET. Strictly read-only: HTTP GET to localhost, `docker logs/stats/ps`, `nvidia-smi`,
`free`, `/proc`, reading files. No POST/PATCH, nothing under `/demo/*`, no restarts, no `docker exec`.

Labels used below: **MEASURED** = read straight from a counter, log or endpoint. **CALCULATION** = arithmetic on measured
values (inputs shown). **ESTIMATE** / **PROJECTION** = depends on stated assumptions.

Time zones: all times are ET (EDT, UTC-4). The box clock is UTC-5, so the tool service's own timestamps (tickets,
notifications, `/metrics.time`) read one hour earlier than ET; container logs are UTC. Everything below is converted to ET.

---

## 0. Key numbers

| What | Value | Status |
|---|---|---|
| LLM requests served (12:09-14:43 ET) | 249 completed, 0 errors, 0 aborts, 0 preemptions | MEASURED |
| Prompt tokens per call | mean 30.3K, p50 ~27K, p95 ~93K, p99 ~169K | MEASURED (bucket-interpolated percentiles) |
| Output tokens per call | mean 514, p50 ~280, p95 ~2.3K (thinking off) | MEASURED |
| Prefix-cache hit rate | 83.0% of prompt tokens (lifetime); 78.5% inside the 9-min snapshot window | MEASURED |
| End-to-end latency per call | mean 14.1 s, p50 6.75 s, p95 49 s, p99 116 s | MEASURED |
| Time to first token | mean 1.5 s, p50 0.62 s, p95 5.8 s | MEASURED |
| Single-stream decode | 66-69 tok/s typical (range 63.5-78 over 18 ten-second windows) | MEASURED |
| Aggregate decode | 97 tok/s average over the busiest 10 min; 142 tok/s peak at 4 concurrent calls | MEASURED |
| Request rate, snapshot window 14:34:05-14:43:05 | 44 requests = 4.9/min (demo active about 6 of the 9 minutes) | CALCULATION |
| Request rate, busiest 10 min (14:21-14:31) | 9.8/min, max 4 concurrent, 0 queued | MEASURED |
| LLM calls per agent wake (one autopilot hook call) | ~9 (7.7-9.3 across four windows) | MEASURED |
| LLM calls per ticket created | 2.4-4.9 | CALCULATION |
| Tokens per wake | ~273K prompt (227K cached, 46K uncached), ~4.6K output | CALCULATION |
| Typical site/day (100 events + brief + 2 shift summaries + 30 chat questions) | ~1,065 calls; 32.3M prompt tokens (26.8M cached, 5.5M uncached); 0.55M output | PROJECTION |
| Headroom | demonstrated rate is ~13x a typical site's daily-average load, ~4x its assumed peak hour | ESTIMATE |

---

## 1. Raw values

### 1.1 vLLM `/metrics` counters (http://localhost:8000/metrics)

| Counter | 14:31 ET (from the task brief, approx.) | Snapshot 1, 14:34:05 ET | Snapshot 2, 14:43:05 ET | Delta S1 to S2 (9.0 min) |
|---|---|---|---|---|
| `vllm:prompt_tokens_total` | ~6.27M | 6,597,690 | 7,672,076 | +1,074,386 |
| `vllm:prompt_tokens_cached_total` (= `by_source{local_cache_hit}`) | | 5,539,728 | 6,369,744 | +830,016 |
| `vllm:prompt_tokens_by_source{local_compute}` | | 1,057,962 | 1,302,332 | +244,370 |
| `vllm:generation_tokens_total` | ~88K | 94,743 | 128,385 | +33,642 |
| `vllm:request_success_total` (stop + length) | 193 | 205 (201 + 4) | 249 (245 + 4) | +44 |
| `request_success_total` abort / error / repetition | | 0 / 0 / 0 | 0 / 0 / 0 | |
| `vllm:prefix_cache_queries_total` | | 6,662,744 | 7,706,604 | +1,043,860 |
| `vllm:prefix_cache_hits_total` | | 5,575,360 | 6,394,896 | +819,536 |
| `vllm:num_preemptions_total` | | 0 | 0 | 0 |
| `vllm:num_requests_running` / `waiting` (gauges) | | 2 / 0 | 0 / 0 | |
| `vllm:kv_cache_usage_perc` (gauge) | | 1.73% | 0.0% | |
| `e2e_request_latency_seconds` count / sum | | 205 / 2,575.2 s | 249 / 3,521.3 s | +44 / +946.1 s |
| `time_to_first_token_seconds` count / sum | | 208 / 323.0 s | 251 / 382.4 s | +43 / +59.4 s |
| `http_requests_total` POST `/v1/chat/completions` | | 206 | 250 | +44 |
| `http_requests_total` POST `/v1/responses` | | 1 | 1 | 0 |

The vLLM process started 12:04:31 ET, the engine and its metrics at 12:08:48 ET, and the first request arrived at 12:09:12 ET.
So the counters cover 154 minutes, mostly idle apart from three bursts of agent activity (13:00-13:20, 14:10-14:39,
14:39-14:44 ET).

### 1.2 Per-request histograms (cumulative at snapshot 2, n = 249 completed requests)

Means are exact (sum/count). Percentiles are linear interpolation inside Prometheus buckets, and the buckets are coarse
(for example 20K-50K tokens), so treat percentiles as approximate.

| Histogram | mean | p50 | p90 | p95 | p99 |
|---|---|---|---|---|---|
| Prompt tokens per request | 30,321 | 26,800 | 74,400 | 93,300 | 168,900 |
| Uncached prompt tokens per request (`request_prefill_kv_computed_tokens`) | 5,202 | 2,090 | 14,300 | 24,200 | 58,500 |
| Generation tokens per request | 514 | 279 | 1,480 | 2,330 | 4,470 |
| End-to-end latency (s) | 14.1 | 6.75 | 35.8 | 49.4 | 116 |
| Time to first token (s), n = 251 | 1.52 | 0.62 | 3.74 | 5.78 | 23.3 |
| Prefill time (s) | 1.39 | 0.53 | 3.43 | 5.31 | 21.7 |
| Decode time (s) | 12.6 | 4.94 | 33.4 | 49.1 | 110 |
| Inter-token latency (ms), n = 128,134 tokens | 24.6 | 22.9 | 44.3 | 47.4 | 49.8 |
| Queue time (s) | 0.040 | at S1, 204 of 205 requests waited under 0.3 s; one waited 5-10 s | | | |

Raw buckets at S1 (n = 205): prompt tokens: up to 5K: 4; 5K-10K: 52; 10K-20K: 28; 20K-50K: 81; 50K-100K: 32; 100K-200K: 8.
Generation tokens: up to 50: 5; 50-100: 45; 100-200: 44; 200-500: 60; 500-1K: 27; 1K-2K: 14; 2K-5K: 10. Four requests
stopped at `max_tokens` (finished_reason=length).

Only the 44 requests inside the S1 to S2 window: prompt mean 24,970 (p50 26,700, p95 48,700); generation mean 778 (p50 436,
p95 3,350); end-to-end mean 21.5 s (p50 12.5 s, p95 84 s); time to first token mean 1.38 s (p50 0.70 s, p95 5.7 s).

### 1.3 vLLM configuration (startup lines in `docker logs vllm-qwen`, 12:04-12:08 ET)

- Image `nvcr.io/nvidia/vllm:26.05.post1-py3`, vLLM 0.21.0. Architecture `Qwen3_5MoeForConditionalGeneration` (hybrid Gated
  DeltaNet "mamba" layers plus attention), text-only mode.
- `max_model_len` 262,144; fp8 KV cache; prefix caching on (vLLM flags its Mamba "align" mode as experimental); chunked
  prefill with `max_num_batched_tokens` 8,192; asynchronous scheduling.
- `gpu_memory_utilization` 0.5. Model weights 19.52 GiB; "Available KV cache memory: 36.92 GiB"; "GPU KV cache size:
  3,666,044 tokens"; "Maximum concurrency for 262,144 tokens per request: 13.98x".
- The NVFP4 MoE uses the MARLIN backend, and vLLM warns: "Your GPU does not have native support for FP4 computation but FP4
  quantization is being used. Weight-only FP4 compression will be used leveraging the Marlin kernel." In other words, this build
  runs the weights through a weight-only FP4 path, not native FP4 compute.
- Tool parser `qwen3_coder` with auto tool choice. Default sampling comes from the model's generation_config (temperature 1.0,
  top_k 20, top_p 0.95).
- Cold start: loading weights took 121.6 s, torch.compile 58.4 s, engine init 111.3 s; about 4.3 minutes from container start
  to serving.

### 1.4 vLLM 10-second engine log lines (`docker logs -t vllm-qwen`)

- The "Avg prompt throughput" in these lines counts only uncached (computed) prompt tokens. Summed up to S1 it gives 1,057,868
  tokens, against the `local_compute` counter's 1,057,962.
- 18 ten-second windows had exactly one request in pure decode (no prefill): 63.5-78.2 tok/s, typically 66-69 tok/s
  (14:18:19-14:18:39, 14:33:09-14:33:39, 14:40:19-14:41:29 ET).
- Aggregate generation tok/s by number of running requests (all 10-second windows): 1 running: median 58, max 98;
  2 running: median 87, max 108; 3 running: median 99, max 121; 4 running: median 104, max 142.
- No 10-second window ever had a waiting request. Maximum KV cache usage was 5.0%. The highest uncached prefill in a
  10-second window was 10,901 tok/s.
- LLM requests per 5 minutes (ET): 12:05: 1 | 12:30: 1 | 13:00: 18 | 13:05: 3 | 13:15: 11 | 13:45: 3 | 14:10: 14 | 14:15: 32 |
  14:20: 40 | 14:25: 49 | 14:30: 46. Per minute after that: 14:35: 11 | 14:36: 6 | 14:37: 3 | 14:38: 2 | 14:39: 4 | 14:40: 4 |
  14:41: 1 | 14:42: 2 | 14:43: 15.

### 1.5 Tool service (GET only, http://localhost:8090)

**Snapshot A, 14:34:47 ET.** The service had been up 6.7 min (restarted 14:28:03 ET).
- `/metrics`: 20 robots, all 20 with active problems; active events: overheat 19, low_stock 7, stuck 1, inventory_mismatch 1;
  `events.raised_total` 102; 18 open tickets.
- `/autopilot`: triage on, every 30 s, min_age 5 s, cooldown 300 s, `brief_every_s` 0 (off), `wakes_agent` true,
  `posts_to` null, `problems_handed_over` 32.
- `/notifications`: 18 entries. 7 are agent wakes ("triage", HTTP 200) at 14:28:15, 14:28:45, 14:30:37, 14:32:15, 14:33:45,
  14:34:15 and 14:34:45. The other 11 are scheduler notices ("no webhook configured").
- `/tickets`: T-1 to T-18, all open. `/events?status=all`: 50 events since the restart (E-0053 to E-0102): stuck 21,
  overheat 19, low_stock 7, other 3.
- Process settings read from `/proc/<pid>/environ` (non-secret keys only): `SUPERVISOR_THINKING=off`, `BRIEF_EVERY_S` unset
  (off), `SUPERVISOR_DELIVER_TO` unset (agent replies were not being posted to Discord).

**Snapshot B, 14:43:05 ET.** The other session restarted the service at 14:39:55 ET with `TRIAGE=0` and a new sim source
(127.0.0.1:3001). State: 0 tickets, empty outbox, triage false, 21 events raised (stuck 11, deadlock 8, inventory_mismatch 1,
overheat 1).

**Archived runs** (files, read only):
- `data/test-run-1/tickets.json`: 10 tickets created 13:01-13:19 ET.
- `data/test-run-2/tickets.json`: 41 tickets created 14:14:56-14:37:24 ET (overheat 20, stuck 9, low_stock 7,
  inventory_mismatch 2, throughput_drop 2, deadlock 1). All still open; 2 PATCH updates.
- `tools.log` holds only the two "listening" lines, because the service suppresses per-request logging. It cannot be used for
  counts.

### 1.6 Agent sandbox log (`docker logs -t openshell-default--navfix-...`, from 13:50 ET)

- Each autopilot wake appears as an inbound `NET:OPEN 127.0.0.1:18789/tcp`. There were 31 since 13:53 ET: 4 at 13:53:44-45 and
  3 at 14:11:30-37 (startup and tests), 21 in run 2 (14:14:14-14:35:46), and 3 in run 3 (14:39:46, 14:43:23, 14:43:53). The 7
  wakes listed in `/notifications` match these one-to-one.
- Each model call appears as `API:INFERENCE Success nvidia/Qwen3.6-35B-A3B-NVFP4 ... <n>ms [POST /v1/chat/completions]`. There
  were 223 calls between 14:11:40 and 14:44:06 ET, the same count as the vLLM access log over that period. So all vLLM traffic
  since 14:10 ET came from the agent sandbox.
- Call duration as the agent saw it (n = 193, up to 14:37): mean 15.3 s, p50 6.9 s, p90 36.4 s, p95 55.2 s, max 133.5 s.
  25% of calls took 3.4 s or less.
- Tool HTTP calls in run 2: 120 in total. `POST /tickets` 63, `GET /events` 12, `GET /fleet` 11, `GET /tickets` 11,
  `GET /zones/N/inventory` 9, `GET /trust` 7, `GET /metrics` 3, `GET /robots/N` 2, `PATCH /tickets` 2.
- Single model calls started over SSH (the other session's developer) at 14:42:14, 14:42:23 and 14:43:07 took one model call
  each.

### 1.7 Resources

| Reading | Time (ET) | Value |
|---|---|---|
| `nvidia-smi` (GB10) | 14:35:32 | GPU util 96%, 58-60 W, 68-69 C, SM clock 2,489 MHz (max 3,003), P0. 2-4 LLM requests were running |
| `nvidia-smi` per process | 14:35:32 | VLLM::EngineCore 60,433 MiB; two GR00T `python` servers 6,501 and 6,669 MiB; desktop (Xorg, gnome-shell, firefox, nautilus, baobab) ~664 MiB. `memory.used`/`total` report N/A (unified memory) |
| `nvidia-smi` at 1 Hz, 31 samples | 14:39:01-14:39:31 | idle: util mean 1% (max 4%), 13.4-14.1 W, 54-55 C |
| `nvidia-smi` | 14:43:05 | 0%, 12.9 W, 49 C |
| `docker stats` | 14:35:27 | vllm-qwen 2.80 GiB (CPU 103%); cell 8.00 GiB (CPU 0.6%); sandbox 736 MiB (CPU 111%) |
| `docker stats` | 14:43:05 | vllm-qwen 2.80 GiB (1.7%); cell 8.03 GiB (7.4%); sandbox 917 MiB (133%) |
| `free -g` | 14:35 | total 121, used 91, free 9, buff/cache 22, available 30. Swap 15 GiB, 1.7 GiB used |
| `free -g` | 14:43 | total 121, used 91, free 8, buff/cache 22, available 30 |
| `/proc/meminfo`, `/proc/loadavg` | 14:39 | MemTotal 127,533,256 kB (121.6 GiB), MemAvailable 32.3 GB; load average 1.85 / 2.59 / 2.44 |

`docker stats` for vllm-qwen counts only CPU-side memory. GPU allocations on GB10's unified memory show in `nvidia-smi`, not
in the container's cgroup. The power figure is the GPU reading from `nvidia-smi`, not wall power.

---

## 2. Analysis

### 2.1 LLM usage per request (MEASURED, 249 requests, about 85% of them from run 2)

- **Prompt-heavy workload.** Over the whole lifetime, prompt to output is 60:1 (7.67M to 128K tokens). Counting only uncached
  prompt tokens it is 10:1. Every call re-sends OpenClaw's system prompt, the skill, and the tool results gathered so far. During
  the demo, `GET /events` returned 18-35 KB of JSON (20-30 active events).
- **Prefix cache does most of the work.** 83.0% of prompt tokens were cache hits (6,394,896 of 7,706,604 queried; cached/total
  gives the same 83.0%). Per request, a mean of only 5.2K tokens (p50 2.1K) had to be computed.
- **Output is short.** Mean 514 tokens, p50 ~280, with thinking off as configured. The longest outputs are tool calls with
  JSON bodies.
- **Latency.** End-to-end mean 14.1 s, p50 6.75 s, p95 49 s. Time to first token p50 0.62 s, p95 5.8 s. Queueing was
  effectively zero (mean 0.04 s). Decode is 89% of total request time (3,142 s of 3,521 s; prefill is 347 s), so the length
  of the output, not the prompt, sets wall time.
- **Generation throughput.** One stream alone decodes at 66-69 tok/s. Under the real mix, each stream ran at ~41-44 tok/s
  (inter-token latency mean 24.6 ms, p50 22.9 ms). The box as a whole produced 97 tok/s on average over the busiest 10
  minutes, peaking at 142 tok/s with 4 concurrent calls.
- **Prefill.** Effective uncached prefill was ~3.7K tok/s per request (1.295M computed tokens over 346.6 s of prefill time),
  and up to 10.9K tok/s averaged over a 10-second window.

### 2.2 Request rate (two snapshots)

CALCULATION:
- **S1 to S2 (14:34:05 to 14:43:05, 9.0 min):** 44 requests = 4.9/min. 1.07M prompt tokens = 119K/min (77% cached).
  33.6K output tokens = 3.7K/min (62 tok/s).
- **Was the demo being exercised?** Partly. Autopilot triage on injected systemic faults (a 19-robot overheat, low stock in
  every zone) ran until about 14:38 ET. The other session restarted the tool service at 14:39:55 with triage off and switched
  to a new sim. After that came one wake at 14:39:46 (9 calls, to 14:41:34), three single developer calls over SSH
  (14:42:14-14:43:09), and two more wakes at 14:43:23 and 14:43:53, just after S2. The system was idle from 14:38:16 to
  14:39:46.
- **Busy-state rate:** 9.8 requests/min in the busiest 10 minutes (14:21-14:31) and 7.9/min across run 2 (14:14-14:39:30).
  Averaged over vLLM's 154-minute life it is 1.6/min.
- **Context:** the demo compresses a working day into minutes. Run 2 produced 41 tickets in 23 minutes. The "typical" site
  in the projection averages 0.74 calls/min, so the demo ran at about 7-13x that rate.

### 2.3 Agent workload and LLM calls per handled event

MEASURED counts:

| Window (ET) | Agent wakes (hook calls) | LLM calls | Tool HTTP calls | Tickets created | LLM calls per wake |
|---|---|---|---|---|---|
| Run 2, 14:14:00-14:39:30 | 21 | 196 | 120 | 41 | 9.3 |
| Run 2, second service lifetime, 14:28:15-14:39:30 | 9 | 81 | 66 | 34 (T-8 to T-41) | 9.0 |
| The 7 wakes listed in `/notifications`, 14:28:15-14:34:47 | 7 | 54 | n/a | 11 (T-8 to T-18) | 7.7 |
| Isolated wake 14:39:46 (calls 14:39:48-14:41:34) | 1 | 9 | 6 (3 `POST /tickets`) | none kept (service restarted underneath) | 9.0 |
| Run 3 wakes 14:43:23 and 14:43:53 | 2 | 17 | 6 | not observed | 8.5 |

Session totals: at least 130 events (run 2 used at least 109 event ids, with `raised_total` at 102 by 14:34:47; run 3 had 21
by 14:43); 51 tickets (10 in run 1, 41 in run 2); 31 hook connections since 13:53 ET (24 from autopilot runs, 7
startup/tests); 249 LLM requests by 14:43:05. Run 1's wakes are not visible, because its sandbox container was replaced at
13:53 ET.

What it means (CALCULATION):
- **About 9 LLM calls per agent wake** (7.7-9.3 across windows). A wake typically runs: read the skill, `GET /events`,
  `GET /trust`, one or more `POST /tickets`, and a final reply. Calls per wake barely changed between wakes that filed 1-2
  tickets and wakes that filed 9, because the model batches parallel tool calls: one response at 14:35:04 issued 9
  `POST /tickets`.
- **2.4-4.9 LLM calls per ticket created.** In the 7-wake window, where one wake grouped "overheat x19", it was **1.7 calls
  per problem handed over** (54 calls for 32 problems).
- **Tokens per wake** (9 calls x per-call means): ~273K prompt (227K cached, 46K uncached) and ~4.6K output. Cross-check
  against the 10-second logs: the isolated 14:39:46 wake used 35.9K uncached prompt and 6.6K output; the two run-3 wakes used
  16.5K uncached and 2.2K output each. So 46K uncached / 4.6K output per wake sits mid-to-high in what we observed.
- **Time to handle a wake.** The isolated wake took 108 s from hook to last model call, and was decode-bound (~6.6K output
  tokens at ~66 tok/s). From wake to first ticket took 19-84 s in the wakes observed (14:28:15 to T-8 at 14:28:48;
  14:30:37 to T-17 at 14:31:52; 14:39:46 to first POST at 14:40:05).
- **Waste worth fixing.** Run 2 made 63 `POST /tickets` for 41 tickets created; the other 22 were duplicates or rejected
  (responses are not logged). Large `GET /events` payloads inflate every later call in a wake. Trimming `/events` and avoiding
  duplicate posts should cut tokens; I have not measured how much.

### 2.4 Resource footprint, next to the deck's official figures

The deck figures are official. My readings are labeled as snapshots.

| Item | Deck (official) | My reading (snapshot at <time>, may include load) | Note |
|---|---|---|---|
| Decode speed | ~62 tok/s | Snapshot at 14:18, 14:33 and 14:40-14:41 ET, may include load: 66-69 tok/s single-stream at ~27K-token contexts. 97 tok/s aggregate average and 142 tok/s peak with 2-4 concurrent calls | Consistent; batching raises the aggregate |
| Time per tool-calling turn | ~3.4 s | Snapshot 12:09-14:43 ET, may include load: per-call p50 6.75 s, mean 14.1 s, p95 49 s; 25% of the agent's calls took 3.4 s or less | Different conditions. Live calls averaged 30K-token prompts with 2-4 sessions at once, and a whole wake (9 calls) took ~108 s end to end. If the deck shows 3.4 s, state the condition it was measured under |
| vLLM memory | ~57 GB | Snapshot at 14:35 ET, may include load: 60,433 MiB (59.0 GiB = 63.4 GB) in `nvidia-smi`; that is weights 19.5 GiB + KV cache 36.9 GiB + overhead | Same order of magnitude. The amount is pre-allocated (`gpu_memory_utilization` 0.5) and does not change with load. The gap is probably units or method |
| GR00T, two servers | ~20 GB | Snapshot at 14:35 ET, may include load: 6,501 + 6,669 MiB GPU (12.9 GiB) + the `cell` container's 8.0 GiB host RAM = ~21 GiB | Consistent |
| Total memory in use | ~88 GB of 128 GB at idle | Snapshot at 14:35 and 14:43 ET, may include load: 91 GiB used of 121.6 GiB visible to the OS, 30 GiB available | Consistent (my figure includes desktop apps and the sandbox) |
| Commissioning run C-3 | 20 trials in 181 s | Not re-run (the trust store has since been reset). `data/clips/C-3` holds 20 clips (5 libero_10 + 15 libero_goal), written 13:11:06-13:13:37 ET | Consistent with the deck |
| GPU power | (not in deck) | Snapshot at 14:35:32 ET under load: 96% util, 58-60 W. Idle 14:39 ET: 13-14 W, ~1% | GPU rail as reported by `nvidia-smi`, not wall power |

### 2.5 PROJECTION: one site per day (labeled projection, every assumption stated)

**Measured basis** (cumulative at S2, 249 calls):
- 30,321 prompt tokens per LLM call, 83.0% cached
- 514 output tokens per call
- ~9 calls per agent run (wake)

**Assumptions**
- A1. One handled event = one agent wake of 9 calls (measured 7.7-9.3). This is conservative: at a calm site each problem
  arrives alone, while grouping cuts cost (1.7 calls per problem in the demo when 19 problems were grouped).
- A2. Per-call token counts equal the measured means. These are probably high for a calm site, because the demo had 20-30
  active events inflating every `GET /events` result.
- A3. A morning brief is one 9-call run. A shift summary is 18 calls (two runs' worth: more reads, such as per-zone inventory,
  and a longer write-up). Neither was measured, since the brief was switched off.
- A4. A chat question is 4 calls (1-2 tool calls plus the reply). Not measured. The three developer calls observed were single
  calls, so 4 is generous.
- A5. Thinking stays off, as configured. Turning it on would raise output tokens by an unmeasured amount.
- A6. Shift summaries per day: light 1, typical 2, heavy 3 (24/7 operation).
- A7. Token counts are Qwen-tokenizer counts. A cloud model's tokenizer will count the same text somewhat differently.

**Formula**
- calls = 9 x (events + briefs + 2 x shift summaries) + 4 x chat questions
- prompt tokens = calls x 30,321; cached = 0.830 x prompt tokens
- output tokens = calls x 514

| Scenario (per site per day) | Activity | LLM calls/day | Input (prompt) tokens/day | of which cached (83.0%) | Uncached input | Output tokens/day |
|---|---|---|---|---|---|---|
| Light | 20 events, 1 morning brief, 1 shift summary, 10 chat questions | 247 | 7.49M | 6.22M | 1.27M | 0.127M |
| Typical | 100 events, 1 morning brief, 2 shift summaries, 30 chat questions | 1,065 | 32.3M | 26.8M | 5.48M | 0.548M |
| Heavy | 300 events, 1 morning brief, 3 shift summaries, 60 chat questions | 3,003 | 91.1M | 75.6M | 15.5M | 1.54M |

Exact daily values (light / typical / heavy):
- input: 7,489,180 / 32,291,403 / 91,052,660
- cached: 6,217,894 / 26,809,950 / 75,596,506
- uncached: 1,271,285 / 5,481,453 / 15,456,155
- output: 126,982 / 547,513 / 1,543,831

Per 30 days:
- Light: 225M input (38M uncached), 3.8M output
- Typical: 969M input (164M uncached), 16.4M output
- Heavy: 2.73B input (464M uncached), 46.3M output

**Cache variants for cloud pricing.** Cloud prompt caches behave differently from vLLM's local prefix cache.
- *As measured:* 83% cached.
- *Each agent session starts cold* (for example, a cloud cache TTL expires between wakes). Add ~8K uncached first-call tokens
  per session; the 5K-10K bucket held 52 requests, consistent with first calls. Uncached input becomes 1.53M (light), 6.55M
  (typical) or 18.4M (heavy) per day, about 80% cached. This assumes 32 / 133 / 364 sessions/day, counting every chat
  question as a cold session.
- *No caching:* all input is billed as uncached.

**Lean sensitivity** (7 calls per event, 20K prompt per call, 3 calls per chat question; output per call unchanged):

| Scenario | Input/day | Uncached input/day | Output/day |
|---|---|---|---|
| Light | 3.8M | 0.65M | 0.10M |
| Typical | 16.5M | 2.8M | 0.42M |
| Heavy | 46.6M | 7.9M | 1.2M |

So the main table is the upper half of a roughly 2x range.

**Optional add-on.** An hourly fleet heartbeat (`BRIEF_EVERY_S=3600`) would add 24 runs/day = 216 calls, about 6.5M input
(1.1M uncached) and 0.11M output per day.

### 2.6 Headroom (ESTIMATE)

- **Demonstrated throughput:** 9.8 LLM calls/min (about 1.1 wakes/min, ~65 wakes/hour), sustained for 10 minutes with up to 4
  concurrent calls. No request ever queued (max waiting 0, mean queue time 0.04 s), KV cache stayed at or below 5% of 3.67M
  tokens, and the one loaded GPU sample read 96% busy.
- **Against one site:**

  | Site | Average load | Assumed peak hour (3x average) | Headroom on average | Headroom at peak |
  |---|---|---|---|---|
  | Light | 0.17 calls/min | 0.5/min | ~57x | ~19x |
  | Typical | 0.74 calls/min | 2.2/min | ~13x | ~4x |
  | Heavy | 2.1 calls/min | 6.3/min | ~4.7x | ~1.6x |

- **Sites per box**, if one box served several sites' agent traffic (not the per-site appliance plan): roughly 4-13 sites' worth
  at the demonstrated rate, depending on whether they are heavy or typical. It would be less if chat replies have latency targets
  or if GR00T commissioning shares the GPU at the same time.
- **Concurrent agent calls:** 4 were measured with no queueing. Aggregate decode rose from ~67 tok/s (1 stream) to ~100-142 tok/s
  (3-4 streams), so each call slows to ~25-35 tok/s at 4-way. KV memory could hold about 120 concurrent 30K-token contexts, so
  compute and memory bandwidth are the limit, not KV memory. Plausibly 6-8 concurrent agent calls fit before per-call latency
  reaches ~3x single-stream; this is untested.
- **At a typical site's average load** (under 1 call/min), calls would mostly run alone at the 66-69 tok/s single-stream rate.
- **Memory headroom:** 30 GiB was still available with everything loaded. vLLM's KV reservation (36.9 GiB) never went above
  5% use, so lowering `gpu_memory_utilization` could plausibly free 20+ GiB for other models (not tested).
- **Unused upside:** this vLLM build runs NVFP4 through the Marlin weight-only path, with no native FP4 compute detected on
  GB10. A native FP4 MoE kernel could raise throughput (not measured).

---

## 3. Caveats

- The sample is small: 249 requests over about 50 minutes of active use. The demo scenarios inject systemic faults, so they do
  not represent steady operations.
- The counters include ~38 requests from before run 2 (12:09-13:49 ET: run 1 and tests) and a few developer-initiated calls.
  All of them are agent-shaped.
- Histogram percentiles are interpolated within buckets. Wake counts come from the sandbox's network log, which I verified
  against `/notifications` for 7 wakes.
- The other session changed the system during my window: tool service restarts at 14:28:03 and 14:39:55, triage switched off,
  and a new sim on port 3001. As a result, the S1 to S2 rate mixes busy and idle minutes.
- FYI for the demo team: `posts_to` was null (`SUPERVISOR_DELIVER_TO` unset) during my window, so autopilot replies were not
  being posted to Discord at that time.

## 4. Method (all read-only)

- vLLM: `curl -s localhost:8000/metrics` at 14:34:05 and 14:43:05 ET, plus `docker logs -t vllm-qwen --since ...` for the
  startup configuration, the access log and the 10-second engine stats.
- Tool service: `curl -s localhost:8090/{health,metrics,autopilot,notifications,tickets,events,events?status=all,trust,commission}`
  at 14:34:47 and 14:43:05 ET. Read `data/test-run-{1,2}/*.json`, `data/clips/` listings, `tools.log` and
  `tools_service.py`.
- Agent: `docker logs -t openshell-default--navfix-... --since ...` for inference calls, tool HTTP calls and hook connections.
- Resources: `docker ps`, `docker stats --no-stream`, `nvidia-smi` (including a 31-second 1 Hz sample), `free -g`,
  `/proc/meminfo`, `/proc/loadavg`, and `/proc/<pid>/environ` of the tool service, filtered to non-secret keys.
