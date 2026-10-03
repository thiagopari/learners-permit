# ShiftLead: business model content for the deck

From session dell-77 for dell-05. The research is in `~/hack/business/research/` (tracks A–G, fact-checks V1–V3).
Tags: **[measured]** on this box today · **[cited]** published source · **[assumption]** our proposal or estimate.
"calc" marks a number calculated from the inputs shown. Any calc that uses an assumption is tagged [assumption].
The GB10 wording follows your rule: the customer buys it through standard Dell channels. There is no partnership claim.

---

## Main slide, 4:10–4:30 · Business model

**Headline (37 chars):** One box and one subscription per site
*Alternative (39 chars):* Eight saved minutes a month pays for it

| Block | Text (≤ 15 words) | Tag · source label |
|---|---|---|
| Who pays | Robot companies' field service teams, who pay for every trip and uptime promise. | [cited] Locus job posting · Symbotic 10-K |
| Price | $1,000 per site per month: the core, one industry pack, unlimited people. | [assumption] our proposed price |
| Runs on | One Dell Pro Max with GB10 per site, bought through standard Dell channels. | [cited] $6.2k–$9k list, dell.com, Oct 3 |
| Break-even | About 8 minutes of avoided site downtime a month covers both. | [assumption] calc, see the big number |

**Big number:** **8 min**. Caption: *of avoided site downtime a month pays for the subscription and the box.*
On-slide label: *Assumption: $10k per downtime hour (Honeywell Intelligrated: downtime at an average DC "can be more than $10k per hour"), box spread over 3 years.*

**Script (44 words):**
> ShiftLead is priced per site: a thousand dollars a month, running on a GB10 the customer buys through standard Dell
> channels. First buyers: robot companies' field service teams. At about ten thousand dollars per downtime hour, eight
> saved minutes a month pays for both.

*Alternative script with the Boston line (50 words):*
> ShiftLead is priced per site: a thousand dollars a month, on a GB10 the customer buys through standard Dell channels.
> Natural first buyers: robot companies' field service teams, several a short drive from here. At about ten thousand
> dollars per downtime hour, eight saved minutes a month pays for both.

**Speaker notes:**
- **Break-even calc:** ($1,000 + $9,007 ÷ 36 months) ÷ ($10,000 ÷ 60) = $1,250 ÷ $167 per minute = **7.5 min**. With the
  cheapest config ($6,177) it's 7.0 min. The slide rounds up to 8.
- **Conservative case:** counting only idle labor ($2,353/h, from a Honeywell case at a US retailer's DC: about $40k
  over 17 hours), break-even is **30–32 min a month**. For scale, Siemens finds getting production running again after
  downtime takes **81 min on average, up from 49 five years earlier** (large factories, not warehouses; Siemens 2024,
  p.11).
- **Why "site downtime":** $10k/h is a whole-DC figure. One stuck robot in a fleet of 20 costs less, so we quote
  minutes of site downtime, not robot downtime.
- **Price anchors, all calc from cited inputs:**
  - $1,000 a month is about 24% of a dispatcher's median wage ($50,340 a year, BLS).
  - It's 2.5–5.7% of renting a 20-robot fleet at $880–$2,000 per robot per month. Those are Sacra's estimates, and its figures don't reconcile, hence the range.
  - It's below Microsoft Dynamics 365 Field Service for a 12-person team, about $1,560 a month before Azure and
    integration. That's 12 users × $105, plus 10 optimized resources × $30.
  - Salesforce's telemetry add-on (Connected Assets) alone lists at $15,000 per org per month.
- **Terms:** a 36-month term per site, matching the box's life. Extra industry packs are add-ons. The subscription is
  software only.
- **Who pays, evidence:**
  - Locus Robotics' "Director of Field Services" posting owns "technician scheduling, dispatching, and coverage
    models to improve response times and reduce travel". The posting was removed in Jan 2026. It also names
    Salesforce Service Cloud as a tool; see Q&A.
  - Symbotic's 10-K says about half its employees "are located across customer sites where they install, commission,
    and maintain our systems".
