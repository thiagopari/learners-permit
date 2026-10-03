# GB10 Hackathon Plan v2: Fleet and Field Ops Desk

Revised Friday, October 2, 2026, after reading the travel team's `Travel_Ops_Agent_Channel_Assistant.docx`. This replaces the earlier camera-based version of this file. That version cut the travel team's core features (transit routing, live calendar sync, departure and attendance checks) and built a camera system their plan doesn't include, so it was not a fair merge.

Each source document stays the spec for its half: `gb10-hackathon-handoff.md` for the robot side and the travel doc for the field side. This file covers only the merge: the shared decisions, the one contract between the halves, the combined demo, roles, and what to add tonight. Anything marked "Verify" has not been confirmed.

## The short version

The product is a 24/7 ops desk for a company that runs robot packing cells at customer sites around Boston, plus the small field team (sales engineers and field engineers) who travel between those sites. The pitch line: robots in the field need people in the field.

Two agents share one GB10 and one Discord server:

- **Fleet** (robot pair) supervises the cells: work orders, the reliability gate, validation sweeps, refusals with clips. This is the handoff plan, nearly unchanged.
- **Field** (travel pair) runs the field team's day: morning brief, answers, transit and traffic travel times, departure and attendance checks, calendar write-back, re-planning. This is the travel plan, nearly unchanged.

A **service ticket** connects them. When the gate refuses a skill the cell was never commissioned for, Fleet opens a ticket that says an engineer must be on site. Field slots the visit into an engineer's day using its free-slot and transit logic, and books it. Transit delays flow back to the customer as a new ETA. When the engineer taps "arrived", Fleet commissions the skill with a bandit: Thompson sampling splits trials between candidate policies and stops as soon as one is 95% likely to succeed at least 80% of the time. If one is, the gate opens and the refused order ships. Each side's output is the other side's input, and neither can finish the story alone.

Design rule from both documents: code enforces, models explain. Counts, free slots, travel times, the reliability gate and the "engineer on site" rule for commissioning are all computed in code.

## 1. Fairness check

| Travel plan | In the merged plan |
|---|---|
| Morning overview | Kept; adds two fleet status lines |
| Answers in the channel | Kept |
| Current venue awareness | Kept |
| Travel time between events (OpenTripPlanner, MBTA) | Kept; also used to place service visits |
| Live departure check | Kept; ETA changes flow back to the ticket |
| Attendance check | Kept; "arrived" starts commissioning |
| Add, move, cancel with calendar write-back | Kept; also books service visits |
| Automatic re-planning | Kept; also re-plans around tickets |
| Calendar watching (heartbeat) | Kept; doubles as the ticket fallback |
| End-of-day recap | Kept; covers the fleet too |
| Nemotron-3-Super, Parakeet, flights (all optional or extended) | Dropped for memory and time |
| Persona | Generic road warrior becomes a robotics company's sales and field engineers; the seeded demo day mostly stays |

| Robot plan | In the merged plan |
|---|---|
| Work orders mapped to skills, dispatch, clips | Kept |
| Reliability gate in code | Kept, now with a confidence rule instead of a raw rate (section 6) |
| Scheduled sweeps and the reliability table | Kept |
| Refusal with evidence, then escalation | Kept; escalation now books an engineer instead of only tagging one |
| Out-of-distribution gate beat | Kept, and it now resolves: commissioning with the goal-suite policy opens the gate |
| Slack | Discord |
| Isaac Sim stretch | Dropped (it was already a stretch) |

From the earlier version of this file, the camera service, webcam interlock, VLM and Slack are all gone.

## 2. Shared decisions

