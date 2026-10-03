# ShiftLead: Business Analysis (consolidated)

Source: Thiago's research on the GB10 hackathon box (`promaxgb10-88a8:~/hack/business/`), copied to `~/gb10-business/` on 2026-10-03.
This file condenses all 14 source files (~40k words): the brief, the one-page business model, the deck content, research
tracks A-H, and fact-checks V1-V3. Every number below comes from those files. Tags follow the original:
**[cited]** published source, **[measured]** on the GB10 today, **[assumption]** their proposal or estimate, **calc** = arithmetic on the inputs shown.

---

## 1. What ShiftLead is

**Event:** Dell x NVIDIA "Dell Pro Max with GB10" hackathon (BuilderBase, Boston, Sat Oct 3 2026). 40 teams, code freeze
18:00 ET, top 8 pitch to a Dell/NVIDIA panel. The rules: an always-on business agent, 100% local on the GB10 (no cloud LLM at
runtime), on NemoClaw + OpenClaw + OpenShell, wired to a real channel (Discord), using tools without a human driving each step.

**Product:** an AI operations supervisor for physical operations, meaning work where fixing a problem needs a person to physically get there.

The loop: **detect -> decide who -> get them there -> verify the fix -> summarize**

| Step | What it does |
|---|---|
| Detect | Code watches an ops data feed: thresholds, stuck assets, errors, inventory mismatches, throughput drops, deadline risk |
| Decide who | Qualified, available, can arrive before the deadline, using current location + travel time (transit/traffic) |
| Get there / verify | Tickets with a state machine and evidence, ETAs, and a **trust gate**: a fix, process, route, vendor or robot skill is accepted only when P(success rate >= 80%) >= 95% |
| Summarize | Shift summaries: inventory status + action plan |

**Design rule:** "code enforces, the model explains." Thresholds, assignment, travel times and trust decisions are computed in
code. The local LLM (Qwen3.6-35B-A3B, NVFP4, vLLM on the GB10) decides what to say, escalate and route, never the safety call.

**Framing:**
- Vision: the ops supervisor for any physical operation.
- Wedge: **robotics**. Demo = 20-robot simulated warehouse; GR00T N1.7 robot policies run on the same box and are commissioned through the trust gate.
- Transferability: generic core (event engine, tickets, people/travel assignment, trust gate, briefs) + per-industry adapters (connectors, detectors, vocabulary).

**One-liner:** *ShiftLead finds the problem, finds the person, gets them there and checks the fix, on one box per site. Robotics is the first market.*

---

## 2. The problem (Track A)

| Finding | Number | Source | Quality |
|---|---|---|---|
| Time to restart after a stoppage | **81 min, up from 49 min five years earlier** (+65%). Lost skilled maintenance staff ("great resignation") is one of three causes given | Siemens True Cost of Downtime 2024, **p.11** (V1 corrected from p.10) | Verified; large factories, not warehouses |
| Downtime cost, average distribution center | **"can be more than $10k per hour"** (say "can be", not "loses") | Honeywell Intelligrated product page | Vendor marketing, no method |
| Idle-labor-only downtime cost (real DC case) | ~$40k over 17 h = **~$2,353/h** (calc) | Honeywell Forge case study, US retailer DC | Vendor case study |
| Downtime cost, large plants | $36k/h (FMCG) to $2.3M/h (automotive); SMEs up to $150k/h | Siemens 2024 | Don't use for a warehouse pitch |
| Plant incident frequency | 25 incidents/month, 27 h/month per large plant | Siemens 2024 | Manufacturing |
| E-com/logistics stoppages | 80% had 6+ unplanned events in 12 months; 35% cite too few skilled techs | MultiSensor AI / Censuswide, Sep 2026, n=152 | Vendor-sponsored |
| First-time fix rate | **77% avg, 88% top, 60% bottom**; MTTR 4.5 days | Aquant 2026 benchmark (30M service events) | Vendor, strongest FTF source |
| Failed visits | 25% of service cost (median); "1 in 5 cases could be resolved remotely" | Aquant 2026 | Vendor |
| Labor shortage | Industrial machinery mechanics: **51,900 openings/yr, +14% 2025-35** | BLS OOH, Aug 2026 | Primary |
| Robot field engineers travel | "up to 85%" (HAI Robotics); 40-100% at Boston-area firms | Job postings | Primary |
| Even best robots need people | Vecna: 99.9% uptime, **on-site** assist < 1% of operating time (remote teleop not counted) | Vecna page | Vendor; V1 corrected the wording |