- **Boston line, optional, every fact verified (track H):** "Our natural first customers are a short drive from this
  room."
  - Symbotic (Wilmington): about half its employees "are located across customer sites where they install, commission,
    and maintain our systems" (10-K).
  - Locus (Wilmington), Vecna (Waltham), Berkshire Grey (Bedford) and Pickle (Charlestown) have all hired field
    technicians who spend 40–100% of their time traveling to customer robots.
  - None of them is a customer, so never say "our customers". Most of those job posts are closed, so say "have
    hired", not "are hiring". Leave Boston Dynamics out; its field-staff evidence is unverified.
  - Sources: https://www.vecnarobotics.com/contact/ ·
    https://jobs.drivecapital.com/companies/vecna-robotics/jobs/34342419-senior-field-service-technician ·
    https://builtin.com/job/technical-field-engineer/7345453 ·
    https://jobs.toyota.ventures/companies/pickle-robot/jobs/63444630-robotic-field-service-technician ·
    https://job-boards.greenhouse.io/locusrobotics
- **Links:**
  - Locus posting: https://builtin.com/job/director-field-services/7976188
  - Symbotic 10-K, FY2025: https://www.sec.gov/Archives/edgar/data/1837240/000183724025000278/sym-20250927.htm
  - Dell store: https://www.dell.com/en-us/shop/desktop-computers/spd/dellpromaxwithgb10fcm1253
  - Honeywell Intelligrated: https://automation.honeywell.com/us/en/products/warehouse-automation/solutions-by-strategy/connected-distribution-center/increase-reliability
  - Siemens True Cost of Downtime 2024 (p.11): https://assets.new.siemens.com/siemens/assets/api/uuid:1b43afb5-2d07-47f7-9eb7-893fe7d0bc59/TCOD-2024_original.pdf
  - BLS dispatchers (43-5032): https://www.bls.gov/oes/2025/may/oes435032.htm (data: https://data.bls.gov/timeseries/OEUN000000000000043503213)
  - Sacra on Locus: https://sacra.com/c/locus-robotics
  - Microsoft pricing: https://www.microsoft.com/en-us/dynamics-365/products/field-service/pricing
  - Salesforce pricing: https://www.salesforce.com/service/field-service-management/pricing/

---

## Backup B3 · Market

**Headline:** Robot fleets first, then any physical operation

| Layer | Count | At $1,000 per site per month | Tag · source |
|---|---|---|---|
| Logistics robots sold worldwide, 2024 | 102,900 (+14%) | n/a | [cited] IFR, Oct 2025 |
| US warehouses | 23,848 | n/a | [cited] BLS QCEW, Q1 2026, private, preliminary |
| First market: US warehouses running robot fleets | about 4,770 (20% assumed) | about $57M a year | [assumption] |
| Next pack: US hospitals | 6,100 | about $73M a year | [cited] AHA 2026 · revenue [assumption] |
| Every physical operation: US maintenance and repair workers | 6.09M | n/a | [cited] BLS OEWS, May 2025 |
| Field service software spend | $4.7B (2024) → $9.2B (2030) | n/a | [cited] Verdantix |

**Takeaway:** Three-year goal: 2–5% of robot-fleet sites, which is 95–239 sites and $1.1M–$2.9M a year. [assumption]

**Speaker notes:**
- **Calcs:**
  - 23,848 × 20% = 4,770 sites, and × $12,000 a year = $57M.
  - 6,100 × $12,000 = $73M.
  - 2–5% of 4,770 = 95–239 sites = $1.1M–$2.9M a year.
- **The 20% share is unsourced.** Track B found no published share of US warehouses running robot fleets, so it's
  labeled as an assumption. The file's sensitivity range is 10–30%.
- **QCEW undercounts.** It misses distribution centers run by wholesalers and retailers, so the site count is a floor.
- **Market reports vary.** Report summaries put field service software at $11.8B–$24.3B by 2030. We use only
  Verdantix, the most credible.