| Decision | Choice | Why |
|---|---|---|
| Channel | Discord: `#field`, `#cell-globex`, `#cell-acme`, plus DMs | The travel UX (buttons, DMs) is designed for Discord; the robot side doesn't depend on the channel |
| Agents | Two agents in one OpenClaw gateway, one Discord bot each, routed with `bindings` | Each pair owns its agent; smaller toolsets suit a 3B-active local model; judges see two agents coordinate |
| Handoff | Service tickets on the cell service, with `/hooks/agent` webhooks | Deterministic and logged; OpenClaw's agent-to-agent tool is optional (it's off by default) |
| LLM | Qwen3.6-35B-A3B NVFP4 only, served by NemoClaw | Both documents already chose it. Nemotron-3-Super (120B total, 12B active) uses about 108 GB of a Spark's 128 GB on its own |
| Tool services | Both on the host and reached by the sandbox through one preset. External API keys stay in the host-side services | One pattern for both teams, and secrets never enter the sandbox |
| Demo clock | Owned by the field service | OpenClaw cron runs on wall-clock time and can't be fast-forwarded (section 6) |

Fallback if multi-agent config fights NemoClaw by 12:30: one agent with both skill packs. The tool services and tickets don't change, so this fallback is cheap.

## 3. The demo (about four minutes)

| # | Beat | Agent | Led by |
|---|---|---|---|
| 1 | 7:00 morning brief (fast-forwarded): events, travel legs, tightest connection, free slots, weather, plus two fleet lines: "Acme cell: soup-and-sauce 96% over 50 trials. Globex cell: not commissioned for drawer tasks." | Field | Travel |
| 2 | "How many sales pitches today?" and "What's my availability?" | Field | Travel |
| 3 | Globex's ops lead posts a job that needs the drawer skill. Fleet: validated 1 of 10 on this cell's policy, so it refuses with failure clips and opens ticket T-12: "engineer on site required to commission" | Fleet | Robot |
| 4 | Field picks up T-12: "You're in Kendall for the Globex pitch at 2:30. Commissioning fits 3:00–3:45 before Initech at 4:00, a 5-minute walk. [Book] [Other time]". After Book, the calendar updates on screen and Fleet tells `#cell-globex` | Both | Both |
| 5 | Fast-forward to 13:25: the departure check finds an MBTA delay and offers "leave now or taxi". The new ETA flows to the ticket and to Globex's channel | Field | Travel |
| 6 | Fast-forward to 15:00: "Arrived?" then [Arrived]. Fleet starts bandit commissioning between the cell's current policy and the goal-suite policy and posts each batch. Trials shift to the goal-suite policy, and after about 24 trials Fleet is 95% sure its success rate is at least 80%. The gate opens, the job runs and succeeds, and the ticket closes. Field: "Done at 3:41, walk to Initech, you're on time." | Both | Robot |
| 7 | Recap covering the day and the fleet | Both | Both |

Beat 6 is the longest: about 24 trials is three batches at 8 parallel envs. Time one batch during the morning smoke run. If it runs long, talk over the per-batch posts, or trigger "arrived" a minute earlier. One person from each pair presents their half.

## 4. Architecture

```
                         Discord  (#field, #cell-globex, #cell-acme, DMs)
                             |
+----------------------------v------------ GB10 box -----------------------------+
|                                                                                |
|  OpenShell sandbox: OpenClaw gateway                                           |
|     Fleet agent (bot 1)    Field agent (bot 2)  --LLM-->  nemoclaw-vllm :8000  |
|        | curl                 | curl                  ^                        |
|        v                      v                       | POST /hooks/agent      |
|  cell service :8090  <-- tickets -->  field service :8092                      |
|    gate, sweeps, tickets,               calendar, free slots, travel,          |
|    commissioning                        checks, demo clock                     |
|    GR00T :5555 libero_10                OpenTripPlanner :8080 (Java)           |
|    GR00T :5556 libero_goal              MBTA, traffic, weather (from the host) |
|    LIBERO (EGL)                         Radicale or Google Calendar            |
+--------------------------------------------------------------------------------+
```

Memory budget (estimates, measure tomorrow):

