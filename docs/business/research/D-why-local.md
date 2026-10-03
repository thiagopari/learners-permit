# Track D: Why local (hardware economics, cloud cost comparison, data regulation)

Researcher: Track D agent. All pages accessed 2026-10-03, about 13:34 to 13:56 ET.
Status labels: **V** = verified (page opened, number seen). **V-sec** = verified, but on a secondary source (news or law firm), not the primary. **U** = unverified (search snippet or secondhand only). **NF** = not found.
Every number I computed myself is marked **CALCULATION**, with its inputs shown.

---

## 0. Bottom line (one paragraph)

The strongest "why local" argument is **legal and operational, not token price**.

- **Token price.** Hosted copies of our exact model (Qwen3.6-35B-A3B) are very cheap: **$1.20 to $5.90 per 1,000 agent calls** with prefix caching. On token cost alone, a $9,007 box takes millions of calls to pay back against hosted open-weight Qwen.
- **Against frontier APIs, the box pays back quickly.** Mid-tier models cost **$13.78 to $17.56 per 1,000 cached calls**, and **$68.50 to $69.40 uncached**. Break-even is about **510k to 650k calls**, which is roughly 36 to 45 days at 10 calls/min, or about a year at 1 call/min.
- **What makes local necessary:**
  - The data ShiftLead needs (where each worker is all day, what they are doing on the premises, OT telemetry) sits under employee-monitoring notice laws (CT, NY, DE), California CPRA sensitive data ("precise geolocation"), and EU worker-surveillance enforcement (the CNIL Amazon warehouse scanner case).
  - In industrial sites, US government OT guidance says to remove OT connections to the public internet.
  - Cloud vendors now charge **+10% for data residency**. On the box, residency costs nothing extra.
  - The box keeps deciding when the WAN is down.

---

## 1. Hardware