- **Momentum:**
  - ServiceTitan IPO, Dec 2024.
  - MaintainX raised $150M at a $2.5B valuation, Jul 2025.
  - Samsara reached $2.125B ARR, up 30%.
- **Links:**
  - IFR: https://ifr.org/ifr-press-releases/news/service-robots-see-global-growth-boom
  - BLS QCEW, NAICS 493: https://data.bls.gov/timeseries/ENUUS000205493
  - AHA Fast Facts (updated Feb 2026): https://www.aha.org/statistics/fast-facts-us-hospitals
  - BLS OEWS 49-0000: https://www.bls.gov/oes/2025/may/oes490000.htm
  - Verdantix: https://www.verdantix.com/venture/report/market-size-and-forecast--field-service-management-software-2024-2030-global

---

## Backup B4 · Competition

**Headline:** Others dispatch. We close the loop on site.

| Product | Covers | Gap for this job | List price |
|---|---|---|---|
| Salesforce Field Service | Skills- and traffic-aware scheduling; telemetry add-on | Cloud integration project; no evidence-based fix check found | $175–$650 per user/mo; Connected Assets $15,000 per org/mo |
| Microsoft Dynamics 365 Field Service | IoT alarm → work order → travel-optimized dispatch | Cloud only (on-premises retired 2022); integration project | $105 per user/mo + $30 per optimized resource/mo |
| ServiceNow, incl. Private Stack | Skills and location dispatch; self-hosted option (2026) | A whole-platform program | Not public |
| InOrbit, Formant (robot ops) | Detect robot incidents | Notify Slack or PagerDuty; no who-goes or travel time | Not public |
| PagerDuty | Alert routing, AI agents | Routes by on-call schedule, not location | $21 per user/mo, annual |
| **ShiftLead** | Robot alarm → ticket with code-attached evidence → right person + ETA → re-check after the fix; trust gate for anything new | One industry pack so far; the fix re-check is done by the agent, not yet a hard gate | $1,000 per site/mo [assumption] |

**Takeaway:** Travel-aware dispatch already exists. What we add is the ready-made loop from robot alarm to a checked
fix, with a trust gate for anything new, running on one box.

**Speaker notes:**
- **Don't say "nobody does travel-aware dispatch."** Microsoft, Salesforce and ServiceNow all match on skills and
  location and estimate travel time.
- **On the fix check, say "we haven't seen it", not "nobody does it".** None of the products reviewed accepts a fix
  based on post-fix evidence; they close when the technician marks the job done.
- **Be exact about our own fix check.** In the code, a ticket can be resolved without evidence. When the Scheduler or a
  human resolves one, the Supervisor is woken to re-check the robot or zone in live data and confirm in one line
  (`tools_service.py`, ticket update). The hard, code-enforced gate is the trust gate for new skills and routes. Don't
  say "a ticket can't close without evidence".
- **On-site AI isn't unique:** ServiceNow Private Stack and Siemens Industrial Copilot both run on site. Our point is the
  whole loop, ready-made on one box, without an IT program.
- **If a judge says "InOrbit or Formant will just add dispatch":** they expose webhooks, so ShiftLead can sit behind
  them as the part that decides who goes and checks the fix.