**Honest gaps (not found):** no rigorous survey of dispatcher coordination time; no published alarm-to-dispatch benchmark; no
warehouse annual downtime hours; no independent AMR intervention/MTTR data; no public RaaS SLA credit values.

### Illustrative per-site value (20-robot warehouse) [assumption, calc]

| | Conservative | Mid | Aggressive |
|---|---|---|---|
| Incidents/yr | 6 | 24 | 60 |
| Minutes saved per incident | 10 | 20 | 32 |
| $/downtime hour | $2,353 | $10,000 | $36,000 |
| Downtime avoided | $2.4k | $80k | $1.15M |
| Supervisor/dispatcher time | $6.7k | $17.2k | $42.0k |
| Repeat truck rolls avoided | $0.1k | $0.9k | $5.7k |
| **Total per site per year** | **~$9.1k** | **~$98k** | **~$1.2M** |

Value is almost all downtime minutes. Rule of thumb: **1 avoided downtime hour ~ $10k.** An idle robot is cheap (~$5.50-6.35/robot-hour of RaaS rent); an idle *site* is what costs money.

---

## 3. Market (Track B)

| Layer | Number | Tag |
|---|---|---|
| US maintenance & repair workers (SOC 49-0000) | **6,086,190** (3.9% of US employment) | [cited] BLS OEWS May 2025 |
| US warehouses (NAICS 493, private) | **23,848** (a floor: misses wholesaler/retailer DCs) | [cited] BLS QCEW Q1 2026, preliminary |
| US warehouses running robot fleets | ~**4,770** (20% share, **unsourced**; sensitivity 10-30%) | [assumption] |
| US hospitals | **6,100** | [cited] AHA Fast Facts 2026 |
| US public EV charging | 82,581 locations, 260,486 ports | [cited] DOE AFDC |
| Logistics robots sold worldwide 2024 | **102,900 (+14%)**; RaaS fleet +31%, logistics RaaS +42% | [cited] IFR, Oct 2025 (global) |
| Mobile robot revenue | ~$5B (2024) -> $14B (2030) | [cited] Interact Analysis via CFO Dive |
| FSM software (global) | **$4.7B (2024) -> $9.2B (2030), 12% CAGR** | [cited] Verdantix; other reports range $11.8-24.3B by 2030 (SEO, ignored) |

**Sizing at $1,000/site/month:** robot-fleet warehouses ~$57M/yr; hospitals ~$73M/yr.
**3-year goal:** 2-5% of robot-fleet sites = **95-239 sites, $1.1M-$2.9M ARR** [assumption].
Cross-check: one Locus-sized partner (350+ sites) = $2.1M-$12.6M ARR depending on price.

**Momentum:** ServiceTitan IPO Dec 2024 (~$8.9B first-day cap); MaintainX $150M at $2.5B (Jul 2025); Samsara $2.125B ARR +30% (Sep 2026), whose 10-K says physical ops are >40% of global GDP; Salesforce Agentforce for Field Service and IFS buying TheLoops (both 2025).

---

## 4. Competition (Track C, fact-checked in V3)

**Bottom line from the research: two claims are FALSE and must not be said on stage:**
1. "Nobody connects detection to travel-aware dispatch." Microsoft (Connected Field Service + RSO), Salesforce (Connected Assets + FS optimization) and ServiceNow all do alarm -> work order -> skills/location/travel-aware assignment.
2. "On-prem local LLM is unique." ServiceNow Private Stack (Apr 2026) runs its LLMs on customer GPUs; Siemens Industrial Copilot "runs entirely on-site" on NVIDIA NIM; IBM Maximo and MiR Fleet run on-prem.