| Process | Budget |
|---|---|
| OS, Docker, desktop | ~10 GB |
| Qwen3.6 on vLLM (NemoClaw's Spark recipe already sets `--gpu-memory-utilization 0.4`) | ~48 GB |
| GR00T server with `libero_10` | ~10 GB |
| GR00T server with `libero_goal` | ~10 GB |
| LIBERO envs for sweeps | ~8 GB |
| OpenTripPlanner (set `-Xmx`; Massachusetts graph) | ~6 GB |
| Field service, Radicale, SQLite | ~1 GB |
| Total | ~93 of 128 GB |

## 5. The ticket contract (the only cross-team API)

The cell service (:8090, robot pair) owns tickets in SQLite. Both agents read and update them over HTTP.

States: `open` → `scheduled` → `on_site` → `commissioning` → `done`, with `failed` (the sweep is still below threshold, so escalate) and `cancelled` as exits.

| Endpoint | Called by | Does |
|---|---|---|
| `POST /tickets` `{cell, skill, reason, evidence: {rate, trials, clips}, needed_by}` | Fleet | Opens a ticket and returns its id |
| `GET /tickets?status=&since=` and `GET /tickets/{id}` | Both | Reads tickets |
| `PATCH /tickets/{id}` `{actor, status, assignee, start, end, eta, event_id, note}` | Field for scheduling, Fleet for commissioning | Updates fields; the service rejects illegal state transitions |
| `POST /cells/{cell}/commission` `{ticket_id}` | Fleet | Refuses unless the ticket is `on_site` (the human-on-site rule lives in code). Switches the skill to the task policy and starts a validation job; returns the job id |

Cells carry site data so Field can route to them: `{cell, customer, site, address, lat, lon, discord_channel}`. Use two cells, Globex in Kendall Square and Acme in Back Bay, matching the travel doc's demo day. Both run on the same simulator and policy servers.

On every state change, the cell service wakes the agent that didn't make the change:

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H "Authorization: Bearer $OPENCLAW_HOOK_TOKEN" -H 'Content-Type: application/json' \
  -d '{"agentId": "field", "name": "ticket", "deliver": true, "channel": "discord",
       "to": "channel:<FIELD_CHANNEL_ID>", "timeoutSeconds": 120,
       "message": "TICKET T-12 open | Globex cell, Kendall Square | commission open_middle_drawer | validated 1/10 on the current policy | needed by 17:00 | Follow the Service visit standing order."}'
```

The OpenClaw gateway reaches the host on 18789 through `openshell forward start 18789 <sandbox>`. Hooks need `hooks.enabled`, a dedicated `hooks.token`, and `hooks.allowedAgentIds: ["fleet", "field"]` (Verify that NemoClaw lets you set these in the sandbox). If the webhook path fails, both agents poll `GET /tickets?since=` from their heartbeats. The travel plan already has a 5-minute heartbeat; set it to 1 minute for the demo.

## 6. Changes to each half

### Robot pair (cell service and Fleet), on top of the handoff

| Change | Detail |
|---|---|
| Two policy servers | `libero_10` on :5555 and `libero_goal` on :5556, both started at boot, so commissioning is a routing switch rather than a slow model load |
| Skill table | Add a `policy` field to each skill. `open_middle_drawer` starts on `libero_10`, where it is out of distribution; commissioning moves it to `libero_goal`, the suite it belongs to |
| Tickets and commissioning | The endpoints in section 5, plus the webhooks |
| Bandit commissioning | `POST /cells/{cell}/commission` runs the algorithm below instead of a fixed sweep, and every gate check uses its confidence rule |
| Fleet standing orders | Order handling (handoff section 6). Commissioning: open a ticket on refusal, run the commissioning sweep on `on_site`, open the gate only through the service, then dispatch the waiting job |
| Dropped | The Isaac Sim stretch, plus everything camera-related from the previous version of this file |

### Bandit commissioning (robot pair)

Commissioning is a small bandit problem. A skill has a few candidate policies (the cell's current `libero_10` policy and the goal-suite `libero_goal` policy). Each trial is one LIBERO episode that succeeds or fails. The question is whether any candidate clears the bar, answered with as few simulator trials as possible. This replaces the fixed-size sweep.

| Piece | Rule |
|---|---|
| Belief per policy | Beta(1 + successes, 1 + failures), starting from a uniform prior |
| Which policy runs next | Thompson sampling: for each slot in a batch of parallel episodes, draw once from every policy's posterior and run the policy with the highest draw |
| Pass | The best policy has P(success rate ≥ 0.8) ≥ 0.95. Deploy it and open the gate |
| Fail | Every policy has P(success rate ≥ 0.8) ≤ 0.05. Keep the gate closed and escalate with clips |
| Cap | 40 trials, then report "inconclusive" with the counts |

The same confidence rule replaces the raw-rate threshold in every gate check, including `/run`, so the gate never opens on a lucky streak:

| Result so far | P(true rate ≥ 0.8) |
|---|---|
| 9 of 10 | 0.68 |
| 10 of 10 | 0.91 |
| 13 of 13 | 0.96 (the shortest all-success streak that passes) |
| 19 of 20 | 0.94 |
| 45 of 50 | 0.96 |

Simulated tonight with the code below (4,000 runs per case, batches of 4). With the drawer task at about 5% on `libero_10` and 95% on `libero_goal`, commissioning picks `libero_goal` in 90% of runs and uses about 24 trials on average, against 40 for a fixed 20-trial sweep of each policy; the other runs hit the cap. With no good policy (5% and 40%), it fails in about 8 trials. A policy just above the bar (85%) usually ends inconclusive and is sometimes rejected, so the rule errs toward keeping the gate closed, which is the safe direction.

```python
# Standard library only, so it runs in /opt/toolsvc without numpy or scipy
import random
from math import comb

