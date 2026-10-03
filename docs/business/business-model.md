# ShiftLead business model, one page

Dell Pro Max with GB10 hackathon, Boston, Oct 3 2026. The sources are in `~/hack/business/research/` (tracks A–G,
fact-checks V1–V3), and the slide-ready version is `deck-content.md`.
Tags: **[measured]** on our box · **[cited]** published source · **[assumption]** our proposal or estimate.

**In one line:** ShiftLead is an AI operations supervisor for physical operations. It finds the problem, finds the
person, gets them there and checks the fix, on one box per site. Robotics is the first market.

## Canvas

| Block | ShiftLead |
|---|---|
| **Customers** | **First:** robot companies and robots-as-a-service providers whose field service teams travel to customer sites. The buyer is the VP or Director of Field Service [cited: a Locus posting for a role that owns "technician scheduling, dispatching... reduce travel"; Symbotic says about half its staff work at customer sites]. **Second:** multi-site warehouses and 3PLs with robot fleets. **Next:** hospital clinical engineering, then grocery refrigeration and facilities. |
| **Problem** | The handoff from alarm to person is manual. Getting production running again after a stoppage takes 81 min, up from 49 five years earlier; one reason Siemens gives is skilled maintenance staff lost in the
"great resignation" [cited, Siemens 2024, large factories]. Industrial machinery mechanics have 51,900 openings a year, +14% to 2035 [cited, BLS]. First-time fix rates average 77% against 88% for the best [cited, Aquant 2026, vendor]. |
| **Value** | One loop: detect → decide who (skills, availability, travel time, deadline) → get them there → verify (the agent re-checks live data after a fix; a trust gate lets nothing new go live until the evidence says so) → summarize. Code enforces; the model explains. The data stays on site. |
| **Revenue** | **$1,000 per site per month** on a 36-month term, covering the core, one industry pack and unlimited people; extra packs are add-ons [assumption]. The customer buys the GB10 through standard Dell channels. |
| **Channels** | Sell direct to robot companies' field service leaders, who roll ShiftLead out to each customer site along with their fleet. Later, integrators build industry packs. |
| **Key resources** | The core (event engine, tickets, assignment by people and travel time, trust gate, briefs), the industry packs, and the local model stack (Qwen3.6-35B-A3B on vLLM, NemoClaw/OpenClaw/OpenShell). |
| **Ecosystem** | Robot fleet platforms (InOrbit and Formant expose webhooks) as inputs. Field service tools (Salesforce, Microsoft) as places to push tickets. Programs we could apply to: NVIDIA Inception (free, no equity) and the Dell AI Ecosystem Program (a software vendor validates its own product and gets listed) [cited]. None of these are partnerships today. |
| **Costs** | Building packs and integrations, plus support. **No per-token inference cost**: the model runs on the customer's box. The same load would cost $7k–$9k per site per year on mid-tier frontier APIs [cited prices, calc]. |

## Per-site economics

| Item | Value | Tag |
|---|---|---|
| Subscription | $12,000 a year | [assumption] |
| Customer's box | $6,177–$9,007 one-time (about $2.1k–$3.0k a year over 3 years), plus at most about $360 a year in power | [cited] dell.com · calc |
| Break-even | About **8 min** of avoided site downtime a month at more than $10k per downtime hour. Counting only idle labor, 30–32 min | [assumption] · calc |
| Illustrative value | $9k (conservative) / $98k (mid) / $1.2M (aggressive) a year for a 20-robot warehouse; the mid case is mostly avoided downtime | [assumption], Track A |
| Our inference cost | About $0 per token: it runs on the customer's box | design |

**Honest read:** the conservative case ($9k) doesn't cover $12k plus the box. ShiftLead pays off where downtime is
expensive or incidents are frequent, so that's where to sell first. A lower entry tier for small sites (Track G
suggested $400 a month) is an option.