| Product | Covers | Gap for this job | List price |
|---|---|---|---|
| Salesforce Field Service | Skills + traffic-aware scheduling; Connected Assets telemetry | Cloud integration project; no evidence-based fix check | $175-$650/user/mo; **Connected Assets $15,000/org/mo** |
| Microsoft D365 Field Service | IoT alarm -> work order -> travel-optimized dispatch | Cloud only (on-prem retired Jun 30 2022); chains IoT Hub + Stream Analytics + Service Bus + Logic Apps + FS + RSO; RSO uses historical, not real-time, traffic | $105/user/mo + $30/optimized resource/mo |
| ServiceNow (incl. Private Stack) | Skills + location dispatch (Google Maps travel time); self-hosted option | Whole-platform program; paid workshop required | Not public |
| InOrbit, Formant (robot ops) | Detect robot incidents | Stop at Slack/PagerDuty/SMS/webhook; no "who goes" or travel | Not public (InOrbit has a free tier) |
| PagerDuty | Alert routing, AI agents | Routes by on-call schedule, not location | $21/user/mo (Professional, annual) |
| CMMS (MaintainX, UpKeep, Fiix, Limble) | Condition triggers -> work orders | No travel-aware dispatch, no verification | $20-$75/user/mo |
| Siemens Industrial Copilot | On-site maintenance Q&A | Doesn't pick who goes or verify the fix | Not public |

**Defensible gaps:**
1. **Robot alarm -> named field engineer with an ETA**, out of the box. This is the wedge.
2. **Evidence-gated fix verification + statistical trust gate** for anything new. Say "we haven't seen it", not "nobody does it".
3. **The whole loop as an appliance**, data on site, no IT program. The difference is packaging and buyer, not a new algorithm.
4. (Minor) Real-time and public-transit-aware travel. Don't lead with it.

**Positioning:** *"ShiftLead is the on-site AI shift supervisor for physical operations, starting with robot fleets. It turns an
alarm into the right qualified person on the way with an ETA, re-checks the fix against live data, and lets nothing new go live
until the evidence says so. It runs on one box, and no operational data leaves the site."*

**Important honesty note about our own code:** a ticket CAN be resolved without evidence today. When resolved, the Supervisor
is woken to re-check live data (`tools_service.py`). The only hard code-enforced gate is the trust gate for new skills/routes.
Never say "a ticket can't close without evidence." A hard no-resolve-while-active gate is a small roadmap item.

---

## 5. Why local (Track D + measurements in Track F)

**Core argument: legal and operational, not token price.**

| Reason | Evidence |
|---|---|
| Worker location is regulated | Connecticut §31-48d: written notice for on-premises electronic monitoring (penalties **up to** $500/$1k/$3k). California CPRA: "precise geolocation" is sensitive PI (employee exemption expired Dec 31 2022). NY and DE have notice laws too |
| EU | AI Act Annex III 4(b): monitoring/evaluating workers is high-risk; task allocation only if "based on individual behaviour or personal traits". High-risk duties postponed to **2 Dec 2027** (Reg. (EU) 2026/1744). CNIL fined Amazon France Logistique for warehouse scanner tracking (cut from EUR 32M to EUR 15M on appeal, Dec 2025) |
| OT networks stay offline | CISA/FBI/EPA/DOE, May 2025: **"Remove OT connections to the public internet."** (strongest point) |
| Defense suppliers | DFARS 252.204-7012: external cloud must meet FedRAMP Moderate |
| Hospitals | HIPAA identifiers include geography, device IDs, faces |
| Cloud residency surcharges | OpenAI +10% data-residency endpoints; Anthropic 1.1x for US-only inference |
| Resilience | Detection, tickets, assignment, trust gate and LLM all run on the box; only Discord needs the internet |

**Caveat they flagged:** local deployment does NOT remove notice duties or EU AI Act classification. Pitch the audit trail + trust gate as compliance features.

### Measured on the GB10 today (Track F, 12:09-14:43 ET, read-only)
- 249 LLM calls, 0 errors, 0 preemptions.
- Prompt: mean **30.3K tokens**/call (p95 ~93K); output mean **514** (thinking off).
- Prefix-cache hit rate **83%**.
- Latency: p50 **6.75 s**, mean 14.1 s, p95 49 s; time-to-first-token p50 0.62 s.
- Decode: 66-69 tok/s single-stream; 97 tok/s avg, 142 tok/s peak at 4 concurrent.
- Busiest 10 min: **9.8 calls/min**, max 4 concurrent, **0 queued**, KV cache never above 5%.
- **~9 LLM calls per agent wake**; 2.4-4.9 calls per ticket; a full wake ~108 s (decode-bound).
- Memory: vLLM ~59 GiB, GR00T servers ~21 GiB total, 91 of 121.6 GiB used, 30 GiB free. GPU 58-60 W under load, 13 W idle.
- vLLM runs NVFP4 through Marlin weight-only path (no native FP4 compute detected), so there is untapped throughput.
- Waste spotted: 63 `POST /tickets` for 41 tickets (22 duplicates/rejects); huge `GET /events` payloads (18-35 KB) inflate every call.
- Ops note: during the window `SUPERVISOR_DELIVER_TO` was unset, so autopilot replies were **not posting to Discord**.
- Deck's "3.4 s per turn" only holds for a short tool-calling turn (25% of calls). Label it that way.