def p_at_least(s, f, thr=0.8):
    """P(true rate >= thr) under a Beta(1+s, 1+f) posterior, which equals P(Binomial(s+f+1, thr) <= s)."""
    n = s + f + 1
    return sum(comb(n, k) * thr**k * (1 - thr) ** (n - k) for k in range(s + 1))

def commission(arms, run_batch, thr=0.8, conf=0.95, batch=4, max_trials=40):
    """arms: candidate policy ids. run_batch({arm: n_episodes}) -> {arm: [1, 0, ...]}, run in parallel."""
    s, f = dict.fromkeys(arms, 0), dict.fromkeys(arms, 0)
    while sum(s.values()) + sum(f.values()) < max_trials:
        picks = [max(arms, key=lambda a: random.betavariate(1 + s[a], 1 + f[a])) for _ in range(batch)]
        for arm, outcomes in run_batch({a: picks.count(a) for a in set(picks)}).items():
            s[arm] += sum(outcomes)
            f[arm] += len(outcomes) - sum(outcomes)
        best = max(arms, key=lambda a: p_at_least(s[a], f[a], thr))
        if p_at_least(s[best], f[best], thr) >= conf:
            return {"decision": "pass", "policy": best, "successes": s, "failures": f}
        if all(p_at_least(s[a], f[a], thr) <= 1 - conf for a in arms):
            return {"decision": "fail", "successes": s, "failures": f}
    return {"decision": "inconclusive", "successes": s, "failures": f}
