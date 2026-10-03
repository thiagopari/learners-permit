# Track C: Competitive landscape and competitor pricing (ShiftLead)

Date: 2026-10-03. Time box ~20 min. Read-only research; this file is the only output.

Method: official pricing pages, product docs, vendor press releases. **(V) = verified**: I opened the page and saw the
text/number. **(U) = unverified**: seen only in a search snippet or a secondary source. Several vendor sites blocked
automated fetches (ServiceNow product pages 403, Oracle 403, IFS 429, BusinessWire 403). Claims that depend on those
sites are marked (U) unless I could open another official page. "N / not found" means not found in the sources I
reviewed in 20 minutes. It does not prove the feature is missing.

---

## 0. Bottom line

1. **"Nobody connects detection to travel-aware dispatch" is false. Do not claim it.** Microsoft (Connected Field
   Service + Resource Scheduling Optimization), Salesforce (Connected Assets + Field Service optimization) and
   ServiceNow (Event Management + FSM Dynamic Scheduling) all document alarm -> work order -> assignment by skills,
   availability, location, travel time and time window. All three also ship AI agents for scheduling and job summaries.
2. **"On-prem with a local LLM" is not unique either.** ServiceNow Private Stack (April 2026) self-hosts the platform,
   including its production LLMs on customer-owned GPUs. Siemens Industrial Copilot for Operations "runs entirely
   on-site" on NVIDIA NIM. IBM Maximo can be deployed on-prem. MiR Fleet Enterprise runs on the customer's Windows servers.
3. **What is actually open (defensible):**
   - **Robot fleet incident -> a named field engineer with an ETA.** Robot ops platforms (InOrbit, Formant) stop at
     notifying Slack, PagerDuty, SMS or a webhook. On-call tools route by schedule and escalation timing only, with no
     location or travel. FSM suites can do it, but only after someone builds a telemetry integration.
   - **Evidence-gated verification of the fix.** Every product reviewed closes work when the technician marks it done.
     The partial exceptions are remote commands and actions (D365, Salesforce). No statistical acceptance gate was found,
     and nothing reuses such a gate to commission robot skills.
   - **Packaging and data locality.** In every FSM product I found, the full loop is a multi-product **cloud**
     integration. D365 needs IoT Hub + Stream Analytics + Service Bus + Logic Apps + Field Service + RSO, and Field
     Service on-prem was retired in 2022. Salesforce's telemetry piece alone lists at $15,000/org/month. The on-prem
     alternatives are either whole enterprise platforms or tools that don't dispatch people.

---

## 1. Matrix: product x loop step x deployment x price

Loop steps: **Detect** | **Decide who** (skills, availability, deadline) | **Travel-aware dispatch** (location,
travel time, ETA) | **Verify fix** | **Summarize**. Y = documented, P = partial, N = not found.

### 1a. Monitoring / alerting / incident response

| Product | Detect | Decide who | Travel-aware | Verify | Summarize | Deployment | List price | Src |
|---|---|---|---|---|---|---|---|---|
| PagerDuty | P: ingests alerts from monitoring tools; AIOps is an add-on (V) | P: **on-call schedule + escalation policy only** (V) | **N**: support doc says nothing about location or travel (V) | N | Y: Scribe agent (call transcripts), SRE agent "Paige" (context, remediation), Insights agent (V) | SaaS; no on-prem on pricing page (V) | Professional **$21/user/mo** annual, $25 monthly; platform tiers $2,800 / $12,000 / $48,000 per yr (V) | S1, S2 |
| Splunk On-Call | P: alert routing | P: "scheduling and escalation policies" (V) | N | N | N found | SaaS (U) | $10 / $35 / $45 per user/mo (U, Capterra; another source says $5, so they conflict) | S3, S4 |
| ServiceNow ITOM Event Mgmt | Y: alert rules "automatically generate and link incidents, tasks..." (V) | P: assignment groups (V) | via ServiceNow FSM (below) | N | Now Assist GenAI (V, mentioned) | SaaS **or Private Stack (self-hosted)** (V) | not public | S5, S7 |

### 1b. Field service management (FSM)