**Typical-site projection** [assumption]: 100 events + brief + 2 shift summaries + 30 chat Qs/day = **~1,065 calls, 32.3M prompt tokens (83% cached), 0.55M output/day**. One box has ~13x headroom on average, ~4x at an assumed peak hour.

### Cost vs cloud (calc on that typical load, list prices 2026-10-03, verified in V2)

| Option | Per site per year |
|---|---|
| Claude Sonnet 5.5 | $7,957 ($8,957 with cache-write premiums) |
| gpt-6.1-sol | $6,979-$7,979 |
| Gemini 3.1 Pro Preview | $8,357 + cache storage |
| Hosted Qwen3.6-35B-A3B (OpenRouter/DeepInfra) | **$485-$2,308** (cheaper than the box) |
| **Dell Pro Max GB10** | $6,166-$9,007 one-time (~$2.1k-$3.0k/yr over 3 yrs) + $165-$360/yr power |

Payback vs frontier APIs: **8-16 months**. Honest footnote: hosted copies of the same open model are cheaper per token, but then the data leaves the site.

**Hardware prices (V2):** Dell list $9,007 (4TB) default; $6,557 (2TB); $6,177 (1TB); absolute min $6,166. No sale. NVIDIA DGX Spark FE MSRP **$4,699** (raised from $3,999 in Feb 2026 for memory costs); NVIDIA says OEM GB10 pricing is set by OEMs, so don't compare directly.

---

## 6. Business model