```

Set `batch` to the number of parallel envs. Post one line per batch (for example "libero_goal 7/7, libero_10 0/1, P(≥80%) = 0.79"), so the wait in beat 6 shows the algorithm working. On a resume this is a multi-armed bandit (Thompson sampling), not reinforcement learning; the RL follow-up is RLinf's PPO fine-tuning of GR00T after the event.

### Travel pair (field service and Field), on top of the travel doc

| Change | Detail |
|---|---|
| Service visits | A new event type, `service_visit`, carrying the ticket id. Booking uses the existing find-free-slots and travel tools |
| Fleet status | A `get_fleet_status(site)` tool that calls the cell service's `/reliability` and `/tickets`, used in the brief and in departure checks for visits ("bring the drawer fixture kit") |
| Service visit standing order | On a ticket: pick the engineer and slot, propose with buttons, and on confirmation create the event and `PATCH` the ticket to `scheduled`. Push ETA changes to the ticket. "Arrived" sets `on_site` |
| Demo clock | The field service owns `GET /clock` and `POST /clock/advance`, and fires due checks through `/hooks/agent`. One-shot cron jobs stay for real-time use |
| Trims to make room (about an hour) | Live traffic API (use OSRM with a congestion factor, or one injected taxi scenario), OwnTracks, Nemotron-3-Super, Parakeet |

## 7. Notes on the travel doc (tell the travel pair tonight)

| Item in their doc | Issue | Fix |
|---|---|---|
| Simulated clock plus one-shot cron checks | OpenClaw cron fires on wall-clock time, so fast-forwarding won't trigger the jobs | Let the field service own the clock and fire checks through `/hooks/agent` |
| Nemotron-3-Super (optional) | About 108 GB of 128 GB on a Spark by itself | Drop it |
| Risk: buttons may not work through the Discord connector | OpenClaw supports Discord components v2 (buttons, selects), and clicks come back to the agent as messages | Use buttons and keep text replies as a fallback (Verify in NemoClaw's bundled OpenClaw version) |
| OpenTripPlanner on the box | It's a Java app, the box likely has no JDK, and the graph must be built with the same OTP version that serves it | Stage an arm64 container (an `eclipse-temurin:21-jre` base plus the OTP jar) and the prebuilt graph on the SSD |
| Tool service on the host | NemoClaw rejects private and loopback destinations by default | Use the preset below with `--trusted-private-host`, the same as the cell service |
| External APIs called from the sandbox | Every host needs its own preset, and the keys would live in the sandbox | Call them from the host-side field service, so the sandbox only reaches the two local services |

```yaml
# presets/opsdesk-tools.yaml   (Verify the curl path inside the sandbox with `which curl`)
preset:
  name: opsdesk-tools
  description: "Cell and field services on the host"
network_policies:
  opsdesk-tools:
    name: opsdesk-tools
    endpoints:
      - host: 172.17.0.1
        port: 8090
        protocol: rest
        enforcement: enforce
        rules:
          - allow: { method: GET, path: "/**" }
          - allow: { method: POST, path: "/**" }
          - allow: { method: PATCH, path: "/**" }
      - host: 172.17.0.1
        port: 8092
        protocol: rest
        enforcement: enforce
        rules:
          - allow: { method: GET, path: "/**" }
          - allow: { method: POST, path: "/**" }
          - allow: { method: PATCH, path: "/**" }
    binaries:
      - { path: /usr/bin/curl }