- **Links:**
  - Salesforce pricing: https://www.salesforce.com/service/field-service-management/pricing/
  - Salesforce route optimization: https://www.salesforce.com/service/field-service-management/field-service-route-optimization/
  - Salesforce Connected Assets: https://www.salesforce.com/service/field-service-management/asset-management/
  - Microsoft pricing: https://www.microsoft.com/en-us/dynamics-365/products/field-service/pricing
  - Microsoft Connected Field Service: https://learn.microsoft.com/en-us/dynamics365/field-service/connected-field-service-architecture
  - Microsoft on-premises retirement (June 30 2022): https://www.microsoft.com/en-us/dynamics-365/blog/?p=129624
  - Siemens Industrial Copilot runs on site: https://press.siemens.com/global/en/pressrelease/siemens-drives-ai-adoption-industrial-operations-x-and-nvidia-accelerated-industrial
  - PagerDuty schedules: https://support.pagerduty.com/docs/escalation-policy-vs-schedule
  - ServiceNow Private Stack: https://www.servicenow.com/community/product-launch-blogs/private-stack-deploy-the-full-servicenow-ai-platform-on-your/ba-p/3524144
  - InOrbit docs: https://developer.inorbit.ai/docs
  - Formant incident management: https://docs.formant.io/docs/incident-management
  - PagerDuty pricing: https://www.pagerduty.com/pricing/

---

## Backup B5 · Why local

**Headline:** Local, because the data has to stay on site

| Reason | Evidence | Tag |
|---|---|---|
| Where workers are is regulated | Connecticut §31-48d requires written notice of monitoring; California treats precise geolocation as sensitive; EU AI Act: AI that monitors and evaluates workers is high-risk | [cited] |
| Plant networks stay offline | CISA, May 2025: "Remove OT connections to the public internet." | [cited] |
| Internet down ≠ operations down | Detection, tickets and the trust gate run on the box; only chat messages go out via Discord | design |
| One box covers a site | Busiest 10 min today: 9.8 model calls/min, none queued, about 13× a typical site's average | [measured] · [assumption] typical site |
| Cost against frontier APIs | A typical site's load: $7k–$9k a year on mid-tier frontier APIs vs $2.2k–$3.4k a year for the box over 3 years | [cited] prices · calc |
| Honest footnote | Hosted copies of our open model cost less: $0.5k–$2.3k a year, but the data leaves the site | [cited] prices · calc |

**Takeaway:** We run locally because the data must stay on site. Against frontier APIs, the box also pays for itself in
about 8–16 months.

**Speaker notes:**
- **Typical site, a projection from today's measurements:** 1,065 model calls a day (100 handled events, briefs and
  chat), 32.3M prompt tokens a day of which 83% are cache hits (measured hit rate), and 0.55M output tokens a day.
- **Measured on this box, 12:09–14:43 ET:**
  - 249 model calls, about 30K prompt tokens and 514 output tokens per call on average.
  - About 9 model calls per agent wake-up.
  - The busiest 10 minutes had 9.8 calls a minute, up to 4 at once, with nothing queued.