| # | Finding | Value | Source (publisher, date) | Exact quote / cell | Status |
|---|---|---|---|---|---|
| H1 | Dell Pro Max with GB10 (FCM1253), US store price, default config | **$9,007.00** | [Dell US store](https://www.dell.com/en-us/shop/desktop-computers/dell-pro-max-with-gb10/spd/dell-pro-max-fcm1253-micro/xcto_fcm1253_usx) (Dell, accessed 2026-10-03). The same price appears on the [Dell work store page](https://www.dell.com/en-us/work/shop/cty/pdp/spd/dell-pro-max-fcm1253-micro) | "Dell Price $9,007.00". Default config: "4TB SSD M.2 2242 PCIe Gen4x4 NVMe TLC SED OPAL", Wi-Fi 7 + BT 5.4, keyboard, mouse, "Basic Hardware Service with Onsite Support After Remote Diagnosis" | V (fetched twice, consistent) |
| H2 | Lower storage configs | 2TB: **$6,557**; 1TB: **$6,177** (CALCULATION) | Same Dell page | "2TB M.2 2230 SSD Gen4x4 (– $2,450.00)", "1TB SSD Gen4x4 TLC (– $2,830.00)". CALCULATION: $9,007 − $2,450 = $6,557; $9,007 − $2,830 = $6,177 | V (deltas); totals are calculated |
| H3 | Memory | 128 GB unified LPDDR5x | Dell page | "128 GB LPDDR5x, up to 8533 MT/s (onboard)" | V |
| H4 | Power supply (Dell) | 280 W | Dell page | "280W USB-C AC Adapter" | V |
| H5 | Other Dell specs | DGX OS 7; ConnectX-7 (2x200G QSFP); 10GbE; 150 x 150 mm; 1.31 kg | Dell page | "NVIDIA DGX OS 7"; "ConnectX-7 Smart NIC (2x 200G QSFP ...)"; "1 Network (RJ-45, 10GbE)"; "Width: 5.90 in. (150.00 mm) Depth: 5.90 in. (150.00 mm)"; "2.89 lb (1.31 kg)" | V |
| H6 | FP4 performance | Up to 1 PFLOP FP4 | [NVIDIA DGX Spark page](https://www.nvidia.com/en-us/products/workstations/dgx-spark/) (NVIDIA, accessed 2026-10-03). The Dell page does **not** list FP4 performance | "Up to 1 petaFLOP of AI performance at FP4 precision" | V (NVIDIA page; same GB10 chip) |
| H7 | Model size, power, positioning (NVIDIA) | Inference up to 200B params; 240 W PSU; GB10 TDP 140 W | NVIDIA DGX Spark page | "inference with AI models up to 200 billion parameters"; "240 Watts"; "140 W"; "build agents that run persistently and privately, without cloud dependency"; "built to run always-on agent workloads" | V |
| H8 | NVIDIA DGX Spark price | **$4,699** (was $3,999) | [NVIDIA Developer Forum, "2/23/2026 Price Change Announcement"](https://forums.developer.nvidia.com/t/2-23-2026-price-change-announcement/361713) (NVIDIA staff, 2026-02-25) | "$3,999" to "$4,699"; "The price adjustment reflects industry wide memory supply constraints." | V |
| H9 | Earlier Dell GB10 prices (conflict) | $4,139.34; "$3,999 MSRP" | Search snippet citing videocardprices.com (date unknown) | n/a | U (likely stale; does not match today's Dell page) |
| H10 | US commercial electricity price | Jul 2026: **14.53 ¢/kWh**; 2025 average: **13.41 ¢**; 2026 YTD (Jan to Jul): **13.97 ¢** | [EIA Electric Power Monthly, Table 5.3](https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_3) (EIA, released 2026-09-24) | Commercial cells "14.53" (July 2026), "13.41" (2025), "13.97" (YTD 2026) | V |
| H11 | Instantaneous GPU power on this box | 13.03 W | `nvidia-smi` (read-only query) on this GB10, 2026-10-03 ~13:50 | "NVIDIA GB10, 13.03 W" | Measured once. GPU only, not wall power, not under load. **Do not use as a typical figure.** |

**Conflict to flag.** Today's Dell configured price ($9,007 with 4TB SED) is almost twice NVIDIA's DGX Spark Founders Edition MSRP ($4,699). NVIDIA attributes 2026 price rises to memory shortages. Before putting a box price on a slide, re-check the Dell configurator live, or say "about $4.7k to $9k depending on vendor and configuration".

### CALCULATION: annual electricity cost, one box running 24/7 (8,760 h)

| Assumed draw | kWh/yr | at 14.53 ¢ (Jul 2026) | at 13.41 ¢ (2025 avg) |
|---|---|---|---|
| 280 W (Dell adapter rating; upper bound, the box will not draw this continuously) | 2,452.8 | **$356/yr** | $329/yr |
| 240 W (NVIDIA DGX Spark PSU rating) | 2,102.4 | $305/yr | $282/yr |
| 140 W (GB10 TDP; a sustained-load proxy, not measured at the wall) | 1,226.4 | **$178/yr** | $164/yr |

Formula: W × 8,760 h ÷ 1,000 × $/kWh. These are US national commercial averages. Massachusetts and other high-cost states were not fetched (NF), so this is not a Boston-specific number.

**Summary: power is at most about $165 to $360 per year per site.** That is noise next to cloud API bills for frontier models.

---

## 2. Cloud LLM API pricing (official pages, checked 2026-10-03)

All prices are USD per 1M tokens, standard/on-demand tier, short context.

| Provider | Model | Input | Cached input | Output | URL | Status / notes |
|---|---|---|---|---|---|---|
| OpenRouter (listing price) | qwen/qwen3.6-35b-a3b | $0.15 | $0.05 | $1.00 | [openrouter.ai/qwen/qwen3.6-35b-a3b](https://openrouter.ai/qwen/qwen3.6-35b-a3b) (data from [models API](https://openrouter.ai/api/v1/models)) | V. API JSON: `"prompt": "0.00000015", "completion": "0.000001", "input_cache_read": "0.00000005"`. Model created 2026-04-27 |
| OpenRouter (cheapest endpoint) | same, routed to Darkbloom (fp4) | $0.05 | $0.025 | $0.70 | [endpoints API](https://openrouter.ai/api/v1/models/qwen/qwen3.6-35b-a3b/endpoints) | V. 9 third-party endpoints: Darkbloom, AkashML, DeepInfra, Venice, Parasail, AtlasCloud, Phala, SiliconFlow, CoreWeave. Range: input $0.05 to $0.25, output $0.70 to $1.80 |
| OpenRouter (highest-output endpoint) | same, routed to SiliconFlow (fp8) | $0.24 | $0.15 | $1.80 | endpoints API | V |
| DeepInfra | Qwen/Qwen3.6-35B-A3B (fp8) | $0.10 | $0.10 (no discount) | $0.95 | [deepinfra.com/Qwen/Qwen3.6-35B-A3B](https://deepinfra.com/Qwen/Qwen3.6-35B-A3B) | V. Matches OpenRouter's DeepInfra endpoint |
| Fireworks | size tier "MoE up to 56B parameters" (applies to Qwen3.6-35B-A3B if served) | $0.50 | none | $0.50 | [docs.fireworks.ai/serverless/pricing](https://docs.fireworks.ai/serverless/pricing) | V (tier). "These size-based prices apply uniformly to input and output (no separate cached-input rate)". Whether Qwen3.6-35B-A3B is actually served serverless on Fireworks: **NF** (not confirmed) |
| Together AI | Qwen3.6-35B-A3B | not offered serverless | n/a | n/a | [together.ai/pricing](https://www.together.ai/pricing) | V. The model appears only in the **fine-tuning** table ("Qwen3.6 35B A3B, $1.05, $2.62, $4.00" = SFT, DPO, minimum charge). No serverless 30B/35B-A3B Qwen listed |
| Together AI (reference only; different model) | Qwen3.8 Flash | $0.09 | not listed | $0.28 | same | V. Shown only as Together's cheapest serverless Qwen. **Not the same model** |
| Alibaba Cloud Model Studio, International (Singapore) | qwen3.6-35b-a3b | $0.375 | not confirmed | $2.25 | [Model Studio pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing) (Last Updated Oct 03, 2026) | V. Cell: "qwen3.6-35b-a3b, International, 0<Token≤256K, $0.375, $2.25, $2.25, 1 million tokens" (free quota) |
| Alibaba Cloud Model Studio, US (Virginia) | qwen3.6-35b-a3b | $0.248 | not confirmed | $1.485 | same | V. Implicit cache is "typically billed at 20% of the standard input token price" ([Context Cache doc](https://www.alibabacloud.com/help/en/model-studio/context-cache), updated 2026-09-28), but this model is not named in the supported list, so cached price is **not confirmed** |
| Anthropic | Claude Haiku 4.5 (small) | $1 | $0.10 | $5 | [platform.claude.com pricing](https://platform.claude.com/docs/en/about-claude/pricing) | V |
| Anthropic | Claude Sonnet 5.5 (mid) | $2 | $0.20 | $10 | same | V. 5-minute cache write $2.50; 1-hour cache write $4 |
| Anthropic | Claude Opus 5.5 (top, generally available) | $4 | $0.20 | $20 | same | V. 5-minute cache write $5. "Cache hits ... on Claude Opus 5.5 are priced at 0.05x" |
| Anthropic | Claude Fable 5.1 (highest-priced GA tier) | $10 | $0.25 | $50 | same | V |
| OpenAI | gpt-6-luna (small) | $0.10 | $0.01 | $0.50 | [developers.openai.com/api/docs/pricing](https://developers.openai.com/api/docs/pricing) | V (raw HTML table). Cache writes $0.125 |
| OpenAI | gpt-6.1-sol (mid) | $2.00 | $0.10 | $10.00 | same | V. Cache writes $2.50 |
| OpenAI | gpt-6-astra (flagship) | $10.00 | $1.00 | $50.00 | same | V. Cache writes $12.50. Long context: $20 input / $75 output |
| Google | Gemini 3.8 Flash | $0.75 (to 2026-12-31); **$1.50 from 2027-01-01** | $0.075, then $0.15 | $3.75, then **$7.50** | [ai.google.dev pricing](https://ai.google.dev/gemini-api/docs/pricing) (last updated 2026-10-01) | V (WebFetch; raw curl was redirected). Cache storage "$0.50 / 1,000,000 tokens per hour" |
| Google | Gemini 3.1 Pro Preview | $2.00 (≤200k) | $0.20 | $12.00 | same | V. Cache storage "$4.50 / 1,000,000 tokens per hour" |

**Data residency costs extra in the cloud (useful for the slide):**

- **OpenAI:** "Regional processing (data residency) endpoints are charged a 10% uplift for models released on or after March 5, 2026, that are eligible for data residency." **V**
- **Anthropic:** "specifying US-only inference through the `inference_geo` parameter incurs a 1.1x multiplier on all token pricing categories". Bedrock and Google Cloud regional endpoints: "10% premium over global endpoints". **V**

**Caveats:**

- Claude 4.7 and later use a tokenizer that "produces approximately 30% more tokens for the same text" than earlier Claude tokenizers (Anthropic page). Token counts differ by tokenizer, so a 32k-token Qwen prompt is not exactly 32k tokens elsewhere. **The calculations below do not adjust for this.**
- The cheapest OpenRouter prices come from routing to small third-party hosts (Darkbloom, Venice, Phala, and so on). Cheapest-token routing and data governance pull in opposite directions.

---

## 3. CALCULATION: cloud cost per 1,000 agent calls

**Inputs**
- 32,000 prompt tokens and 450 output tokens per call (from the brief).
- Per 1,000 calls: 32.0M input tokens and 0.45M output tokens.

**Formulas**
- **No cache:** 32 × input + 0.45 × output.
- **With cache (ASSUMPTION: 90% of prompt tokens are prefix-cache hits):** 3.2 × input + 28.8 × cached + 0.45 × output.

**What the cached figure ignores**
- **Cache-write premiums.** These are negligible if calls arrive within the cache TTL. If calls are more than 5 minutes apart, Anthropic re-writes the cache on every call at 1.25x input. Example: Sonnet 5.5 would then cost about **$82.90 per 1,000 calls**, worse than no caching.
- **Gemini cache storage.** CALCULATION for keeping a 28.8k-token prefix cached 24/7: 0.0288M × $4.50/hr × 8,760 h = **about $1,135/yr** for Gemini 3.1 Pro, and about $126/yr for Flash. This applies to explicit caching only; implicit-cache billing was not checked.

**Replace the 90% hit rate with the measured vLLM prefix-cache hit rate from our own logs (not read here).**

| Provider | Model | No cache, $/1,000 calls | 90% cached, $/1,000 calls | CALC: break-even calls vs $9,007 box (cached) | Days to break even at 1,440 calls/day (1/min) | at 14,400/day (10/min) |
|---|---|---|---|---|---|---|
| OpenRouter (listing) | Qwen3.6-35B-A3B | $5.25 | $2.37 | 3.80M | 2,639 | 264 |
| OpenRouter (cheapest endpoint) | Qwen3.6-35B-A3B | $1.92 | $1.20 | 7.54M | 5,234 | 523 |
| OpenRouter (SiliconFlow) | Qwen3.6-35B-A3B | $8.49 | $5.90 | 1.53M | 1,061 | 106 |
| DeepInfra | Qwen3.6-35B-A3B | $3.63 | $3.63 (no discount) | 2.48M | 1,724 | 172 |
| Fireworks (tier) | Qwen3.6-35B-A3B if served | $16.23 | $16.23 (no cached rate) | 0.56M | 386 | 39 |
| Alibaba, International | qwen3.6-35b-a3b | $13.01 | $13.01 (cache not confirmed) | 0.69M | 481 | 48 |
| Alibaba, US (Virginia) | qwen3.6-35b-a3b | $8.60 | $8.60 (cache not confirmed) | 1.05M | 727 | 73 |
| Together (reference, different model) | Qwen3.8 Flash | $3.01 | $3.01 | 3.00M | 2,081 | 208 |
| Anthropic | Claude Haiku 4.5 | $34.25 | $8.33 | 1.08M | 751 | 75 |
| Anthropic | Claude Sonnet 5.5 | $68.50 | $16.66 | 0.54M | 375 | 38 |
| Anthropic | Claude Opus 5.5 | $137.00 | $27.56 | 0.33M | 227 | 23 |
| Anthropic | Claude Fable 5.1 | $342.50 | $61.70 | 0.15M | 101 | 10 |
| OpenAI | gpt-6-luna | $3.43 | $0.83 | 10.8M | 7,509 | 751 |
| OpenAI | gpt-6.1-sol | $68.50 | $13.78 | 0.65M | 454 | 45 |
| OpenAI | gpt-6-astra | $342.50 | $83.30 | 0.11M | 75 | 8 |
| Google | Gemini 3.8 Flash (2026 price) | $25.69 | $6.25 | 1.44M | 1,001 | 100 |
| Google | Gemini 3.8 Flash (2027 price) | $51.38 | $12.49 | 0.72M | 501 | 50 |
| Google | Gemini 3.1 Pro Preview | $69.40 | $17.56 | 0.51M | 356 | 36 |

**Worked example (Sonnet 5.5, cached).** 3.2 × $2 + 28.8 × $0.20 + 0.45 × $10 = $6.40 + $5.76 + $4.50 = **$16.66** per 1,000 calls. Break-even: $9,007 ÷ $0.01666 = 540,636 calls.

**CALCULATION: illustrative annual cloud spend (90% cached).** Call volumes are assumptions; replace them with ShiftLead's measured call rate.

| Model | 525,600 calls/yr (1/min) | 5,256,000 calls/yr (10/min) |
|---|---|---|
| Qwen3.6-35B-A3B on OpenRouter (listing) | $1,246 | $12,457 |
| Qwen3.6-35B-A3B on DeepInfra | $1,907 | $19,066 |
| qwen3.6-35b-a3b on Alibaba US | $4,522 | $45,219 |
| gpt-6.1-sol | $7,243 | $72,428 |
| Claude Sonnet 5.5 | $8,756 | $87,565 |
| Gemini 3.1 Pro Preview (excluding cache storage) | $9,230 | $92,295 |
| Claude Opus 5.5 | $14,486 | $144,855 |
| gpt-6-astra | $43,782 | $437,825 |

Local box running costs: $6,177 to $9,007 one-time (H1, H2) plus about $165 to $360/yr of power (section 1). Not included: support, admin time, and any capacity limit of one box. Throughput was not measured in this track.

**How to read this honestly**
1. **Against hosted copies of the same open model, local does NOT win on token price** unless volume is high. Payback is 1.5M to 7.5M calls.
2. **Against frontier mid-tier APIs** (the realistic choice for a team that does not self-host), the box pays back in about 0.5M calls. Sending the 32k-token prompt **uncached**, frontier mid-tier costs 4 to 5x more again.
3. **Cloud prices move.** Gemini 3.8 Flash doubles on 2027-01-01 (V). The box price is fixed once bought.

---

## 4. Why data must stay on site: regulation by industry

| # | Industry / jurisdiction | Rule | Exact quote | Why it matters for ShiftLead | Does local help? | Source (publisher, date) | Status |
|---|---|---|---|---|---|---|---|
| R1 | All employers, Connecticut | Conn. Gen. Stat. §31-48d | "Electronic monitoring" means "the collection of information on an employer's premises concerning employees' activities or communications by any means other than direct observation, including the use of a computer, telephone, wire, radio, camera, electromagnetic, photoelectronic or photo-optical systems". Employers "shall give prior written notice to all employees who may be affected". Penalty "five hundred dollars for the first offense, one thousand dollars for the second offense and three thousand dollars for the third and each subsequent offense." | Tracking where workers are and what they do on the premises (badges, RTLS, scanners, cameras) is "electronic monitoring". | **Partly.** Notice is still required. Keeping data on site limits who else holds it. | [CGA chapter 557](https://www.cga.ct.gov/current/pub/chap_557.htm) (CT General Assembly, statutes revised to Jan 1, 2026) | V |
| R2 | All employers, New York | NY Civil Rights Law §52-c*2 | Covers "Any employer who monitors or otherwise intercepts telephone conversations or transmissions, electronic mail or transmissions, or internet access or usage". Notice "upon hiring", "acknowledged by the employee", posted "in a conspicuous place". Penalties $500 / $1,000 / $3,000. | Covers our agent reading staff messages (Discord). **Caveat: the text does not mention GPS or location tracking.** | **No.** It is a notice duty either way. | [nysenate.gov CVR 52-C*2](https://www.nysenate.gov/legislation/laws/CVR/52-C*2) (NY Senate, revision 2022-05-13) | V |
| R3 | All employers, Delaware | 19 Del. C. §705 | Covers "telephone conversation or transmission, electronic mail or transmission, or Internet access or usage". Notice daily, or one-time with acknowledgement. "$100 for each such violation". | Same as R2. | **No** (notice duty). | [delcode.delaware.gov Title 19 ch. 7](https://delcode.delaware.gov/title19/c007/sc01/index.html) (State of Delaware) | V |
| R4 | All employers, California | CCPA/CPRA (Cal. Privacy Protection Agency FAQ) | Employee exemptions "expired on December 31, 2022". Sensitive personal information includes "your precise geolocation". ADMT regulations "became effective January 1, 2026. Certain compliance deadlines are phased beginning in 2027 and 2028." | Worker location is **sensitive PI**. Automated assignment of people may fall under ADMT rules. | **Partly.** Fewer processors and transfers to disclose. Rights and notices still apply. | [cppa.ca.gov/faq.html](https://cppa.ca.gov/faq.html) (CPPA, accessed 2026-10-03) | V |
| R5 | Warehousing, EU (France) | GDPR enforcement: CNIL vs Amazon France Logistique | CNIL fined **€32M** (Dec 2023) over warehouse scanner indicators, including one flagging an item "scanned in less than 1.25 seconds after the previous one" and inactivity tracking. The Conseil d'État (23 Dec 2025, no. 492830) **confirmed the fine but cut it to €15M**. | The closest precedent to "track every worker's activity in a warehouse". Shows regulators will act on fine-grained worker telemetry. | **Partly.** Locality helps with minimisation and retention control, but proportionality rules still apply. | CNIL page now "no longer available" (CNIL de-publishes named sanctions). [Mind RH (2026-03-03)](https://www.mind.eu.com/rh/en/article/amazon-france-logistique-employee-surveillance-fine-halved-on-appeal/); CNN and others (Jan 2024) | V-sec |
| R6 | All employers, EU | GDPR guidance on location tracking: Article 29 WP Opinion 2/2017 on data processing at work | not fetched | The standard citation for proportionality of vehicle and device tracking of employees. | n/a | Not opened in this sprint. **Also older than 2022** | NF / U |
| R7 | All employers, EU | EU AI Act (Reg. 2024/1689), Annex III point 4(b) | High-risk includes AI used "to allocate tasks based on individual behaviour or personal traits or characteristics or to monitor and evaluate the performance and behaviour of persons in such relationships." Timing: a provisional Digital Omnibus deal moves stand-alone Annex III obligations to **2 December 2027**. | ShiftLead "decides who" goes. If that uses behaviour or traits, it is likely high-risk in the EU. **Local deployment does NOT exempt it.** Human oversight, logging, and "code enforces, model explains" are the mitigations. | **No** (classification is by use, not location). | [artificialintelligenceact.eu Annex III](https://artificialintelligenceact.eu/annex/3/) (reproduces the OJ text); [Gibson Dunn (2026-05-27)](https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/) | V (text); V-sec (timing; OJ publication not verified) |
| R8 | Industrial / critical infrastructure, US | CISA, FBI, EPA, DOE: "Primary Mitigations to Reduce Cyber Threats to OT" | "Remove OT connections to the public internet"; "OT devices are easy targets when connected to the internet"; "Segment IT and OT networks"; "practice and maintain the ability to operate OT systems manually." | A cloud-LLM agent needs an outbound path from OT data to the internet. A box on the plant LAN does not. | **Yes.** This is the core argument. | [CISA](https://www.cisa.gov/resources-tools/resources/primary-mitigations-reduce-cyber-threats-operational-technology) (2025-05-06) | V |
| R9 | Industrial | IEC 62443 (zones and conduits, 62443-3-2) | not fetched | Standard OT segmentation model. | n/a | Not opened in this sprint | NF |
| R10 | Electric utilities | NERC CIP-004-7 / CIP-011-3 (BCSI in the cloud allowed from 2024-01-01). Project 2023-09: cloud for CIP systems still in progress | not opened | Cloud is allowed for *information about* BES systems with controls. Broader cloud use for CIP systems is still being written. | **Yes** (avoids an open standards question) | NERC [Project 2023-09 SAR](https://nerc.com/pa/Stand/202309RiskMgmtforThirdPartYCloudServices_DL/2023-09_Cloud%20Services%20SAR_redline%20final_121024.pdf) (not opened) | U |
| R11 | Defense manufacturing | DFARS 252.204-7012 (MAY 2024) | "If the Contractor intends to use an external cloud service provider to store, process, or transmit any covered defense information ... the cloud service provider [must meet] security requirements equivalent to ... (FedRAMP) Moderate baseline" | Defense-supplier plants: shop-floor data that is covered defense information cannot go to an arbitrary LLM API. | **Yes** (no external CSP) | [acquisition.gov DFARS 252.204-7012](https://www.acquisition.gov/dfars/252.204-7012-safeguarding-covered-defense-information-and-cyber-incident-reporting.) (page current as of 2026-09-23) | V |
| R12 | Healthcare | HIPAA 45 CFR 164.514(b)(2)(i), Safe Harbor identifiers | "(B) All geographic subdivisions smaller than a State, including street address, city, county, precinct, zip code, and their equivalent geocodes"; "(M) Device identifiers and serial numbers"; "(Q) Full face photographic images and any comparable images" | When device, location, or video data is linked to patients (hospital logistics, home-care field visits), it stays identifiable PHI. | **Partly.** A cloud LLM vendor would be a business associate needing a BAA. HHS's cloud guidance page returned 403, so that point is not verified. | [Cornell LII 45 CFR 164.514](https://www.law.cornell.edu/cfr/text/45/164.514) | V (identifiers); U (BAA guidance) |

---

## 5. Enterprise sentiment and evidence of on-prem preference

| # | Finding | Exact quote / number | Source (publisher, date) | Commissioned by | Status |
|---|---|---|---|---|---|
| S1 | Privacy is the top GenAI inhibitor | "Data privacy (57%) and trust and transparency (43%) concerns are the biggest inhibitors of generative AI" (n = 8,584 IT professionals, Nov 2023). Nuance: for AI in general, the top barrier was "limited AI skills and expertise (33%)" | [IBM Newsroom](https://newsroom.ibm.com/2024-01-10-Data-Suggests-Growth-in-Enterprise-Adoption-of-AI-is-Due-to-Widespread-Deployment-by-Early-Adopters) (2024-01-10) | IBM (Morning Consult) | V |
| S2 | Local storage seen as safer | "90% of organizations see local storage as inherently safer". In the same study, "91% ... trust global providers for better data protection" (both held at once). "64% of respondents worry about inadvertently sharing sensitive information publicly or with competitors"; "Nearly half admit to inputting personal employee or non-public data into GenAI tools" (2,600 privacy and security pros, 12 countries) | [Cisco Newsroom, 2025 Data Privacy Benchmark](https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2025/m04/cisco-2025-data-privacy-benchmark-study-privacy-landscape-grows-increasingly-complex-in-the-age-of-ai.html) (2025-04-02) | Cisco | V |
| S3 | AI workloads moving off public cloud | "66% of respondents said their organizations moved AI workloads from public cloud back to private cloud or on-premises infrastructure during the past year". Top driver: "Data security, governance, and compliance requirements (42%)"; "Supporting real-time or edge-based AI capabilities (35%)"; "Eighty-four percent said AI workloads have increased infrastructure costs." (n = 1,500, 9 markets) | [Campus Technology](https://campustechnology.com/articles/2026/08/18/survey-organizations-moving-ai-workloads-away-from-public-cloud.aspx) (2026-08-18), reporting a Wakefield Research survey | **Cloudera** (vendor) | V-sec |
| S4 | On-prem inference cost vs cloud | On-prem "up to 2.6x" / "62%" cheaper than public cloud IaaS and "4.1x" / "75%" cheaper than API-based services. Per the search summary: a 70B model over 4 years vs a GPT-4o API | [ESG analyst paper](https://www.delltechnologies.com/asset/en-uk/solutions/business-solutions/briefs-summaries/esg-inferencing-on-premises-with-dell-technologies.pdf) (2025-04-30) | **Dell Technologies** | V (headline); U (model size and horizon) |
| S5 | Private cloud for AI and repatriation | 56% run AI workloads in private cloud vs 41% public; 69% considering repatriation, one-third already done | Broadcom Private Cloud Outlook 2025 (press release blocked our fetch) | **Broadcom / VMware** | U |
| S6 | Share of AI workloads on-prem | "49.9%" of AI workloads on-prem or private cloud | IDC (Dec 2025), search snippet only | n/a | U |
| S7 | Connectivity gaps at remote sites | "roughly 10.5 million people still lack access to fixed terrestrial advanced telecommunications capability at speeds of 100/20 Mbps (if satellite service is not taken into account)" | [FCC 2026 Section 706 Report, FCC 26-55, ¶135](https://docs.fcc.gov/public/attachments/FCC-26-55A1.txt) (adopted 2026-08-13, released 2026-08-14) | US government | V |
| S8 | Warehouse-specific connectivity data | A survey quantifying Wi-Fi or WAN problems at warehouses was not found in the time box | n/a | n/a | NF |

---

## 6. Resilience: the agent keeps working when the site's internet is down

**Architecture (our argument, not a sourced claim).** All of the decision loop runs on the GB10 on the site LAN:

- the detectors and event engine;
- ticket state;
- people, skills and travel-time assignment;
- the trust gate;
- Qwen3.6-35B-A3B served by vLLM.

A WAN cut does not stop detection or decisions. A cloud-LLM design loses its "brain" whenever either the site's internet or the LLM provider is down.

**Honest gap: Discord is a cloud channel.** During a WAN outage, alerts need a local fallback, such as a LAN dashboard, an on-site display or radio, or an SMS/cellular modem. The state and decisions survive and catch up when the link returns. Say this before a judge does.

| # | Finding | Quote | Source | Status |
|---|---|---|---|---|
| X1 | Connectivity-related outages are rising | "Outages linked to fiber and connectivity issues are rising and more likely to result in extended disruptions." Also: "57% of respondents said their most recent major outage cost more than $100,000"; "1 in 5 reported costs exceeding $1 million". **These are data-center / IT-service outages, not site internet outages.** | Uptime Institute Annual Outage Analysis 2026 press release (13 May 2026), reprinted by [ITWeb](https://itweb.africa/article/uptime-announces-annual-outage-analysis-report-2026/WnxpEv4Y6837V8XL). The 57% figure was also reported for Uptime's 2025 survey, so the 2026 release may be citing it | V-sec |
| X2 | Even top LLM APIs are not 100% available | OpenAI status page: APIs "99.96 % uptime" (window as displayed; typically 90 days). CALCULATION: 0.04% × 8,760 h ≈ **3.5 h/yr** of API unavailability, before counting the site's own WAN | [status.openai.com](https://status.openai.com) (checked 2026-10-03) | V (figure); window not confirmed |
| X3 | Guidance to be able to run without the network | "practice and maintain the ability to operate OT systems manually" | CISA et al. (2025-05-06), as R8 | V |
| X4 | Frequency/cost of business internet outages at sites (survey) | n/a | n/a | NF in the time box |

---

## 7. Conflicts, caveats, gaps

- **Dell price.** $9,007 (today's Dell configurator, 4TB SED) vs $4,699 (NVIDIA DGX Spark FE) vs older $3,999 to $4,139 figures. Give a range, or re-check live before quoting.
- **Cost story.** Hosted open-weight Qwen beats the box on token price. Frontier APIs do not. **Do not claim "local is cheaper than cloud" without saying "than frontier APIs".**
- **Cisco S2** shows people see local storage as safer *and* trust global providers. Use both or neither.
- **IBM S1** is from a Nov 2023 survey (published 2024). Recent surveys found are vendor-commissioned (Cloudera, Dell/ESG, Broadcom). Label them as such.
- **Local deployment does not remove legal duties.** Notice duties (CT, NY, DE), CPRA rights, and EU AI Act high-risk classification still apply. Local reduces transfers, processors and third-party exposure. It does not make monitoring lawful.
- **Gaps:**
  - Not fetched: IEC 62443 text, WP29 Opinion 2/2017, the HHS cloud guidance (403), and the NERC SAR.
  - Not found: Massachusetts electricity price, warehouse connectivity survey data, business internet-outage frequency survey data.
  - Not confirmed: whether Fireworks serves Qwen3.6-35B-A3B serverless, and Alibaba cache support for this model.

---

## 8. Recommendations for the "why local" slide (for Dell and NVIDIA judges)

1. **Lead with "the data can't leave," not "tokens are cheaper."**
   - Headline: *"ShiftLead's fuel is where your people are and what your machines are doing. That data is regulated, and it lives inside the site perimeter."*
   - Three proof points with sources:
     - **CT §31-48d:** on-premises activity tracking is "electronic monitoring".
     - **CPRA:** "precise geolocation" is sensitive personal information.
     - **CISA (May 2025):** "Remove OT connections to the public internet."
   - Add DFARS 7012 (FedRAMP-Moderate cloud only) as the manufacturing closer.
2. **Show the cost slide against what customers would actually buy.**
   - "A 32k-token agent call on a mid-tier frontier API costs **$13.78 to $17.56 per 1,000 calls even with caching** ($68.50 to $69.40 without). One Dell Pro Max GB10 pays for itself after **about 0.5M calls**: roughly 5 to 6 weeks at 10 calls/min. Power is about **$165 to $360/yr**."
   - Footnote that hosted open-weight Qwen is cheaper per token. The appliance wins on data control and fixed cost, not on undercutting open-weight API prices.
3. **Name the hidden cloud taxes.**
   - **+10%** for data-residency endpoints (OpenAI) and **1.1x** for US-only inference (Anthropic).
   - Gemini Flash prices **double on 1 Jan 2027**.
   - The cheapest hosted Qwen is reached by routing across **9 third-party hosts**.
   - Local means residency by default, a fixed price, and one known processor (the customer).
4. **Resilience line:** *"Internet down ≠ operations down."*
   - Detection, assignment, trust gate and the LLM all run on the box.
   - Cite Uptime 2026 ("fiber and connectivity issues are rising") and the fact that even OpenAI's API shows 99.96% uptime (about 3.5 h/yr).
   - Pre-empt the Discord question with the local-fallback channel.
5. **Tie it to the GB10 story and to compliance by design.**
   - Use NVIDIA's own words: GB10 runs "always-on agent workloads ... persistently and privately, without cloud dependency", with 128 GB unified memory and up to 1 PFLOP FP4 in a 150 mm box.
   - Then show that ShiftLead adds what regulators ask for: worker-notice templates in each industry pack, audit logs, and human-in-the-loop "code enforces, model explains". This answers the EU AI Act Annex III(4)(b) "task allocation / monitoring" high-risk question instead of hiding it.