**Example customer** (calc): a robot company with 25 customer sites and 15 field engineers.
- $300k a year in recurring revenue, $900k over 3 years.
- The customer buys $154k–$225k of GB10 hardware through standard Dell channels.
- A second pack on every site adds $150 per site per month in Track G's add-on pricing, about $45k a year.

## Go-to-market
1. **Land:** a 3–5 site pilot with one robot company. The pilot measures the two numbers we're assuming today: minutes
   saved per incident and incidents per site.
2. **Expand:** roll out to all of that customer's sites and add a second pack. Target net revenue retention of 110% or
   more; Motive reports 110% for core customers [cited, S-1].
3. **New vertical:** hospitals (71,800 US medical equipment repairers; only 11% work for hospitals, and 33% work for
   equipment wholesalers, whose engineers travel between sites [cited, BLS]), then grocery refrigeration (EPA has required leak repairs within 30 days since
   Jan 2026 [cited]). The precedent is Motive: 70% of its recurring revenue now comes from outside trucking and
   logistics [cited].

## Market (Track B)
| Layer | Number | Tag |
|---|---|---|
| US maintenance and repair workers | 6.09M | [cited] BLS May 2025 |
| US warehouses | 23,848 | [cited] BLS QCEW Q1 2026, private, preliminary (a floor) |
| Robot-fleet warehouses, our first market | about 4,770 sites, about $57M a year at our price | [assumption] 20% share |
| US hospitals | 6,100, about $73M a year at our price | [cited] AHA · [assumption] revenue |
| Field service software | $4.7B (2024) → $9.2B (2030) | [cited] Verdantix |
| Three-year goal | 2–5% of robot-fleet sites: 95–239 sites, $1.1M–$2.9M a year | [assumption] |

## Competition (Track C)
Positioning: *ShiftLead is the on-site AI shift supervisor for physical operations, starting with robot fleets. It turns
an alarm into the right qualified person on the way with an ETA, re-checks the fix against live data, and lets nothing new
go live until the evidence says so. It runs on one box, and no operational data leaves the site.*
- **Not unique:**
  - Travel-aware dispatch (Microsoft, Salesforce, ServiceNow).
  - Turning an alarm into a work order (Microsoft Connected Field Service, Salesforce Connected Assets).
  - On-site AI (ServiceNow Private Stack, Siemens Industrial Copilot).
- **Our angle:**
  - The whole loop ready-made on one box with no integration project.
  - A robot alarm becomes a named engineer with an ETA; robot fleet platforms stop at a Slack or PagerDuty alert.
  - A re-check after the fix, plus a statistical trust gate for anything new. We haven't seen either in the products we
    reviewed. Today the re-check is done by the agent; making it a hard gate in code (no resolve while the event is
    still active) is a small roadmap item.

## Risks
1. **Incumbents add the loop.** We integrate with them, as a source of alarms and a destination for tickets, rather
   than compete as a field service tool.
2. **Low-value sites.** At a quiet site the box plus the subscription costs more than the value. Target high-downtime
   sites, and remember the box can also run the site's robot policies.
3. **Key assumptions are unvalidated:** the 20% robot-fleet share, minutes saved per incident, and the $10k/h vendor
   figure. The pilot measures them.
4. **Regulation cuts both ways.** Running locally doesn't remove worker-monitoring notice duties or EU AI Act high-risk
   obligations (now due Dec 2027). The audit trail and trust gate are compliance features.
5. **Discord is a cloud hop.** An internet outage stops chat alerts, though the rest of the loop keeps running. A local
   alert fallback belongs on the roadmap.

## Open decisions for the team
- **Price point:** $1,000 a month is recommended. Track G suggested $400 for adoption, and Track B sized $500–$3,000.
- **First design partner:** pick one target. Verified Greater Boston candidates that run robots at customer sites with
  travelling field staff: Symbotic and Locus (Wilmington), Vecna (Waltham), Berkshire Grey (Bedford) and Pickle
  (Charlestown). None is a customer yet (track H).