- **Cloud cost per year for that load (calc, today's list prices, 365 days):**
  - Claude Sonnet 5.5: $7,957, or $8,957 with cache-write premiums.
  - gpt-6.1-sol: $6,979–$7,979.
  - Gemini 3.1 Pro Preview: $8,357, before cache storage.
  - Hosted Qwen3.6-35B-A3B: $485 (cheapest OpenRouter endpoint) to $2,308 (highest-priced OpenRouter endpoint).
    The cheapest is a 4-bit build on a small host. DeepInfra ($0.10 input / $0.95 output per 1M, no cache discount)
    comes to about $1,369.
- **Box cost per year:** $6,177–$9,007 over 3 years, plus $165–$360 a year in power. That's 140 W (GB10 chip TDP) to
  280 W (Dell's adapter rating), 24/7, at EIA's US commercial average of 13.41–14.53¢/kWh. That's an upper bound: the
  GPU measured 58–60 W under agent load today [measured].
- **Price check, live today:** the Dell price shows no sale. The cheapest Dell config is $6,166 without keyboard and
  mouse, and NVIDIA's own DGX Spark lists at $4,699; NVIDIA leaves other makers' GB10 prices to them, so don't compare
  the two directly.
- **Payback against frontier APIs:** the box price divided by (annual cloud cost minus power) = 8–16 months.
- **Fine print:**
  - Connecticut's penalties are maximums: up to $500 / $1,000 / $3,000.
  - EU AI Act Annex III 4(b) also covers task allocation, but only when it's based on individual behaviour or traits.
    The high-risk obligations were postponed to 2 Dec 2027 by Reg. (EU) 2026/1744 (law-firm summary, not checked on
    EUR-Lex).
- **Compliance:** running locally doesn't remove notice duties (Connecticut) or EU AI Act obligations. We present the
  trust gate and audit trail as compliance features.
- **Links:**
  - Connecticut statute: https://www.cga.ct.gov/current/pub/chap_557.htm
  - CPPA FAQ: https://cppa.ca.gov/faq.html
  - EU AI Act Annex III: https://artificialintelligenceact.eu/annex/3/
  - CISA: https://www.cisa.gov/resources-tools/resources/primary-mitigations-reduce-cyber-threats-operational-technology
  - Anthropic pricing: https://platform.claude.com/docs/en/about-claude/pricing
  - OpenAI pricing: https://developers.openai.com/api/docs/pricing
  - Google Gemini pricing: https://ai.google.dev/gemini-api/docs/pricing
  - OpenRouter endpoints: https://openrouter.ai/api/v1/models/qwen/qwen3.6-35b-a3b/endpoints
  - DeepInfra: https://deepinfra.com/Qwen/Qwen3.6-35B-A3B
  - EIA Table 5.3: https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_3
  - Measurements: `~/hack/business/research/F-local-measurements.md` (vLLM /metrics on the box)

---

## Q&A prep for the presenter

| If a judge asks | Answer |
|---|---|
| "Salesforce and Microsoft already do this." | They're our benchmark for dispatch. With them, going from robot alarm to work order is a cloud integration project; Salesforce's telemetry add-on alone lists at $15k per org per month. We ship the loop ready-made on one box. After a fix, the Supervisor re-checks the robot's live data, and nothing new
  goes live until the trust gate opens. If a customer already has a field service tool, we can push our tickets into it. |
| "Hosted Qwen is cheaper. Why a box?" | Per token, yes: about $0.5k–$2.3k a year for a typical site. But then worker locations and plant data leave the site, which is what the Connecticut and California rules, the EU AI Act and CISA's OT guidance push against. The same box also runs the robot policies. |
| "Locus already uses Salesforce Service Cloud." | Good: then we feed it. ShiftLead turns the robot alarm into a ticket with evidence and a proposed person, and pushes it into Service Cloud. We're the part between the robot and the field service tool. |
| "Who pays for the box?" | The customer buys it through standard Dell channels. Our subscription is software only, on a 3-year term that matches the box's life. |
| "Is $10k per hour real?" | It's Honeywell Intelligrated's figure: downtime at an average distribution center "can be more than $10k per hour". Counting only idle labor, break-even is about 30 minutes of avoided downtime a month. |
| "What if the internet goes down?" | Detection, tickets and the trust gate keep running on the box. Only the chat channel needs the internet. |
| "How does this grow beyond robots?" | Industry packs on the same core. Hospitals come first: 71,800 US medical equipment repairers, a third employed by equipment sellers who travel between sites. Then grocery refrigeration, where EPA has required leak repairs within 30 days since January 2026. |

---

## Optional numbers for your other slides (cited, single-checked)

- **The problem:** Siemens 2024: getting production running again after a stoppage takes 81 minutes on average, up from
  49 five years earlier. One reason Siemens gives is skilled maintenance staff lost in the "great resignation" (large
  factories).
- **100% local:** if a judge asks about the 3.4 s per turn, that figure is a short tool-calling turn. Today's live agent
  calls with about 30K-token prompts had a median of 6.75 s and a p95 of 49 s, with 2–4 sessions running at once
  [measured]. Consider labeling 3.4 s as "short tool-calling turn".
- **Beyond the warehouse:**
  - Hospitals: 71,800 medical equipment repairers (BLS 49-9062, 2025), and only 11% work for hospitals.
  - Grocery: refrigerant leaks must be repaired within 30 days, with verification tests (EPA, since Jan 1 2026).