| Block | ShiftLead |
|---|---|
| Customers | **First:** robot companies and RaaS providers whose field teams travel to customer sites; buyer = VP/Director of Field Service. **Second:** multi-site warehouses / 3PLs with robot fleets. **Next:** hospital clinical engineering, then grocery refrigeration and facilities |
| Value | The full loop with verification; code enforces, model explains; data stays on site |
| Revenue | **$1,000/site/month**, 36-month term: core + 1 industry pack + unlimited people. Extra packs are add-ons [assumption] |
| Hardware | Customer buys the GB10 through standard Dell channels (stays on Dell's books, protects software margin) |
| Channels | Direct to robot companies' field service leaders, rolled out per customer site with the fleet; later integrators build packs |
| Ecosystem | InOrbit/Formant webhooks as inputs; Salesforce/Microsoft as ticket destinations. Programs to apply to: NVIDIA Inception (free, no equity), Dell AI Ecosystem Program (self-validated blueprint + catalog listing), Dell OEM Solutions (de-branded box). **None are partnerships today** |
| Costs | Pack/integration building + support. **~$0 per-token inference** (runs on customer's box) |

### Per-site economics
- Subscription: $12,000/yr.
- **Break-even: ~8 min of avoided site downtime per month** at $10k/h: ($1,000 + $9,007/36) / ($10,000/60) = 7.5 min, rounded up. With the cheapest box, 7.0 min.
- Counting idle labor only ($2,353/h): **30-32 min/month**.
- Price anchors: ~24% of a dispatcher's median wage ($50,340, BLS); 2.5-5.7% of renting a 20-robot fleet ($880-$2,000/robot/mo, Sacra estimate, internally inconsistent); below D365 for a 12-person team (~$1,560/mo before Azure); Salesforce Connected Assets alone is $15k/org/mo.
- **Honest read:** the conservative case ($9k/yr value) does NOT cover $12k + the box. Sell first where downtime is expensive or incidents frequent.

**Example customer** (25 sites, 15 field engineers): $300k ARR, $900k over 3 years; customer buys $154k-$225k of GB10 hardware from Dell; a second pack on every site adds ~$45k/yr.

### Pricing conflict (OPEN DECISION)
| Source | Proposed price |
|---|---|
| business-model.md / deck | **$1,000/site/mo** (recommended) |
| Track G | **$400/site/mo** incl. core + 1 pack + 25 assets + unlimited techs; +$150/extra pack; +$15/asset above 25 |
| Track B | sized at $500-$3,000 |

Track G's reasoning for $400: at today's Dell price, the box costs 1.3-1.9x a site's first-year $4,800 fee; all-in 3-year ROI only ~0.9-1.2x under wage-only assumptions. Software alone breaks even at ~2.4 supervisor-hours saved per site per week (3.4-3.9 h including the box). The $1,000 price leans on the downtime ($10k/h) argument instead of labor.

### Analogs (Track G)
- **Samsara:** $2.125B ARR +30%, 77-78% gross margin, priced per asset per application, 3-5 year terms, device included.
- **Motive:** $501M ARR, 70% GM, NDR 110% core / 126% large, ~3-year terms, **70% of ARR now outside its original vertical** (trucking). This is the land -> expand -> new vertical pattern.
- **Dell + Cohere North:** precedent for Dell selling an ISV's agentic platform turnkey on-prem.
- Targets: 80%+ software GM, 110%+ NRR, ~90% gross retention, CAC payback <= 18 months.
- Don't bundle NVIDIA AI Enterprise ($4,500/GPU/yr would be 94% of a $4,800 site fee); use open-source vLLM.
- **Not found:** revenue split for ISV software pre-installed on Dell hardware, or how a small ISV gets onto Dell's price list. Suggested as a question to ask the Dell judges.

---

## 7. Go-to-market

1. **Land (0-6 mo):** 3-5 site pilot with one robot company. The pilot measures the two big unknowns: minutes saved per incident and incidents per site. Join Inception; submit a Dell AI Ecosystem blueprint.
2. **Expand (6-18 mo):** all that customer's sites + a second pack. Target NRR >= 110% (Motive's core is 110%).
3. **New vertical (18+ mo):** hospitals, then grocery refrigeration. Dell OEM de-branded box once volume justifies.

### Verticals ranked (Track E, judgment scores)
| Vertical | Score | Why |
|---|---|---|
| **Hospitals (HTM)** | 8 | Strongest why-local (HIPAA, $7.42M avg healthcare breach, CMS maintenance rule). 6,100 hospitals, **71,800 medical equipment repairers**; only 11% work for hospitals, 33% for equipment wholesalers who travel between sites, same shape as robotics. Trust gate = return-to-service test |
| **Grocery refrigeration** | 7 | Vivid clocks: food >41F for >4 h must be discarded; **EPA requires leak repair within 30 days with verification tests since Jan 1 2026**; automatic leak detection mandatory on large systems by Jan 1 2027. Trust gate maps ~1:1 onto EPA's verification tests. Weak why-local |
| Utilities & telecom | 7 | 389,700 workers, $44B-$80B/yr outage cost, but incumbents are deepest and assignment needs crews not individuals. Keep for Q&A |
| EV charging | 6 | Cleanest adapter (OCPP/OCPI open standards), NEVI 97% uptime rule (~263 h/port/yr budget), but status data is public by law so why-local is weak; NEVI funding contested |

Slide line: *"Same core: event engine, tickets, who-goes + travel time, trust gate, briefs. New adapter: connectors + detectors + vocabulary + qualifications."* Don't quote a "% of code reused"; nothing was measured.

### Boston-area target design partners (Track H, none are customers)
| Company | Location | Evidence |
|---|---|---|
| Symbotic | Wilmington | 10-K: ~half of ~2,000 employees "are located across customer sites where they install, commission, and maintain our systems" (strongest) |
| Locus Robotics | Wilmington | Director of Field Services: owns "technician scheduling, dispatching... reduce travel", 40-60% travel (posting removed Jan 2026); current "Onsite Support Engineer" openings at customer sites. **Already uses Salesforce Service Cloud** |
| Vecna | Waltham | Senior Field Service Tech, 75-100% travel (closed) |
| Berkshire Grey | Bedford | Technical Field Engineer, 90% travel (removed Nov 2025) |
| Pickle Robot | Charlestown | Field Service Tech, 75% travel, emergency dispatch (closed) |
| Boston Dynamics | Waltham | Field evidence **unverified**: leave out |

Say "natural first customers" and "have hired", never "our customers" or "are hiring".

---

## 8. Risks

1. **Incumbents add the loop.** Mitigation: integrate (alarm source in, ticket destination out) rather than compete as an FSM.
2. **Low-value sites:** box + subscription > value at quiet sites. Target high-downtime sites; the box also runs robot policies.
3. **Key assumptions unvalidated:** 20% robot-fleet share, minutes saved per incident, the $10k/h vendor figure. The pilot measures them.
4. **Regulation cuts both ways:** local doesn't remove notice duties or EU AI Act obligations.
5. **Discord is a cloud hop:** internet outage stops chat alerts (rest of loop keeps running). Local alert fallback is roadmap.
6. Hardware price volatility: Dell GB10 has moved from ~$4.6k to $9k; quote a range and re-check live.

---

## 9. Judge Q&A prep (from deck-content.md)

| Question | Answer |
|---|---|
| "Salesforce and Microsoft already do this." | They're our dispatch benchmark. With them, robot alarm -> work order is a cloud integration project; Salesforce's telemetry add-on alone is $15k/org/mo. We ship the loop ready-made on one box, re-check the fix in live data, and gate anything new. We can push our tickets into their tools |
| "Hosted Qwen is cheaper. Why a box?" | Per token, yes (~$0.5k-$2.3k/yr). But then worker locations and plant data leave the site, which CT/CA law, the EU AI Act and CISA's OT guidance push against. The box also runs the robot policies |
| "Locus already uses Service Cloud." | Then we feed it: alarm -> ticket with evidence + proposed person -> pushed into Service Cloud |
| "Who pays for the box?" | Customer buys it through standard Dell channels. Our subscription is software only, 3-year term matching box life |
| "Is $10k/h real?" | Honeywell Intelligrated: an average DC "can be more than $10k per hour". Idle labor only gives ~30 min/month break-even |
| "Internet goes down?" | Detection, tickets and trust gate keep running on the box; only chat needs internet |
| "Beyond robots?" | Industry packs on the same core: hospitals first (71,800 repairers, a third at equipment sellers who travel), then grocery refrigeration (EPA 30-day leak repair) |
| "InOrbit/Formant will add dispatch." | They expose webhooks; ShiftLead sits behind them as the part that decides who goes and checks the fix |

---

## 10. Fact-check corrections (V1-V3) to respect

- Honeywell: "**can be** more than $10k/h", not "loses".
- Siemens: cite **p.11**; "five years ago" (baseline 2019); lost skilled labour is one of **three** factors; large manufacturing plants only.
- Vecna: < 1% is the **on-site** assist rate, not all human help.
- QCEW 23,848: label "private, preliminary"; all ownerships = 24,115.
- IFR figures are **worldwide**.
- Sacra Locus numbers are estimates and don't reconcile (17,000 x $2,000 x 12 = $408M vs $180M ARR).
- Salesforce top tier is named "**Agentforce 1 Field Service**".
- Microsoft RSO is $30 per **resource** (not technician), paid yearly.
- Connecticut penalties are **maximums**.
- EU AI Act task allocation is high-risk only when "based on individual behaviour or personal traits".
- Locus posting shows they already use Salesforce Service Cloud: this supports the "handoff gap" framing, not "no tooling".

---

## 11. My observations (not in Thiago's files)

- **The price is unresolved.** The deck says $1,000/mo while Track G, the most thorough pricing track, recommends $400. The two rest on different value arguments (downtime vs labor). Pick one before the pitch so the "8 minutes" number and the "who pays" story stay consistent.
- **The headline "8 min" depends on one vendor marketing figure** ($10k/h, no method). The conservative 30-32 min figure is more defensible if a judge pushes.
- **The research is careful about honesty.** Every risky claim was downgraded to "we haven't seen it". The weakest spot is the claim that the fix is verified: in code, it's an agent re-check, not a hard gate.
- **Track D used early assumptions** (32K prompt / 450 output / 90% cache); the deck correctly switched to Track F's measured numbers (30.3K / 514 / 83%). Use F's figures.
- **Two cheap engineering wins from Track F:** trim `GET /events` payloads and dedupe ticket posts. Both cut tokens and latency.

## Source files
`~/gb10-business/business-model.md`, `deck-content.md`, `research/{BRIEF, A-pain-roi, B-market, C-competition, D-why-local, E-verticals, F-local-measurements, G-pricing-gtm, H-boston-robotics, V1-factcheck, V2-factcheck, V3-factcheck}.md`
