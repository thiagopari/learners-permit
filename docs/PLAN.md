# Nebius × NVIDIA Global AI Hackathon: Project Plan

Researched 2026-10-04. **Submission deadline: Fri Oct 30, 2026, 10:00 AM PT** (26 days left).

## The pick: **Learner's Permit** (Hyperion + GR00T, one stack), Physical AI track
**Pitch:** *"A Nemotron agent may command a GR00T skill only after Nebius-run trials prove it, only within the conditions tested, and loses the licence the moment live results slip."*
**Angle vs. the field:** *"Other robot agents ask when they're unsure; ours asks when it's unproven."* The rules bar third-party trademarks in submissions, so don't name Gemini in the video. Cite it in the README only.

**Red-team judges** (Nebius ML PM, NVIDIA robotics DevRel, Tavily engineer), scored out of 60:
- **Merged: 48.**
- Hyperion-only: 29 ("an endpoint swap").
- GR00T-only: 25 ("a training run, not a product").
- **Judges may score "solely on the text description, images, and video"**, so the video is the product.

**Track:** Physical AI. Its text asks for robotics "powered by Nemotron, GROOT, Cosmos and Sonic models and coordinated through an agent runtime", which is this architecture word for word. Physical AI also doesn't require a live demo URL. Sim-only is allowed; **label sim footage as simulation**.