| Product | Detect | Decide who | Travel-aware | Verify | Summarize | Deployment | List price | Src |
|---|---|---|---|---|---|---|---|---|
| **Salesforce Field Service** | Y with **Connected Assets**: real-time telemetry, Asset Health Score, actions on "asset failures or error codes" (V) | Y: "assigning the right technician based on skills and location" (V) | **Y**: "street-level, turn-by-turn routing", traffic, ETAs (V) | P: remote actions on failures (V); no evidence gate found | Y: Agentforce job summaries (V) | Cloud SaaS; no on-prem found | Dispatcher **$175**, Technician **$175**, FS Plus **$230**, Agentforce 1 FS **$650** /user/mo; Agentforce for FS add-on $125/user/mo; **Connected Assets $15,000/org/mo** (V) | S8-S11 |
| **Microsoft D365 Field Service** | **Y**: Connected Field Service, where Stream Analytics threshold rules -> IoT alert -> case + work order (V) | Y: characteristics/proficiency, roles, territories, working hours, **scheduling windows** (V) | **Y**: RSO "Minimize total travel time"; historical-traffic travel times, but "doesn't account for real-time disruptions" (V) | P: remote commands (e.g. reboot) via IoT Hub before dispatch (V) | Y: Copilot "work order creation and updates, scheduling, and summarization" (V) | **Cloud only**: on-prem use rights retired 30 Jun 2022 (V) | **$105/user/mo**; Contractor $50; **RSO $30/resource/mo**, all paid yearly (V) | S12-S17 |
| ServiceNow FSM | P: via Event Mgmt / platform workflows (FSM linkage U) | Y: "skills and location", availability, work hours (V docs) | **Y**: travel time via "Google Maps API, straight-line estimates" (V docs) | N | Now Assist (U detail) | SaaS **or Private Stack** with LLMs on customer GPUs (V) | not public | S6, S7 |
| IFS Cloud FSM | P: Falkonry AI anomaly detection, acquired 2023 (U) | Y (U) | Y: "scheduling optimization" (U) | N | IFS.ai; IFS Loops agents from the TheLoops deal, Jun 2025 (U) | Cloud, remote **or on-premise**, "same software" (U; ifs.com returned HTTP 429) | not public | S18-S20 |
| Oracle Field Service | not reviewed | Y: skills (U) | Y: "time-based, self-learning, and predictive routing" (U) | N | not reviewed | Cloud (U) | not public on product pages; a price-list snippet shows $100 and $225 per hosted named user/mo, min 50 (U, conflicting); third-party estimate $90-$300 (U) | S21, S22 |
| ServiceTitan | N (home-services CRM) | P: drag-and-drop dispatch board (V) | not shown | N | not reviewed | Cloud | **not public**: "per-technician pricing", "Request Pricing" (V) | S23 |
| IBM Maximo App Suite (added: on-prem EAM) | Y: Maximo Monitor/Predict in Premium (V) | Y: "MAS Scheduler included"; Schedule Optimizer (V) | not verified | N | Maximo Assist (V, name only) | **On-prem, client-managed cloud, or SaaS** (V) | Essentials SaaS "starting under **$40K/year**" (V) | S24 |

### 1c. CMMS / maintenance / predictive maintenance

| Product | Detect | Decide who | Travel-aware | Verify | Summarize | Deployment | List price | Src |
|---|---|---|---|---|---|---|---|---|
| MaintainX | Y: condition-based triggers; IoT sensor integrations (Premium+); "AI-Powered Anomaly Detection" (V) | P: assignment, not travel-based | N | N | P: MaintainX Assist (V) | Cloud; no on-prem mentioned (V) | Free; Essential **$20** annual / $25 monthly; Premium **$65** / $75; Enterprise custom (V) | S25 |
| UpKeep (+ Edge sensors) | Y: Warning / Out of Range / Incident thresholds; "AI-suggested work orders created directly from insights and alerts" (V) | N: page doesn't say how work is assigned (V) | N | N | not reviewed | Cloud (V, no on-prem mentioned) | Essential **$24**, Premium **$55** /user/mo; higher tiers by quote (V) | S26, S27 |
| Limble | P: IoT integrations on Enterprise only (V) | P: "AI Scheduling Suggestions" on Enterprise (V) | N | N | - | Cloud (V, no on-prem mentioned) | **not public** (price calculator) (V) | S28 |
| Fiix (Rockwell) | P: condition-based triggers on Enterprise (V) | N | N | N | Fiix MAX Q&A assistant (V) | Cloud (V, no on-prem mentioned) | Free; Basic **$45**; Professional **$75** /user/mo; Enterprise custom (V) | S29 |
| Augury | Y: sensors + AI machine-health diagnosis (U detail) | N: hands off to a CMMS work order (V) | N | N | - | Cloud AI platform (U) | not public; sold per machine per year incl. hardware (U) | S30 |