```

```bash
nemoclaw <sandbox> policy add --from-file presets/opsdesk-tools.yaml --trusted-private-host 172.17.0.1 --dry-run
nemoclaw <sandbox> policy add --from-file presets/opsdesk-tools.yaml --trusted-private-host 172.17.0.1 --yes
```

Bind both services to the address the OpenShell gateway reaches (the docker0 IP is a first guess) rather than 0.0.0.0, so they aren't open to the venue Wi-Fi.

## 8. Roles and schedule

| Role | Who | Owns |
|---|---|---|
| Shared setup and Field agent | Travel pair, person 1 | NemoClaw onboarding, Discord (both bots), the Field workspace and standing orders, the demo clock (the travel doc already planned the box setup) |
| Field service | Travel pair, person 2 | Calendar, OpenTripPlanner, MBTA and weather tools, service visits, ticket handling |
| Policy and sweeps | Robot pair, person 1 | Both GR00T servers, LIBERO, sweeps, timing the commissioning sweep (handoff role B) |
| Cell service and Fleet agent | Robot pair, person 2 | Gate, tickets, commissioning, webhooks, the Fleet workspace and standing orders (handoff roles A and C on the fleet side) |

| Time | Milestone |
|---|---|
| 09:00–10:30 | Brief; copy and load from the SSD if allowed |
| 10:30–11:15 | Travel pair: NemoClaw, Qwen3.6 and Discord up (per their plan). Robot pair: GPU checks, both GR00T servers, smoke rollout |
| 11:15–12:30 | Each agent answers in its own channel against mock tools; ticket endpoints live in mock mode |
| 12:30 | Checkpoint 1: Fleet opens a mock ticket, and Field receives it and proposes a slot. Decide now between two agents and the one-agent fallback |
| 12:30–15:00 | Each half follows its own document's timeline |
| 15:00 | Checkpoint 2: the full ticket loop with real calendar write-back and a real commissioning sweep |
| 15:00–16:45 | Demo clock and seed data, message polish, full sweeps so the reliability table is populated |
| 16:45–17:30 | Two rehearsals; record the backup video |
| 17:30–17:45 | Submit (code freeze at 18:00) |

Either half can carry a demo alone if the other breaks. If GR00T won't run, the cell service's mock mode keeps the ticket loop intact. If routing or the calendar fails, the robot half still has its original three beats.

## 9. Tonight, on top of each document

Robot pair:
1. Stage the goal-suite checkpoint too (about 7 GB): `hf download nvidia/GR00T-N1.7-LIBERO --include "libero_goal/*" --local-dir /mnt/hack/ckpt/GR00T-N1.7-LIBERO`
2. Add tickets, bandit commissioning (section 6) and webhooks to the cell service in mock mode.
3. Skip the Isaac Sim stretch and all camera prep from the previous version of this file.

Travel pair:
4. Create a second Discord bot (Fleet), invite both bots, create the three channels, and note the channel IDs.
5. Build the OpenTripPlanner graph and its arm64 container. Seed the demo day with Globex (Kendall) and Acme (Back Bay) as robot customers.
6. Build the service-visit flow against a mock of section 5.

Everyone:
7. Agree on the ticket JSON in section 5 tonight. It's the only thing the two pairs must not change on their own tomorrow.
8. Thiago's laptop has about 37 GB free where Docker stores images, against the handoff's 150–200 GB budget. Prune first, or build the arm64 images on an Apple Silicon Mac, which builds them natively.

## 10. Pitch

| Part | What to say |
|---|---|
| Problem | Robot companies keep cells running at customer sites with a small field team. When a cell can't do a job safely, someone has to get there at the right time with the right evidence. Today a dispatcher stitches that together from a robot dashboard, a calendar and the MBTA app |
| Demo | The seven beats |
| Why local | Two kinds of sensitive data on one box: customers' operations data and robot footage, and where the team is all day. No model call leaves the box |
| Design | Code enforces, models explain |
| Roadmap | Logged failures become post-training data; commissioning becomes over-the-air policy rollout gated by validation; real fleet and calendar integrations |

## 11. Open questions

| Question | How to check |
|---|---|
| Do multi-agent config and two Discord bot accounts work inside NemoClaw's sandbox? | Checkpoint 1 |
| Can hooks (including `allowedAgentIds`) be enabled under NemoClaw, and is 18789 forwarded? | The `/hooks/wake` test from the host |
| Do Discord buttons work in NemoClaw's bundled OpenClaw version? | One test message |
| Does the drawer task score low on `libero_10` and high on `libero_goal`? | Morning sweeps. The goal suite reports 97.5% overall; per-task rates aren't published |
| How long does a commissioning run take (about 24 trials)? | Time one batch during the smoke run |
| How much heap does OpenTripPlanner need for the Massachusetts graph? | Tonight's graph build |

## 12. Sources

| Topic | Link |
|---|---|
| OpenClaw multi-agent routing and agent-to-agent | `~/.npm-global/lib/node_modules/openclaw/docs/concepts/multi-agent.md`, https://docs.openclaw.ai |
| OpenClaw webhooks and cron | `docs/automation/cron-jobs.md` in the same folder |
| OpenClaw Discord components | `docs/channels/discord.md` in the same folder |
| GR00T LIBERO suites and task lists | https://github.com/NVIDIA/Isaac-GR00T/blob/main/examples/LIBERO/README.md |
| GR00T N1.7 LIBERO checkpoints (`libero_10`, `libero_goal`, `libero_object`, `libero_spatial`) | https://huggingface.co/nvidia/GR00T-N1.7-LIBERO |
| Nemotron 3 Super on DGX Spark | https://ai-muninn.com/en/blog/dgx-spark-nemotron-120b-vllm |
| Thompson sampling (Russo et al., tutorial) | https://arxiv.org/abs/1707.02038 |
| NemoClaw custom presets and private hosts | https://docs.nvidia.com/nemoclaw/user-guide/openclaw/network-policy/configure-policies/create-custom-policy-presets |
| NemoClaw dashboard forward on 18789 | https://www.akamai.com/cloud/marketplace-docs/guides/nemoclaw |