**Novelty, honestly stated:**
- **Already exists:** evidence-gated autonomy in general ("EntropyRuntime", with five "gears" of autonomy, [arXiv 2607.00334](https://arxiv.org/abs/2607.00334)); typed authority layers (Edge Skillguard, [2608.25091](https://arxiv.org/abs/2608.25091)); OWASP LLM06 "complete mediation"; SayCan, KnowNo, RoboGuard; and Gemini Robotics-ER 2 asking humans for help.
- **Apparently unclaimed:** *per-skill, per-scope licences issued from a Bayesian success posterior and enforced where the LLM calls the VLA*:
  - A licence covers only the colours, phrasings, payloads and speeds that were tested.
  - Licences are **tiered:** 80% for supervised use, 99% for unattended use. The 99% tier takes **298 straight successes**, which is the honest reason for Nebius-scale evals.
  - **Drift revokes** a licence.
  - **Web results can only narrow** a licence, never widen it.

**Fix the gate before trusting it.** The red team simulated it as configured (checks every 4 trials, cap 40):
- A truly 90% policy gets licensed only **56%** of the time, and an 85% one only 23%.
- **Raise the cap to 100:** a 90% policy is then licensed about 92% of the time, and false licences at exactly 80% rise from about 8% to about 14% (exact calculation: 92.2%, 7.9% → 14.4%). Show this trade-off in the README.
- The 99% "unattended" tier needs about 298 straight successes, so it needs a cap of **at least 300**. That's what Nebius-scale evals are for.

**Must-ship** (wins on all 4 criteria **without any fine-tuning**). Freeze this by **Oct 11**:
1. Zero-shot N1.7 evals on Nebius on two RoboLab tasks.
   - One gets **licensed** ("put the bananas in the bin": NVIDIA's README shows 38/40, so P ≈ 0.99 if your run matches).
   - One gets **refused** ("put the red dishes in the bin": README 15/40, so ≈ 0).
   - **Re-measure both yourselves, and quote your numbers, not NVIDIA's.**
   - The Cedar `object_class` list must match the scene: banana/dish for the must-ship RoboLab scene, housing/lid for the custom sorting scene (stretch).
2. Enforced `POST /run` + Cedar. **The role comes from the session, never the LLM.**
3. A Nemotron planner restricted to catalogue skills.
4. A **Tavily datasheet check that can only block, never allow.** The 2.4 kg must come from `extract`, not the LLM.
5. **Live revocation:** perturb the scene and the licence drops.
6. A console with licence cards (posterior, confidence interval, clips, cost per 1,000 episodes), approvals and an audit log.
7. **A 4-beat video: refuse → earn → block → revoke.**

**Stretch:** the fine-tune earns the colour licence · a real-arm clip · a phrasing heatmap · recall and fault-code flows.
**Cut:** navbot, Discord, Hermes Agent, purely to keep the scope small. The teammates have agreed to open-source their code.

Both ideas fit without compromise, because each supplies what the other is missing:
- The **GR00T project** has a skill, but nothing decides when that skill is safe to hand to an AI.
- **Hyperion** has that decision (a Bayesian trust gate), but the audit showed **nothing enforces it**, and it has no skill to gate.

| Layer | What | Owner idea | Runs on |
|---|---|---|---|
| **Skill** | GR00T N1.7-DROID post-trained for language-conditioned part sorting in Isaac Sim (Franka) | GR00T project | Nebius AI Cloud (H100/RTX PRO 6000 training) |
| **Proof** | Hyperion's Thompson-sampling commissioning sweep: a skill or phrasing is "licensed" only when P(success ≥ 0.8) ≥ 0.95 | Hyperion | Nebius RTX PRO 6000 VMs (uk-south2) or Serverless L40S jobs (both have RT cores) |
| **Permission** | RBAC at ONE `POST /run` choke point: role × skill × part class × bin × speed. The AI agent role may only call *licensed* skills; anything else escalates to a human approver | Both | Tool service |
| **Brain** | **Nemotron** (Token Factory) planner turns orders into catalog skill calls. Hyperion's loop handles exceptions: detect → investigate (**Tavily**) → decide → verify → summarize | GR00T project's "brain" + Hyperion | Nebius Token Factory |

**Why it scores on all 4 criteria (25% each):**
- **Technical implementation:** real post-training plus a statistically sound evaluation at scale on Nebius, and two NVIDIA open models (GR00T, Nemotron).
- **Design:** one choke point, and the requester's identity never passes through the LLM.
- **Impact:** Gartner expects over 40% of agentic AI projects to be canceled by the end of 2027, citing costs, unclear value **or inadequate risk controls**. We go after the risk-control part.
- **Idea:** "skills are permissions you earn with evidence".

**The video: 4 beats, under 3:00.** The red team found 7 beats was "a feature tour".
1. **Refuse (0:00–0:45):**
   - The order: "Put the red dishes in the bin." Nemotron plans the catalogue skill, then `/run`, then Cedar.
   - The role is fine, but the skill is **unlicensed**. Your own zero-shot sweep on Nebius gives a posterior near 0 (NVIDIA's README reports about 15/40 for this task; quote your measurement). Result: **REFUSED** and escalated.
   - For contrast, "put the bananas in the bin" (about 38/40 → P ≈ 0.99) is licensed and runs.
   - **Stretch version:** the same beat on your custom "red housings to bin A" scene, with its own measured baseline.
2. **Earn (0:45–1:30):**
   - A commissioning sweep on Nebius RTX PRO 6000s: the fine-tuned policy (stretch), or a narrower scope that passes.
   - The licence card's posterior crosses 0.95 live, with the confidence interval, clips and cost per 1,000 episodes.
   - A licence is issued **with its scope** (the colours and phrasings tested).
3. **Block (1:30–2:10):**
   - An unknown part number appears. Tavily `extract` pulls the datasheet: **2.4 kg against a 2.0 kg limit**, so the pick is blocked.
   - A ticket opens with the source URL. Web results can only narrow a licence.
4. **Revoke (2:10–2:45):**
   - Perturb the scene (new distractor, lighting). Live success slips and the **licence is revoked**, so the agent goes back to asking a human.
   - Close: *"Other robot agents ask when they're unsure; ours asks when it's unproven."*
- Add a real-arm clip if you have one, and **label sim footage as simulation.**

**Gate math (verified Oct 4 by reproducing the red team's simulation):**
- 38/40 → P(rate ≥ 0.8) = 0.993; 15/40 → about 2×10⁻⁹.
- Straight successes: 13/13 → 0.956 if you check after every trial. **With batches of 4, the first pass is at 16/16 (0.977)**, because 12/12 gives only 0.945.
- The 99% tier needs 298 straight successes: P(rate ≥ 0.99) = 0.9505 (297 gives 0.9500, just short).
- Chance of licensing at cap 40 vs **cap 100**:

| True success rate | Cap 40 | Cap 100 |
|---|---|---|
| 80% | 7.5% | 14% |
| 85% | 23% | 49% |
| 90% | 56% | **92%** |
| 95% | 91% | 100% |

## Event facts (confirmed)
- **The Boston "Builders & Brews: Hack Edition" already happened** on Fri Oct 2 at Jaho Coffee in Central Square ([luma.com/emee7xtr](https://luma.com/emee7xtr)). It was a meetup with workshops and credits; nothing gets submitted or pitched there.
- **The real competition:** [nebiusglobalaihackathon.devpost.com](https://nebiusglobalaihackathon.devpost.com/). It's online, with 17,533 participants so far. Submissions are open Aug 26–Oct 30, judging runs Dec 1–15, and winners are announced around Jan 11, 2027.
- **Tracks:** Coding & Agentic Engineering · Best Apps & Agents · Personal AI · **Physical AI** (ours).
- **Must:**
  - Use at least one **NVIDIA open model** (Nemotron, GR00T, Cosmos, Sonic).
  - **Run on Nebius:** Token Factory calls at runtime, or AI Cloud (Serverless Jobs/Endpoints, DevPods).
  - Ship a **public repo** with an OSS license (Apache 2.0, MIT, MPL 2.0).
  - Make a **public YouTube video under 3 min**.
  - Write a README.
  - Add a prior-work note.
- **Prior work** is allowed if significantly updated after Aug 26, with a written explanation. Hyperion was built Oct 3, so it falls inside the window.
- **Judging:** first a pass/fail viability check, then **4 criteria at 25% each:** Technological Implementation, Design, Potential Impact, Quality of the Idea.
- **Prizes** (one Overall or Track award per project, plus one Bonus):
  - Overall: $20k / $10k / $6k.
  - Track winners: a Jetson Orin Nano.
  - Bonus: **Best Use of Tavily, $3k**.
  - **City Winner: $500 × 20.** The Official Rules limit it to entrants who attended a listed Builders & Brews event, and Boston is on the list (re-checked Oct 5). Our teammate attended, so pick Boston on the form.
  - **City, Tavily and Feedback are all Bonus Awards, and a project can win only one**, so aim for **Tavily ($3k)** over City ($500).
  - Feedback prize: $100.
- **Team size:** no maximum; solo is allowed.
- **A teammate attended the Oct 2 Boston event** (confirmed Oct 4). So the team has the attendee credits ($100 AI Cloud + $100 Token Factory) and should pick **Boston** on the submission form.

## What Hyperion actually has (code audit, Oct 4)
- **Real:**
  - GR00T N1.7 inference on NVIDIA's published LIBERO checkpoints (no training).
  - MuJoCo test episodes with video clips.
  - A **Thompson-sampling commissioning sweep** (`cell/bandit.py`): batches of 4, up to 40 trials. A skill passes when P(success ≥ 0.8) ≥ 0.95, and the result lands in `data/trust.json`.
- **Not real:**
  - **Nothing reads `trusted`.** The gate is enforced only by the agent prompt.
  - There's no `/run` or `/skills` endpoint (the handoff doc specified them).
  - The GR00T arm isn't connected to the fleet simulator.
  - The "skill refused / gate open" Discord cards came from `mock_supervisor.py`.
  - The tool service has no authentication, and the agent can claim to be "human" in ticket transitions.
- **RBAC-like pieces that exist:**
  - The sandbox network allowlist (method and path only).
  - The legal ticket state machine (`TICKET_FLOW`).
  - Discord `ROLE_APPROVER` on reactions.
- **The seam for the merged project:**
  - One new `POST /run` choke point: `authorize(role, skill, args)` → check `trusted` → run on `TRUST[skill]["policy"]`.
  - A new GR00T runner following the existing `run_batch({arm: n}) → {arm: [0/1]}` contract, so the bandit needs **no changes**.
  - Orders come in through navbot, then glue, then `POST /orders` (which stores the requester's **role**). The Nemotron planner can only call skills in `CATALOG`, and identity never passes through the LLM.
- **Effort:**
  - Port as-is to Nebius + Tavily: about **4 person-days**.
  - Merged project: about **20** (16–26), of which the GR00T sorting skill is 7–10.
  - **1-day fallback:** NVIDIA's `libero_object` checkpoint ("pick up X and place it in the basket") through the existing runner.
- **Owners (all agreed on Oct 4 to open-source their code):** Megha (navbot, dashboard), Amal (dashboard UI), "Ferbin (integration)" (`sim/`, `glue/`, `isaac/`, `docker/`).
- **GB10-only (needs replacing):** `infra/*` arm64 builds, the offline checkpoint fixes, the vLLM/Qwen config, the NemoClaw sandbox gateway, and hard-coded `/home/dell` paths.

## GR00T sorting feasibility ([V] = verified, [E] = estimate)
- **Model [V]:**
  - **GR00T N1.7** is the latest release: 3B parameters, a Cosmos-Reason2-2B backbone, relative end-effector actions ([repo](https://github.com/NVIDIA/Isaac-GR00T)).
  - Fine-tune with `launch_finetune.py` on LeRobot v2 data plus `modality.json`. The default keeps the backbone frozen and trains the projector + action head, under ~35 GB per GPU.
  - N1.7 has **no LoRA**.
  - Use the **DROID (Franka)** embodiment tag; SO-100 and GR1 would need a new embodiment trained from scratch.
- **The baseline that makes the story [V]:** NVIDIA's RoboLab runs N1.7-DROID zero-shot in Isaac Sim.
  - **BananasInBin (RoboLab task `BananasInBinThreeTotalTask`): 38/40.**
  - **RedDishesInBin (`RedDishesInBinTask`): 15/40.**
  - **Careful with the framing:** the same README reports **8.58% overall** (412/4,800 episodes). RedDishesInBin is actually one of only 13 tasks with any success, so "colour is where it breaks" won't survive NVIDIA judges.
  - **The honest claim:** zero-shot reliability **varies wildly from task to task** (95% vs 37.5% vs mostly 0%), and that's exactly why per-skill licences are needed. ([RoboLab](https://github.com/NVIDIA/Isaac-GR00T/blob/main/examples/RoboLab/README.md))
  - Measure your own scene's baseline in Tier 1; never quote 15/40 as your scene's number.
- **Data [E]:** a scripted state-machine expert (modelled on Isaac Lab's `lift_cube_sm.py`) reading object poses from the sim. It generates 500–1,000 demos across 3–4 colours with no teleop; new phrasings cost nothing.
  - **Reference [V]:** Isaac Lab Mimic turns about 10 demos into 1,000, in about 4 h for Franka stacking.
  - **Skip [E]:** GR00T-Dreams/Cosmos world models are beyond a $200 budget.
- **GPUs [V]:**
  - **Isaac Sim needs RT cores; H100/A100 can't render.**
  - Nebius L40S: $1.55/h ($0.74 spot). RTX PRO 6000: $1.80/h ($0.95 spot, checked Oct 5). H100: $4.50/h since Oct 1, for training only ([prices](https://nebius.com/prices)).
- **Eval cost [E]:** about **$6–14 per 1,000 episodes**; measure the real figure in Tier 1.
  - **Report every success rate with a confidence interval.** Arena's own numbers show why: 0.88 on 17 episodes became 0.605 on 200. Hyperion's Bayesian gate is built for exactly this.
- **Known bug to avoid [V]:** with `n_envs>1`, `rollout_policy.py` keeps the first episodes to finish, which inflates success rates. Use one env per run, or fix the bug.
- **Tiered plan:**

| Tier | When | Cost | What |
|---|---|---|---|
| 0 | Days 1–2 | ~$5 | Run RoboLab + N1.7-DROID **on a Nebius RTX PRO 6000 VM**, not the laptop. The laptop's RTX PRO 2000 has 8 GB; GR00T and Isaac Sim each need 16 GB+, and RoboLab's TiledCamera hangs on laptop Blackwell GPUs. Reproduce both baselines. |
| 1 | Week 1 | ≤$10 | One sorting scene: 3 coloured parts, 2 bins. Zero-shot eval over 10 phrasings, with held-out colours. |
| 2 | Week 2 | ~$40 | 500–1,000 scripted demos (DROID format). Fine-tune 5–10K steps on 1× RTX PRO 6000, about 3–6 h per run. |
| 3 | Week 3 | ~$40–60 | Several thousand eval episodes on spot RTX PRO 6000 VMs (uk-south2) or Serverless L40S jobs. L40S quota is only 2, and its "spot" price is flat-rate. Keep a reserve. |

- **Demo-able even if training underperforms:**
  - Zero-shot vs fine-tuned clips.
  - A success and wrong-bin heatmap by phrasing.
  - Cost per 1,000 episodes.
  - **The trust gate refusing a weak policy.**
- **Risks:**
  - Version split: RoboLab uses Python 3.11 and GR00T uses 3.12, so run the policy server and sim client separately.
  - The data must match DROID's format exactly.
  - Scripted demos may be too clean.
  - Spot instances can be preempted.

## Track rules that shape the project (verbatim from the [rules](https://nebiusglobalaihackathon.devpost.com/rules))
- **Physical AI:** "Build embodied and edge agents that sense and act in the real world: robotics, IoT, and on-device intelligence."
- **Video:** "must include at least a 1-minute clip showing the physical hardware/robot actually operating, **or — if your Project has no physical hardware component — the key application modules in action.**"
  - So a simulation-only project is *allowed*, but **real hardware footage is a big edge** in a "real world" track.
  - Cheapest credible route: GR00T N1.7-**DROID** was trained on real Franka data. **An hour on a lab Franka** (ask Northeastern robotics labs) could produce a real clip of the same skill.
  - Plan B: a real webcam watching a real tray of coloured parts, with the verify step running on it.
- **Demo URL:** "not required for Physical AI submissions".
- **Tavily bonus ($3k, one winner, stacks with a track or overall prize):** the only stated criterion is "a functional, runtime call to the Tavily API". **Three Tavily staff are judges.**

## Sponsor angles
- **Tavily** ([docs](https://docs.tavily.com/llms.txt)): search, extract, crawl, map and research endpoints, plus an MCP server (`https://mcp.tavily.com/mcp/`).
  - 1,000 free credits a month; **free for students**.
  - **Make a Tavily result gate a robot decision**, log the source URL, and show it in the video:
    1. **Part → datasheet:** search the manufacturer's site, then extract the ratings (mass, temperature, ESD) and compare them to the skill's limits *before* the planner can command a pick.
    2. **Recall/safety bulletin:** news search over the installed parts list. A hit **parks the robot** and opens a ticket.
    3. **Fault code → fix:** crawl the vendor manual, then a research call with a structured output (cause, fix, source_url) attached to the ticket.
- **Nous Research:**
  - Hermes 4.3 (Apache-2.0) **isn't an NVIDIA model**, so it doesn't satisfy the model rule; keep Nemotron as the planner.
  - Optional nod to Nous: **Hermes Agent** (MIT) as the agent runtime. It supports MCP (for Tavily) and has a guide for running Nemotron 3 Ultra. Wiring it to Token Factory is unverified.
  - Skip Atropos: it was archived in Jul 2026.

## Nebius setup (checked Oct 4)
- **One GPU type for everything: RTX PRO 6000.** It has RT cores for Isaac Sim and 96 GB for GR00T fine-tuning (which needs 40 GB+).
  - Price: $1.80/h on demand, **$0.95/h spot** (Nebius pricing page, checked Oct 5). $100 buys about 55 h on demand or
    105 h spot, less the disk: $0.071 per GiB-month whether the VM runs or not (150 GiB is about $10.65 a month).
  - Only the L40S ($1.55/h) and RTX PRO 6000 have RT cores. **H100/H200/B200/B300 can't render Isaac Sim.**
  - H100 went from $3.85 to $4.50/h on Oct 1.
- **Region and quota trap:** new accounts get **0 RTX PRO 6000 quota in us-central1**, but 32 in **uk-south2 / eu-south1**; L40S quota is 2 in eu-north1. **Launch in uk-south2 or eu-south1,** and request quota on day 1.
- **Spot instances** get a SIGTERM 60 s before stopping and don't auto-restart, so checkpoint fine-tunes often.
- **Use Nebius's own [Physical AI Workbench](https://github.com/nebius/nebius-physical-ai):**
  - Open source, with Isaac Sim/Lab, GR00T and Cosmos images, run with SkyPilot on Managed Kubernetes (free control plane). It saves setup and shows "effective use of Nebius".
  - It has an Isaac Lab quadruped guide.
  - **Serverless Jobs** (which the rules name as a valid Nebius runtime) work on L40S. Whether RTX PRO 6000 is offered there is unclear, because Nebius's docs conflict. Use VMs or Kubernetes for RTX PRO 6000.
- **Token Factory** (`https://api.tokenfactory.nebius.com/v1/`, OpenAI-compatible; function calling on all the models below). Price per 1M tokens, in/out:

| Model | In | Out |
|---|---|---|
| Nemotron-3-Nano-30B | $0.06 | $0.24 |
| Nemotron-3.5-Lightning | $0.06 | $0.24 |
| **Nemotron-3-Super-120B** | $0.30 | $0.90 |
| Nemotron-3-Ultra-550B | $1 | $3 |
| Hermes-4-405B | $1 | $3 |

  - So $100 is effectively unlimited for a planner.
  - Token Factory fine-tuning doesn't cover Nemotron, so planner tuning is out of scope.
- **Credit gotchas:**
  - AI Cloud: add a card (a $25 top-up goes into your balance), then Billing → Apply promo code. **Set a budget alert**; the card auto-charges if the balance goes negative.
  - Token Factory promo codes are applied separately (Top up → promo).

## Potential Impact: the numbers (for the README and video)
- **The gap:** published vision-language-action (VLA) robot policies on sorting and kitting land at roughly **75–95%** in lab or vendor settings, versus about **99.9%** claimed for production picking.
  - Gemini Robotics 2: pick-and-place **74.2%**, tool kitting **78.9%** ([DeepMind](https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/)).
  - Figure Helix: 94.4% barcode success, vendor figure ([Figure](https://www.figure.ai/news/scaling-helix-logistics)).
- **Why supervision matters:** Dyna's *illustrative* math (labelled "not measured", for laundry folding) says 95% per step over about 79 steps means **only 1.7% of cycles finish clean**, or about 190 interventions per 24 h ([Dyna](https://www.dyna.co/dyna-2.1)). Someone has to decide which skills to trust and when to call a human. That's this project.
- **Cost of getting it wrong:** *unplanned* downtime runs **over $2M/hour in automotive** and $39K/hour in consumer goods (2021–22 data). An average large plant has about 25 h of downtime a month ([Siemens](https://assets.new.siemens.com/siemens/assets/api/uuid:3d606495-dbe0-43e4-80b1-d04e27ada920/dics-b10153-00-7600truecostofdowntime2022-144.pdf)).
- **The industry is converging on this design:** Gemini Robotics-ER 2 orchestrates VLAs as tools, halts near humans, and asks humans when unsure ([Google](https://blog.google/innovation-and-ai/models-and-research/google-deepmind/gemini-robotics-er-2/)). Formant and InOrbit ship ops copilots.
  - **Our difference:** permissions are *earned through measured evaluation* and enforced in code, on open models.
- *Caveat:* several of these are vendor numbers; label them as such on slides.

## Schedule (Oct 5 → submit Thu Oct 29, a day of buffer)
Workstreams:
- **SKILL:** Thiago + the GR00T friend.
- **GATE/RBAC:** the Hyperion friend.
- **BRAIN/TAVILY:** the 4th teammate, or shared.
- **SHIP:** everyone in week 4.

| Week | Goal | Done when |
|---|---|---|
| **1 (Oct 5–11)** End to end on a fallback skill | Nebius accounts, promo codes, budget alerts, **RTX PRO 6000 quota request (uk-south2)**. Tier 0 on the Nebius VM: RoboLab + N1.7-DROID on the Linux laptop. Port the tool service to x86. Build `POST /run` + `authorize()` + trust check. Nemotron tool-calling loop over `tools.json` on Token Factory. | **The must-ship demo works:** order → plan → gate refuses or allows → the skill runs, using the `libero_object` checkpoint or a RoboLab task |
| **2 (Oct 12–18)** Make the skill real | Isaac Lab sorting scene (3 colours, 2 bins). Scripted expert generating 500–1,000 DROID-format demos. Fine-tune on spot RTX PRO 6000 with frequent checkpoints. Tavily gates (datasheet limit, recall → park, fault code → ticket). RBAC policy + human approvals | A fine-tuned checkpoint exists; Tavily blocks a pick live |
| **3 (Oct 19–25)** Prove it at scale | Connect the Thompson-sampling gate to the new runner. Zero-shot vs fine-tuned across 10 phrasings and held-out colours, thousands of episodes on Nebius. Confidence-interval plots and cost per 1,000 episodes. **Oct 22 cut line:** real Franka clip, or fall back to a webcam verify | The gate licenses the fine-tuned skill on evidence |
| **4 (Oct 26–29)** Ship | Video under 3 min (story above), README (architecture, impact numbers, Nebius usage), prior-work note, tool feedback, license. **Submit Oct 29** | Devpost submitted |

## Risks and cut lines (from the red team)
| Failure | Cheapest mitigation | Cut line |
|---|---|---|
| **Scope:** about 20 person-days is all your part-time capacity | Freeze the must-ship list; drop each stretch item that misses its date | **Oct 11:** must-ship runs end to end |
| **Isaac/GR00T integration** (Python 3.11/3.12; Blackwell sm_120 wheels) | RoboLab's 3.11 client already talks to the GR00T server over ZMQ, so it's two containers. **Clone RedDishesInBin; don't build a new scene first** | **Oct 9:** reproduce about 15/40, or stay on Hyperion's working LIBERO runner |
| **DROID-format fine-tune** fails in closed loop | Round-trip 5 demos through GR00T's loader and replay them open-loop **before** generating 1,000 | **Oct 14:** replay passes. **Oct 20:** beats 15/40, or the video shows "the gate kept refusing" (still a valid result) |
| **Quota + spot** (only 2 L40S of quota) | RTX PRO 6000 in uk-south2, requested day 1. Resumable evals keyed by (arm, seed). Checkpoint every 500 steps. Run the on-camera sweep on demand | **Oct 8:** no quota means evals stay on the laptop |
| ~~**Teammates' code**~~ | **Resolved Oct 4:** Megha, Amal and Ferbin all agreed | Done |
| **Hardware footage** (a lab Franka isn't DROID's ZED 2 + ZED Mini rig) | Put any real arm with a scripted pick behind the same `/run`. **16 straight successes license it on camera** (batches of 4; 13 if you check every trial). Note that the rules let the sponsor ask for hardware access, so a borrowed lab arm is a risk | **Oct 12:** access confirmed. **Oct 22:** footage shot |

## Update (Oct 4, evening): findings from the Linux runbook
- **The laptop can't do the GPU work.** It has an RTX PRO 2000 Blackwell with 8 GB. GR00T inference needs 16 GB+, Isaac Sim 5.1 lists 16 GB as its minimum, RoboLab recommends 48 GB, and its TiledCamera hangs on laptop Blackwell chips (Isaac Lab #4951/#5001). **Use the Nebius RTX PRO 6000 VM from day 1.** The laptop runs the control plane, scripts and git.
- **Task names:** `BananasInBinThreeTotalTask` and `RedDishesInBinTask`. RoboLab needs `uv sync --extra isaac50` (or `isaac51`) plus git-lfs. The GR00T example README is stale.
- **Each RoboLab call boots Isaac Sim, so commissioning uses batches of 20 episodes,** not 4. With 20/20, P(rate ≥ 0.8) = 0.991, so a perfect skill passes in one launch.
- **Fine-tune data risk:** RoboLab's exporter writes LeRobot v3 with joint-position state, not DROID's 17-D v2 layout, so expect a conversion step. Validate 5 episodes first (`docs/RUNBOOK.md` §3.3).
- **Quota:** the default RTX PRO 6000 quota is 32 GPUs in uk-south2/eu-south1, so the Oct 8 cut line is just "confirm the quota row shows 32".

## Update (Oct 5): the rules, re-read live
Checked against the [overview](https://nebiusglobalaihackathon.devpost.com/) and the
[Official Rules](https://nebiusglobalaihackathon.devpost.com/rules) on Oct 5.

**What the rules add to our plan:**
1. **Give Nemotron a visible second job.**
   - Why: the first judging criterion asks "how effectively does it use Nebius Token Factory or AI Cloud model(s), and NVIDIA Nemotron". Today Nemotron only turns an order into skill calls.
   - Proposal for the must-ship (team to confirm): Nemotron also explains every refusal, block and revocation to the supervisor in plain English, from the audit record, and the video shows it.
   - This restores, in minimal form, the "summarize" step of the Brain layer above. It costs pennies on Token Factory.
2. **Run one evaluation sweep as a Nebius Serverless Job.**
   - Why: the Physical AI track text says "Use Nebius Serverless Jobs to run simulations, generate synthetic data, evaluate robot policies".
   - Cost: jobs bill at the same per-second Compute prices as a VM, and a finished job leaves no idle machine, so this adds no budget.
   - Work: it needs our stack as a container image. The job's container disk is wiped when it finishes, so results must go to Object Storage or a shared filesystem, which are billed separately.
   - The platform is picked from the Compute VM types (the docs' example uses `gpu-l40s-a`). Whether `gpu-rtx6000-a` is offered for jobs is still to check.
3. **Each teammate joins the Nebius Builder Program**, which the rules say gives "credits for Nebius Token Factory, Tavily, and Nebius Academy".
4. **Everyone whose Hyperion code we reuse is on the team.** The submission must "be solely owned by you, your Team ... with no other person or entity having any right or interest in it".

**Facts confirmed:**
- **Sponsor and support clause:**
  - The Sponsor is Nebius B.V. alone.
  - The "financial or preferential support" clause covers Nebius and Devpost, so Hyperion being built on Dell/NVIDIA loan hardware is fine.
- **Prizes:** each project is eligible for one Overall Award or one Track Award, plus one Bonus Award.
- **The video:**
  - It must show the project working and how we used Token Factory and the NVIDIA models.
  - Judges aren't required to watch beyond 3 minutes.
  - No third-party trademarks or copyrighted music without permission.
- **The README** needs setup instructions and clear guidance for running the project. It must highlight the NVIDIA models, where Token Factory helped, and any other Nebius services. The form also asks for feedback on Token Factory, AI Cloud and the NVIDIA tools.
- **Testing and access:**
  - The project must stay free to test until judging ends (Dec 15).
  - Physical AI needs no demo URL.
  - If we show hardware that isn't widely available, the Sponsor may ask for physical access to it.
- **Open source:** components are allowed if we follow their licenses and build on top of them.
- **Admin:**
  - Everything in English.
  - One Representative submits for the team.
  - No changes after Oct 30, 10:00 AM PT.

## Budget
> **Credits confirmed (Oct 4):** a teammate attended Boston, so you have the $100 AI Cloud + $100 Token Factory attendee credits. Redeem them in week 1:
> - **AI Cloud:** it needs a card and a $25 top-up before the promo code applies. **Set a budget alert;** the card auto-charges if the balance goes negative.
> - **Token Factory:** promo codes are applied separately (Top up → promo).

- **AI Cloud $100:**
  - Tier 0–1: about $5–15 (all GPU work is on the Nebius VM; the 8 GB laptop can't host GR00T + Isaac Sim).
  - Fine-tunes: ~$40, at 2–4 runs × 3–6 h on spot RTX PRO 6000.
  - Eval sweep: ~$40–60.
  - Ask the Nebius team for the "additional platform credits" the event mentioned, and keep $20 of buffer.
- **Token Factory $100:** Nemotron-3-Super at $0.30/$0.90 per 1M tokens. Thousands of planner calls cost under $5.
- **Tavily:** 1,000 free credits a month (free for students).

## Before writing code
- [x] **Teammates' consent** to open-source Hyperion (Megha, Amal, Ferbin): **done Oct 4.**
- [ ] **Make the repo public with an OSS license** (Apache-2.0).
  - Add a `LICENSE` file. Keep the git history: the Oct 3 commit dates back up the prior-work note, and they credit each author.
  - **Run a secret scanner (e.g. gitleaks) over the full history before going public.** An earlier pattern scan of 187 history files found no keys. Checked Oct 4: history contains authors' names (Thiago Pari, "Ferbin (integration)") and the GB10's hostname (`gb10-88a8`), but **not** its IP address. All harmless.
  - Going forward, never commit weights, `.env` files, or credentials.
- [ ] **Prior-work note:** Hyperion was built Oct 3, inside the Aug 26+ window. Say what's new (gate enforcement, RBAC, Nemotron planner, GR00T sorting skill, Nebius evals).
- [x] **Attended Boston on Oct 2: confirmed.** You have the credits, and you're eligible for the Boston City Winner. **Pick Boston on the form.** A project can win only one bonus, so aim for Tavily ($3k); the City prize ($500) is the fallback if Tavily goes to another project.
- [ ] **Accounts:** Nebius AI Cloud + Token Factory promo codes, Tavily, and Hugging Face access for the **gated** Cosmos-Reason2-2B backbone.

## Brain + permission layer design
- **Planner: Nemotron-3-Super-120B-A12B.** TauBench V2 61.2 (Nano scores 49.0), on Token Factory at $0.30/$0.90 per 1M tokens.
  - License: NVIDIA Nemotron Open Model License (commercial use OK with attribution).
  - Tool calls use the OpenAI format. **Smoke-test tool calling on Token Factory in week 1**; there's no per-model support list.
- **Policy engine: [Cedar](https://docs.cedarpolicy.com/auth/authorization.html).** Default deny, and `forbid` overrides `permit`. AWS AgentCore uses Cedar to gate agent tool calls, which is precedent to cite.
  - The policy enforcement point is the `/run` endpoint. It fills `context` (hour, human_in_zone, approver, **skill_licensed**) from clocks, sensors, verified tokens and `trust.json`, **never from LLM text**.
- **Escalation:**
  - A deny returns a reason and opens a ticket.
  - Supervisor approval mints a **single-use, short-lived token bound to the command hash**.
  - Mode changes need two humans (NIST "two-person control").
  - Every decision is logged.
- **Safety framing (say this explicitly):** RBAC gates *intent* (who may request which mode, speed ceiling or zone), mapped to ISO 10218-1/2:2025 operating modes, ISO/TS 15066 speed/force limits and IEC 62443 zones. **E-stops and monitored limits stay in the robot's safety controller, outside the LLM/RBAC path.**
  - Prior art to cite: RoboGuard cut unsafe LLM robot plans from over 92% to under 3% under jailbreaks ([arXiv 2503.07885](https://arxiv.org/abs/2503.07885)). Also CaMeL capabilities ([2503.18813](https://arxiv.org/abs/2503.18813)) and AgentSpec ([2503.18666](https://arxiv.org/abs/2503.18666)).
- **Roles:**

| Role | Allowed |
|---|---|
| operator | pick/move in cell1, ≤80% speed |
| supervisor | mode and limit changes; approves escalations |
| maintenance | manual mode in the maintenance zone, ≤25% speed |
| **ai_agent** | housing/lid parts → bins A/B, ≤50% speed, 06–22h, **only licensed skills**, never modes |

- **Cedar policy, tested Oct 4 with cedarpy 4.12.1:** all 18 original cases pass, 3 fail-closed checks pass, and **4 new licensed-skill cases pass**:
  - Unlicensed skill → Deny.
  - Missing flag → Deny.
  - Unlicensed but supervisor-approved → Allow (the escalation path).
  - Operator "approval" → Deny.
  - The policy and tests are in `earned-autonomy-rbac/` next to this file. Run `pip install cedarpy && python test_licensed.py`.
```cedar
permit (principal in Role::"ai_agent", action in [Action::"pick_place", Action::"move_to"], resource in Zone::"cell1")
when { ["housing","lid"].contains(context.object_class) && ["A","B"].contains(context.bin)
       && context.speed_pct <= 50 && context.hour >= 6 && context.hour < 22
       && context.skill_licensed };   // earned autonomy: set from trust.json by the PEP
permit (principal in Role::"ai_agent", action == Action::"pick_place", resource in Zone::"cell1")
when { context has approver && context.approver in Role::"supervisor" && context.speed_pct <= 50 };
permit (principal in Role::"operator", action in [Action::"pick_place", Action::"move_to"], resource in Zone::"cell1")
when { context.speed_pct <= 80 };
permit (principal in Role::"supervisor", action in [Action::"change_mode", Action::"set_speed_limit"], resource in Zone::"cell1");
permit (principal in Role::"maintenance", action == Action::"change_mode", resource in Zone::"maint")
when { context.speed_pct <= 25 };
forbid (principal in Role::"ai_agent", action in [Action::"change_mode", Action::"set_speed_limit"], resource);
// fail closed on missing fields
forbid (principal, action, resource) unless { context has human_in_zone && context has speed_pct
       && (!context.human_in_zone || context.speed_pct <= 25) };
```