### 1d. Robot fleet operations

| Product | Detect | Decide who | Travel-aware | Verify | Summarize | Deployment | List price | Src |
|---|---|---|---|---|---|---|---|---|
| InOrbit | Y: status rules -> Warning/Error -> incident (V) | P: notifies **Slack / Google Chat / OpsGenie / PagerDuty / webhook** (V) | **N**: docs describe no staff assignment, location or travel (V) | N | "RobOps Copilot" (U) | Cloud; on-prem not found | Free edition with unlimited robots (V, 2021 post, so older than 2022); Standard is per-robot pay-as-you-go (U), no $ figure found | S31, S32 |
| Formant | Y: events on data thresholds (V) | P: Slack / SMS / PagerDuty / webhook; operator "intervention requests" (V) | **N** (V, docs don't mention it) | N | - | Cloud app (V); on-prem not found | **not public** (pricing page 404) | S33 |
| MiR Fleet Enterprise | P: keeps operators updated on obstacles and route disruptions (V) | N | N | N | - | **On-prem Windows Servers** (V) | not public | S34 |
| LocusONE / LocusHub | P: dashboards, predictive work-completion insights (U) | N | N | N | - | (U) | not public (RaaS) | S35 |
| Meili FMS | P: robot task allocation, traffic control (U) | N (robots only) | N | N | - | (U) | not public | S35 |
| SVT Robotics SOFTBOT | P: system-health dashboard across automation systems (U) | N | N | N | - | (U) | not public | S35 |

### 1e. Agentic AI for operations / field service (2024-2026)

| Product | What overlaps | What doesn't | Deployment | Price / funding | Src |
|---|---|---|---|---|---|
| Agentforce for Field Service (Salesforce, Apr 2025) | "proactively and autonomously assign new appointments", summarize jobs (V) | No telemetry-triggered loop or verification in the announcement (V) | Cloud | $125/user/mo add-on (V) | S8, S11 |
| D365 **Scheduling Operations Agent** (preview, doc dated 2026-06-30) | Agent re-optimizes up to 5 technicians' schedules with skills, territories, time windows, predictive travel (V) | Preview, dispatcher-initiated, no real-time traffic (V) | Cloud | in D365 licensing | S16 |
| PagerDuty agents (SRE, Shift, Scribe, Insights) | Triage, context, summaries (V) | Schedule-based routing, no physical dispatch (V) | SaaS | in platform tiers (V) | S1 |
| IFS Loops (TheLoops acquisition, 2025-06-26) | "Industrial AI workforce" agents inside IFS Cloud (U) | Unknown | IFS Cloud (U) | not public | S19 |
| Siemens Industrial Copilot for Operations (2024-11-11) | **Runs entirely on-site** on NVIDIA NIM; maintenance Q&A on operational data (V) | Doesn't choose who goes and doesn't verify the fix (V, not in release) | On-prem IPC bundle | not public | S39 |
| Probook (home services, Fortune 2026-06-23) | AI dispatch/booking: "2,542 jobs in its first month without a single human touching the booking" (V, vendor claim) | Customer calls, not telemetry; homes, not robots | Cloud | raised **$40M** ($34M A by a16z + $6M seed by Sequoia) (V) | S36 |
| Netic (home services) | AI agents book jobs into CRM/FSM (U) | Same as Probook | Cloud | $20M A (Jun 2025) + $23M B (Nov 2025) (U) | S37 |
| ResolveGrid (AI Fund, ex-Xerox CareAR; 2026-05-14) | Agentic repair guidance; "cutting dispatches in half at early customers" (V, vendor claim) | **Does not schedule or dispatch** technicians (V) | Enterprise SaaS | not public | S38 |

---

## 2. Pricing benchmark

| Category | Product / plan | List price | Metric | Status |
|---|---|---|---|---|
| Incident mgmt | PagerDuty Professional | $21 (annual) / $25 (monthly) | per user / month | list price, verified on page |
| Incident mgmt | PagerDuty platform: Starter / Essential / Plus / Ultimate | $2,800 / $12,000 / $48,000 / custom | per year (10 / 20 / 50 / 500 seats) | list price, verified on page |
| Incident mgmt | Splunk On-Call Starter / Growth / Enterprise | $10 / $35 / $45 (another source: $5) | per user / month | unverified (Capterra), conflicting |
| ITOM / FSM | ServiceNow (Event Mgmt, FSM, Private Stack) | - | - | not public |
| FSM | Salesforce Dispatcher / Technician | $175 / $175 | per user / month, annual | list price, verified on page |
| FSM | Salesforce Field Service Plus | $230 | per user / month | list price, verified on page |
| FSM | Salesforce Agentforce 1 Field Service | $650 | per user / month | list price, verified on page |
| FSM | Salesforce Contractor Plus | $80, or $32 per login | per user / month | list price, verified on page |
| FSM add-on | Salesforce Agentforce for Field Service | $125 | per user / month | list price, verified on page |
| FSM add-on | Salesforce **Connected Assets** (telemetry, includes 10,000 assets) | **$15,000** | per org / month | list price, verified on page |
| FSM | Microsoft D365 Field Service | $105 | per user / month, paid yearly | list price, verified on page |
| FSM | D365 Field Service Contractor | $50 | per user / month | list price, verified on page |
| FSM add-on | D365 Resource Scheduling Optimization | $30 | per **resource** / month | list price, verified on page |
| FSM | Oracle Field Service Enterprise | $100 or $225 (min 50 users); third-party $90-$300 | per hosted named user / month | unverified, conflicting |
| FSM | IFS Cloud FSM | - | - | not public |
| FSM | ServiceTitan | - | "per-technician" | not public (verified that the page shows no price) |
| EAM | IBM Maximo Essentials SaaS | "starting under $40K" | per year | list price, verified on page |
| CMMS | MaintainX Essential / Premium | $20 / $65 (annual); $25 / $75 (monthly) | per user / month | list price, verified on page |
| CMMS | UpKeep Essential / Premium | $24 / $55 | per user / month | list price, verified on page |
| CMMS | Fiix Basic / Professional | $45 / $75 | per user / month | list price, verified on page |
| CMMS | Limble | - | calculator | not public |
| PdM | Augury | - | per machine / year incl. hardware (U) | not public |
| Robot ops | InOrbit | Free edition, unlimited robots; Standard per robot, no $ found | per robot | free tier verified (2021 post); paid not public |
| Robot ops | Formant, MiR Fleet, LocusONE, Meili, SVT | - | - | not public |

**Calculation (mine, not sourced). Assumed team: 2 dispatchers + 10 field engineers = 12 users, list prices only:**
- Microsoft: 12 x $105 + 10 x $30 (RSO) = **$1,560/mo ($18,720/yr)**. This excludes Azure IoT Hub, Stream
  Analytics, Service Bus and Logic Apps consumption plus implementation, which I did not price.
- Salesforce closed loop: 12 x $175 + $15,000 (Connected Assets) = **$17,100/mo ($205,200/yr)**. Adding the
  Agentforce for FS add-on for all 12 users adds 12 x $125 = $1,500/mo.
- PagerDuty Professional: 12 x $21 = **$252/mo**. MaintainX Premium: 12 x $65 = **$780/mo**.
- Reading: at list price, a cloud closed loop for a 12-person team costs about $1.6k/mo plus Azure and integration
  (Microsoft) up to about $17k/mo (Salesforce with Connected Assets). A per-site subscription in the low thousands
  per month would sit inside that range. This is my inference, not a sourced figure.

---

## 3. Where the gap is, and where it is NOT

**NOT a gap (don't claim it on stage):**
1. **Travel-aware, skills-aware, deadline-aware assignment.** This is standard FSM. Salesforce: skills, location,
   traffic, ETAs. D365 RSO: characteristics, travel-time minimization, scheduling windows, predictive travel. ServiceNow:
   Google Maps travel time, skills, location, availability. Oracle: self-learning routing (U).
2. **Telemetry -> work order automation.** D365 Connected Field Service documents it end to end: "automate the creation of
   work orders and dispatch technicians when a device needs service". Salesforce Connected Assets, ServiceNow Event
   Management, UpKeep Edge and MaintainX also do it, and Augury pushes work orders into SAP, Maximo, Infor, MaintainX and Limble.
3. **AI agents for scheduling and summaries.** Agentforce for Field Service, the D365 Scheduling Operations Agent, the
   PagerDuty agents, IFS Loops (U), and Probook/Netic in home services.
4. **On-prem by itself.** ServiceNow Private Stack runs LLMs on customer GPUs (28 countries). Maximo runs on-prem, IFS
   has a self-managed option (U), MiR Fleet Enterprise runs on Windows servers, and Siemens' copilot runs on-site.

**IS a gap (defensible, with caveats):**
1. **Robot fleet -> human dispatch.** Robot ops platforms detect robot incidents and notify on-call channels. On-call
   tools route by schedule. FSMs are travel-aware but aren't wired to robot telemetry out of the box. I found no product
   that ships "robot incident -> named field engineer -> ETA -> verified fix" for robot OEMs, RaaS operators, or sites
   with mixed fleets. **This is the wedge.**
2. **Evidence-gated verification.** Incumbents close work orders when the technician says it's done. ShiftLead accepts
   a fix only when post-fix telemetry gives P(success rate >= 80%) >= 95%, and reuses that gate to commission robot
   skills and policies. I did not find this anywhere. Phrase it as "we haven't seen it", not "nobody does it".
3. **The loop as an appliance, with data kept on site.** The incumbents' closed loop is a cloud integration project.
   Their on-prem options are whole platforms bought through an account team (ServiceNow requires a paid workshop) or
   don't dispatch people (Siemens). ShiftLead's difference here is packaging and buyer (mid-size sites, robot OEM
   field-service teams), not a new algorithm.
4. *(Minor)* **Real-time and public-transit travel for shift workers.** D365's predictive travel explicitly excludes
   real-time disruptions, and FSM travel models assume technicians drive. Transit-aware assignment was not found. Don't
   lead with this.

**Revised gap sentence for the deck:** "Enterprise suites can close this loop in their cloud after an integration project.
Robot fleets and mid-size sites don't have that loop, and nobody verifies the fix with evidence."

---

## 4. Positioning statement (one line)

**"ShiftLead is the on-site AI shift supervisor for robot fleets: it turns a robot alarm into the right qualified engineer
on the way with an ETA, and closes the ticket only when the telemetry proves the fix. It runs on one box, and no data
leaves the site."**

## 5. Judge pushback and answers

1. **"Salesforce and Microsoft already do IoT alarm -> work order -> optimized dispatch."**
   Yes, and we use them as our benchmark. Microsoft's loop chains Azure IoT Hub, Stream Analytics, Service Bus, Logic
   Apps, Field Service and RSO, and it is cloud-only (Field Service on-prem was retired in 2022). Salesforce's telemetry
   piece lists at $15,000/org/month before $175 per seat. We ship the loop pre-integrated on one box per site, starting
   with robot fleets, and we add evidence-gated acceptance of the fix. Where a customer already runs an FSM, an adapter
   can push our work orders into it.
2. **"On-prem AI isn't new. ServiceNow Private Stack and Siemens run LLMs on-site."**
   True. Private Stack is the whole ServiceNow platform self-hosted for sovereign customers (defense, government,
   banking), bought through the account team with a paid workshop. Siemens' on-site copilot answers maintenance
   questions. It doesn't decide who goes, track the ETA, or verify the fix. Our differentiator is a closed loop for
   physical operations that a site can run without an IT program. "Local LLM" alone is not the differentiator.
3. **"InOrbit or Formant will just add dispatch, or customers will wire up PagerDuty."**
   Today they hand off to Slack or PagerDuty, and PagerDuty routes by on-call schedule with no location or travel.
   Workforce scheduling with travel time belongs to a different product category (FSM). We should integrate rather than
   compete: they expose webhooks, so ShiftLead can be the webhook target that decides who goes and verifies the fix.
   Risk acknowledged.

---

## 6. Sources

Publication dates are given where the page shows one. Otherwise "undated" (all accessed 2026-10-03).

- **S1** PagerDuty pricing, https://www.pagerduty.com/pricing/, PagerDuty, undated. "$21 / user / mo" (annual),
  "$25 per user / month" (monthly); "$2,800 platform fee per year" (Starter, 10 seats); "$12,000 platform fee per year"
  (Essential, 20 seats); "$48,000 / year" (Plus, 50 seats); agents "Paige (SRE Agent)", "Shift Agent", "Scribe Agent",
  "Insights Agent". (V)
- **S2** PagerDuty Support, "Escalation Policy vs. Schedule", https://support.pagerduty.com/docs/escalation-policy-vs-schedule,
  undated. "escalation policies allow you to connect services to on-call schedules, and they ensure that the right
  people are notified at the right time". The page says nothing about responder location or travel. (V)
- **S3** Splunk On-Call product page, https://www.splunk.com/en_us/products/on-call.html, Splunk (Cisco), undated.
  "Automate all the essentials including scheduling and escalation policies." No price on the page. (V)
- **S4** Capterra, Splunk On-Call pricing, https://www.capterra.com/p/139957/VictorOps/pricing/, 2026. Starter $10,
  Growth $35, Enterprise $45 per user/month. Another secondary source says $5/user/month. (U, secondary, conflicting)
- **S5** ServiceNow docs, "Create an alert management rule",
  https://www.servicenow.com/docs/r/it-operations-management/event-management/create-alert-management-rule.html, undated.
  "Automatically generate and link incidents, tasks, or knowledge articles to alerts." (V)
- **S6** ServiceNow docs, FSM scheduling methods (Xanadu),
  https://www.servicenow.com/docs/r/xanadu/field-service-management/field-service-scheduling/setting-up-scheduling-methods.html,
  undated. "Google Maps API, straight-line estimates" for travel time; "It works based on set criteria like skills and
  location." (V)
- **S7** ServiceNow Community product-launch blog, "Private Stack",
  https://www.servicenow.com/community/product-launch-blogs/private-stack-deploy-the-full-servicenow-ai-platform-on-your/ba-p/3524144,
  2026-04-30. "It delivers the same application software that runs in our commercial cloud, but deployed and operated
  within your own infrastructure."; "Our Private Stack customer base spans 28 countries"; LLMs "on customer-owned GPU
  infrastructure"; "Customers should expect to purchase a workshop from ServiceNow". (V)
- **S8** Salesforce Field Service pricing, https://www.salesforce.com/service/field-service-management/pricing/,
  undated. "$175 USD/User/Month" (Dispatcher; Technician); "$230 USD/User/Month" (Field Service Plus); "$650
  USD/User/Month" (Agentforce 1 Field Service); "$80 user/month or $32/login" (Contractor Plus); Agentforce for Field
  Service "$125/user/month"; Connected Assets "$15,000/org/month". (V)
- **S9** Salesforce asset management / Connected Assets,
  https://www.salesforce.com/service/field-service-management/asset-management/, undated. "Monitor and act on
  comprehensive telemetry data in real-time."; "$15,000 USD/Organization/Month", includes "10,000 connected digital
  assets"; actions "in response to asset failures or error codes". (V)
- **S10** Salesforce route optimization,
  https://www.salesforce.com/service/field-service-management/field-service-route-optimization/, undated.
  "street-level, turn-by-turn routing"; "assigning the right technician based on skills and location"; "precise travel
  estimates and arrival times". (V)
- **S11** Salesforce News, "Agentforce for Field Service deep dive",
  https://www.salesforce.com/news/stories/agentforce-for-field-service-deep-dive/, 2025-04-09. "proactively and
  autonomously assign new appointments"; "summarize jobs, troubleshoot, and optimize scheduling". (V)
- **S12** Microsoft D365 Field Service pricing,
  https://www.microsoft.com/en-us/dynamics-365/products/field-service/pricing, undated. "$105.00 user/month, paid
  yearly"; Contractor "$50.00 user/month, paid yearly"; RSO "$30.00 resources/month, paid yearly"; AI for "work order
  creation and updates, scheduling, and summarization". (V)
- **S13** Microsoft Learn, "How Connected Field Service with IoT Hub works",
  https://learn.microsoft.com/en-us/dynamics365/field-service/connected-field-service-architecture, ms.date
  2026-08-28. "You can also automate the creation of work orders and dispatch technicians when a device needs
  service."; IoT Alert "starts the process of creating a case and a work order"; Stream Analytics "detects faults based
  on threshold rules"; device commands: "reboot them". (V)
- **S14** Microsoft Learn, "Connected Field Service overview",
  https://learn.microsoft.com/en-us/dynamics365/field-service/connected-field-service, ms.date 2025-10-14.
  "technician expertise, availability, and proximity help you optimize resource allocation". (V)
- **S15** Microsoft Learn, "Optimization goals in RSO",
  https://learn.microsoft.com/en-us/dynamics365/field-service/rso-optimization-goal, ms.date 2026-09-03.
  "include historical traffic information ... This option doesn't account for real-time disruptions like road
  maintenance or accidents."; objective "Minimize total travel time"; constraints "Meets required characteristics",
  "Scheduling windows". (V)
- **S16** Microsoft Learn, "Run interactive optimizations (preview)",
  https://learn.microsoft.com/en-us/dynamics365/field-service/soa-interactive-optimizations, ms.date 2026-06-30.
  "Use the Scheduling Operations Agent to make in-the-moment adjustments to up to five technicians' schedules"; "This
  is a preview feature." (V)
- **S17** Microsoft Dynamics 365 blog, https://www.microsoft.com/en-us/dynamics-365/blog/?p=129624, 2021-06-30
  (older than 2022, but describes the current status). "use rights for Dynamics 365 Field Service (on-premises) will be
  retired on June 30, 2022." (V)
- **S18** IFS, deployment options (ifs.com "modern technology" and "IFS Cloud for defense: in the cloud or on-prem"),
  undated. "IFS Cloud can be run as a service from IFS or in a location of your choice including on-premise". (U:
  search snippet; site returned 429)
- **S19** IFS press release, https://www.ifs.com/news/corporate/ifs-acquires-theloops-to-launch-the-industrial-ai-workforce,
  2025-06-26. "launches the Industrial AI workforce". (U: snippet; 429)
- **S20** Secondary sources on IFS acquisitions: Falkonry (Aug 2023, anomaly detection), Poka (Jun 2023, connected
  worker), 7bridges (Aug 2025). (U)
- **S21** Oracle Fusion Cloud Global Price List (PDF),
  https://www.oracle.com/latam/a/ocom/docs/corporate/pricing/oracle-fusion-cloud-global-price-list.pdf. The snippet
  shows Field Service Enterprise Hosted Named User at "$100.00" and "$225.00" per month, min 50. erpresearch.com
  estimates "$90-$300 per user per month". (U: PDF returned 403; figures conflict)
- **S22** Oracle scheduling and routing datasheet,
  https://oracle.com/cx/service/field-service-management/scheduling-routing-specification-datasheet. "time-based,
  self-learning, and predictive routing and scheduling engine". (U)
- **S23** ServiceTitan pricing, https://www.servicetitan.com/pricing, undated. "Our per-technician pricing is designed
  to fit your business and goals, at any size."; tiers show "Request Pricing". (V)
- **S24** IBM Maximo pricing, https://www.ibm.com/products/maximo/pricing, undated. "MAS can be deployed on prem,
  through hyperscalers ... or as SaaS through AWS."; Essentials "Starting under $40K/year"; Premium includes "Maximo
  Monitor, Predict, Assist and Schedule Optimizer". (V)
- **S25** MaintainX pricing, https://www.getmaintainx.com/pricing, undated. "$20 per user*/month billed annually" /
  "$25 billed monthly"; "$65 per user*/month billed annually" / "$75 billed monthly"; "IoT Sensor Integrations";
  "AI-Powered Anomaly Detection". (V)
- **S26** UpKeep pricing, https://upkeep.com/pricing/, undated. Essential "$24/user/month", Premium "$55/user/month";
  Professional/Enterprise "Request a Quote"; "Nova AI". (V)
- **S27** UpKeep Edge, https://upkeep.com/product/edge/, undated. "AI-suggested work orders created directly from
  insights and alerts"; "Warning, Out of Range, and Incident states". (V)
- **S28** Limble pricing, https://limble.com/pricing, undated. No prices shown ("Calculate my price"); Enterprise:
  "IoT Sensor Integrations*", "AI Scheduling Suggestions". (V)
- **S29** Fiix pricing, https://fiixsoftware.com/pricing/, undated. "$45 Per user, per month"; "$75 Per user, per
  month"; Enterprise "Custom Pricing"; Fiix MAX "An AI maintenance assistant". (V)
- **S30** Augury partners, https://www.augury.com/partners/, undated. "Automatically trigger work orders in Infor EAM
  from your machine alerts."; "Trigger repairs from your machines' alerts directly in IBM Maximo". (V) Per-machine
  annual pricing model. (U, secondary)
- **S31** InOrbit developer docs, https://developer.inorbit.ai/docs, undated. "Once a Status changes its value to
  Warning or Error, this can trigger an incident"; "out-of-the-box integrations with Slack, Google Chat, OpsGenie and
  PagerDuty". No staff assignment or travel described. (V)
- **S32** InOrbit blog, https://www.inorbit.ai/blog/free-edition-has-arrived, 2021-09-23 (older than 2022).
  "supporting an unlimited number of robots, for free, forever". (V) Per-robot Standard plan from an inorbit.ai/plans
  snippet. (U; the page returned 404)
- **S33** Formant docs, https://docs.formant.io/docs/incident-management, undated. "send a custom message with
  auto-filled event data as a Slack message, an SMS message, to PagerDuty, or as a webhook". (V) Homepage
  https://formant.ai/: "connects robots, operators, enterprise systems, and AI agents through a governed layer". (V)
  formant.ai/pricing returned 404.
- **S34** MiR Fleet, https://mobile-industrial-robots.com/products/software/mir-fleet, undated. "MiR Fleet Enterprise
  runs on Windows Servers and supports modern virtualization and cloud strategies." (V)
- **S35** LocusONE / LocusHub, Meili FMS, SVT Robotics SOFTBOT: search snippets and secondary press only. (U)
- **S36** Fortune, https://www.fortune.com/2026/06/23/exclusive-this-startup-wants-to-be-the-ai-brain-for-home-services-and-it-just-raised-40-million-from-sequoia-and-a16z/,
  2026-06-23. "a $34 million Series A led by Andreessen Horowitz and a $6 million seed led by Sequoia Capital";
  "booked 2,542 jobs in its first month without a single human touching the booking". (V; the jobs figure is a vendor
  claim)
- **S37** Netic: BuiltIn SF, https://www.builtinsf.com/articles/netic-raises-20m-funding-20250604 (2025-06-04), and
  other coverage of the Nov 2025 Series B. (U)
- **S38** ResolveGrid press release, 2026-05-14 (BusinessWire, https://www.businesswire.com/news/home/20260514354794/en/,
  returned 403). Read via the mirror at
  https://www.01net.it/resolvegrid-launches-agentic-ai-platform-that-cuts-field-service-dispatches-in-half/. "guides
  field service technicians through complex repairs in real time"; "cutting dispatches in half at early customers". (V
  via mirror; vendor claim)
- **S39** Siemens press release,
  https://press.siemens.com/global/en/pressrelease/siemens-drives-ai-adoption-industrial-operations-x-and-nvidia-accelerated-industrial,
  2024-11-11. "The Siemens Industrial Copilot for Operations powered by NVIDIA NIM microservices also runs entirely
  on-site and allows automation and maintenance engineers to make real-time queries about operational and document
  data". (V)

**Not covered / open items:** ServiceNow and IFS list prices (not public). IFS PSO travel details and Oracle
capabilities (sites blocked). The PagerDuty AIOps and Advance add-on prices (not shown on the pricing page).
Brain Corp and Boston Dynamics Orbit, which are robot-as-inspector platforms that push findings into EAM, were not
reviewed in depth.
