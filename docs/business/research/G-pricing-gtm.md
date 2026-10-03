# Track G: Business model analogs, pricing and go-to-market

Track G research for the ShiftLead pitch. Researched 2026-10-03, time-boxed to about 20 minutes. Follows BRIEF.md.

**Status labels.**
- **Verified:** I opened the page or filing, or queried the official API, and saw the number. Where WebFetch summarized a page, the number shown was on the fetched page.
- **Unverified:** I saw the number only in a search snippet or a secondhand page.
- **Secondary:** the page was opened, but the publisher is not the primary source.

**Calculations.** Every calculation is labeled CALC and shows its inputs. Nothing in the PROPOSAL section is a sourced fact unless it cites a finding number (F#).

---

## Bottom line

1. **The model has strong precedent.** Samsara and Motive are both "sticky hardware + recurring software" businesses. Both price **per asset, per application/product**, on **3-5 year terms**, and include the device in the subscription.
   - Samsara: $2.125B ARR, +30% YoY. 77-78% gross margin. 3,194 customers above $100K ARR in its 10-K, and 3,605 at Q2 FY27 per a secondary source.
   - Motive: $501M ARR, 70% gross margin. NDR of 110% for core customers and 126% for large customers. 70% of its ARR now comes from outside its original vertical. That is the land, expand, new-vertical pattern ShiftLead wants.
2. **Recommended price (PROPOSAL):** a **site plan at $400 per site per month**, with the **Dell Pro Max GB10 bought through Dell**.
   - The site plan includes the core, 1 industry pack, up to 25 monitored assets and unlimited technicians. It runs on a 36-month term.
   - Add-ons: +$150 per extra pack, and +$15 per asset above 25.
   - $400 is 9.5% of a dispatcher's median monthly wage (BLS May 2025). At 20 robots per site it is $20 per robot per month, which is 1.0-2.3% of a robot's RaaS fee.
3. **Example: a robotics company with 25 sites, 500 robots and 15 field engineers.**
   - Software ACV is **$120,000**, and the 3-year contract value is $360,000.
   - **Hardware revenue to Dell is $154,425-$225,175** one-time, at dell.com list price.
   - The software alone breaks even if it saves about **2.4 supervisor-hours per site per week**. Including the Dell box amortized over 3 years, the figure is 3.4-3.9 hours.
4. **The honest risk.** At today's dell.com list price ($6,177-$9,007), the GB10 costs **1.3-1.9x a site's first-year software fee**.
   - Under conservative wage-only assumptions, the all-in 3-year ROI is only about 0.9-1.2x.
   - The pitch should therefore target sites where at least one of these holds:
     - the box also does other work (robot policies, video);
     - uptime is contractually priced;
     - there are many assets or engineers per box.
   - It should also keep hardware on Dell's books, not ShiftLead's, to protect software margins.
5. **Channel paths that exist today:**
   - NVIDIA Inception: free, no equity.
   - The Dell AI Ecosystem Program (May 2026): a self-validated blueprint on Dell AI Factory and listing in Dell catalogs.
   - Dell OEM Solutions: a de-branded box that carries the ISV's brand.
   - The Dell + Cohere North turnkey on-prem precedent.
   - **Not found publicly:** the revenue split for an ISV whose software comes pre-installed on Dell, HPE or Lenovo hardware, and the process for getting onto Dell's price list.

---

## Findings table

### A. Hardware-enabled software analogs (Samsara, Motive, Verkada)

| # | Finding | Number | Source (publisher, date, URL) | Exact quote / table cell | Verified? |
|---|---|---|---|---|---|
| F1 | Samsara ARR and revenue, Q2 FY2027 (quarter ended Aug 1, 2026) | ARR $2,124.7M (+30% YoY); revenue $508.4M (+30%) | Samsara Inc., Exhibit 99.1 earnings release, 2026-09-03, https://s29.q4cdn.com/853855404/files/content_files/Q2-2027-Earnings-Press-Release-Draft-FINAL.pdf | "Ending ARR of $2.125 billion, representing 30% year-over-year growth"; "Q2 revenue of $508.4 million, representing 30% year-over-year growth" | Verified (PDF text extracted) |
| F2 | Samsara gross margin, Q2 FY2027 | GAAP 77%; non-GAAP 78% | Same release (F1) | Table rows: "GAAP gross margin ... 77%" and "Non-GAAP gross margin ... 78%" | Verified |
| F3 | Samsara large customers | 3,194 customers >$100K ARR (Jan 31, 2026); about 61% of ARR from them. 3,605 customers >$100K ARR at Q2 FY27 | Samsara 10-K for the FY ended 2026-01-31 (filed Mar 2026), https://www.sec.gov/Archives/edgar/data/1642896/000162828026018167/iot-20260131.htm. Q2 figure: Quartr event summary, Sept 2026, https://quartr.com/events/samsara-inc-iot-q2-2027_ojW4QHpw | 10-K: "As of January 31, 2026, we had 3,194 large customers, each representing over $100,000 in ARR. ... approximately 61% of our ARR came from large customers". Quartr: "Large customers ($100,000+ ARR) contributed $1.3 billion in ARR, up 38% year-over-year, with 3,605 customers in this segment" | 10-K: verified. 3,605: verified on a secondary source (Quartr); I did not open the primary shareholder letter |
| F4 | Samsara pricing model: per asset, per application. The device, connectivity, support and warranty are inside the subscription; 3-5 year terms | 3-5 year initial terms; about 98% of revenue from subscriptions | Samsara FY2026 10-K (F3 URL) | "A subscription to our Connected Operations Platform includes IoT data collection, which usually comes from a Samsara IoT device, such as an internet gateway, camera or sensor ...; cellular connectivity for our IoT devices; access to our cloud Applications ...; customer support; and warranty coverage. We generally price our subscriptions on a per asset, per application basis. For example, one vehicle using two Applications (AI Video-Based Safety and Telematics) would count as two subscriptions." / "Our contracts are typically for an initial subscription term of three to five years." / "approximately 98% of our revenue from subscriptions" | Verified |
| F5 | Samsara net revenue retention | **Not found** in the FY2026 10-K text (zero hits for "net retention rate") or in the Q2 FY27 release. A secondary snippet says the target is about 115% for Core Customers | Snippet only (e.g., https://www.saastr.com/5-interesting-learnings-from-samsara-at-1-9-billion-in-arr/) | n/a | Unverified |
| F6 | Motive ARR | $501M at Sep 30, 2025 (+28% YoY) | Motive Technologies, Form S-1, Dec 2025, https://www.sec.gov/Archives/edgar/data/1646681/000162828025058773/motive-sx1.htm | "Our ARR as of September 30, 2024 and 2025 was $393 million and $501 million, respectively, representing 28% year-over-year growth." | Verified |
| F7 | Motive gross margin and net dollar retention | Gross margin 70% (9M 2025 and FY2024). NDR: Core 110%, Large (>$100K) 126% at Sep 30, 2025. 9,201 Core and 494 Large customers | Motive S-1 (F6) | Table: "Gross margin 70 % 70 %" (9M 2024/2025). "As of September 30, 2024 and 2025, our Core Customers had an NDR of 109% and 110%, respectively, and our Large Customers had an NDR of 124% and 126%, respectively." | Verified |
| F8 | Motive pricing model: hardware bundled in the subscription, per asset per product, about 3-year contracts; device cost amortized over 5 years | 3-year typical term; 5-year device amortization | Motive S-1 (F6) | "A subscription to our platform includes the use of our platform, along with an integrated suite of hardware devices. Our subscription pricing is structured on a per asset, per product basis, with contracts typically spanning three years." / "Deferred device costs are generally amortized over a five-year expected benefit period." | Verified |
| F9 | Motive expanded from its first vertical | 70% of ARR from outside trucking and logistics (Sep 30, 2025), up from 65% a year earlier | Motive S-1 (F6) | "ARR from industries outside of trucking and logistics representing 70% of our total ARR as of September 30, 2025, compared to 65% as of September 30, 2024. Our fastest growing verticals include construction, field service, and passenger transit." | Verified |
| F10 | Motive list price per vehicle | About $25-35 per vehicle per month | Third-party pricing page, 2026, https://fleets.levyelectric.com/compare/motive-pricing | (snippet) "$25-35/vehicle/month with 1-3 year contracts" | Unverified (secondary snippet) |
| F11 | Verkada model: hardware purchase plus a mandatory per-device cloud license sold in 1/3/5/10-year terms | Camera license $199/yr (CDW, part LIC-CAM-1Y) to $249/yr (cited as MSRP) | CDW-G listing, https://cdwg.com/product/verkada-video-security-cloud-subscription-license-1-year-1-camera/7245788 (fetch timed out). Coram (a competitor's blog), https://www.coram.ai/post/verkada-pricing | (snippet) "LIC-CAM-1Y ... $199.00"; "1-year camera licenses at $249" | Unverified |

### B. On-prem / edge AI appliance analogs (ISV software on partner hardware)

| # | Finding | Number | Source | Exact quote | Verified? |
|---|---|---|---|---|---|
| F12 | Dell sells an ISV's agentic AI platform as a turnkey on-prem solution (Cohere North on PowerEdge). Customers engage through Dell sales | n/a (pricing and licensing not disclosed) | Dell Technologies blog (J. Jones), 2025-05-19, https://www.dell.com/en-us/blog/smart-simple-secure-enterprise-ai-with-dell-cohere/ | "the first provider to bring Cohere North's capabilities to organizations on-prem"; "delivered as a turn-key solution"; contact "your Dell Technologies sales representative" | Verified |
| F13 | Dell OEM Solutions lets an ISV ship its own branded appliance on Dell hardware | n/a | Dell OEM Solutions page (undated), https://www.dell.com/en-us/dt/oem/index.htm | "De-branded, regulatory-approved tier 1 products are standing by to carry your brand's identity" | Verified |
| F14 | Dell AI Ecosystem Program: an ISV self-validates on Dell AI Factory and gets catalog visibility and a certified designation | Fees: not stated | Dell blog (B. Maltz), 2026-05-18, https://www.dell.com/en-us/blog/simplifying-enterprise-ai-introducing-the-dell-ai-ecosystem-program/ | "a validation and blueprinting framework that sits on top of Dell AI Factory"; "Self-validated Blueprint on Dell Automation Platform"; "Visibility and credibility through Dell's AI ecosystem destinations and catalogs"; "AI Ecosystem Certified" designation | Verified |
| F15 | Revenue split between an ISV and its hardware partner (Dell, HPE, Lenovo) for pre-installed AI or ops software | **Not found** | n/a | n/a | Not found |

### C. Robotics pricing anchors

| # | Finding | Number | Source | Exact quote | Verified? |
|---|---|---|---|---|---|
| F16 | Locus Robotics RaaS price, all-in | About $2,000 per robot per month. Also: $180M ARR (Jun 2026); 17,000+ robots across 360+ sites | Sacra company page (as of Jun 2026), https://sacra.com/c/locus-robotics | "roughly $2,000 per robot per month all-in, that covers hardware, software, maintenance, and support"; "$180M in annual recurring revenue (ARR) in June 2026"; "17,000+ robots across 360+ sites" | Verified on a secondary source. Sacra cites no primary source. **Conflict (CALC):** 17,000 × $2,000 × 12 = $408M, which is more than twice the $180M ARR. If every robot were on subscription, the implied average is $180M / 17,000 / 12 = **$882 per robot per month**. Use a range of **$880-$2,000** |
| F17 | Formic RaaS pricing is a fixed monthly OpEx price with no capex | No dollar amount on the site | Formic homepage (accessed 2026-10-03), https://formic.co/ | "One fixed monthly price. Zero capital risk."; "$0 CapEx Required" | Verified |
| F18 | Formic hourly price | "As low as $8 an hour" | Gear Technology (about 2021), https://www.geartechnology.com/robotics-as-a-service-lets-manufacturers-hire-robots-at-low-hourly-rate. Robotics 24/7, 2021-08-30, https://www.robotics247.com/article/formic_offers_robotics_as_a_service_and_financing_to_manufacturers | $8 figure: search snippet only. Robotics 24/7: "We offer systems at a low hourly rate with guaranteed performance and SLAs" | $8: unverified and stale (pre-2022). SLA quote: verified but stale (2021) |
| F19 | Pricing for robot fleet-management software (InOrbit) | **No public dollar prices** | InOrbit pricing page, https://inorbit.ai/pricing | The page shows no dollar amounts (I opened it). The snippet describes the Standard tier as "per robot, pay as you go pricing with volume discounts" | Absence verified; tier wording unverified |

### D. Value anchors: BLS OEWS, May 2025 national estimates (wages only, excluding benefits)

**Source for all rows:** U.S. Bureau of Labor Statistics, OEWS May 2025 estimates. These were pulled on 2026-10-03 from the BLS Public Data API, https://api.bls.gov/publicAPI/v1/timeseries/data/. The API is the latest available; data year 2025, period "A01".

Human-readable pages follow the pattern https://www.bls.gov/oes/current/oes435032.htm. The site blocked automated fetch, so I queried the API instead.

**Series ID format:** OEUN + 13 zeros + SOC code + data type. Data types: 13 = annual median, 08 = hourly median, 04 = annual mean, 01 = employment.

| # | Occupation (SOC) | Median annual | Median hourly | Other | API cell quoted | Verified? |
|---|---|---|---|---|---|---|
| F20 | Dispatchers, except police, fire and ambulance (43-5032) | **$50,340** | **$24.20** | Mean $54,740; employment 202,810 | OEUN000000000000043503213: {"year":"2025","period":"A01","value":"50340"} | Verified (primary API) |
| F21 | First-line supervisors of mechanics, installers and repairers (49-1011) | **$79,860** | **$38.39** | Mean $85,220; employment 617,500 | OEUN000000000000049101113: "79860" | Verified |
| F22 | Industrial machinery mechanics (49-9041) | **$64,520** | $31.02 | Employment 439,640 | OEUN000000000000049904113: "64520" | Verified |
| F23 | Maintenance and repair workers, general (49-9071) | **$49,590** | $23.84 | Employment 1,529,700 | OEUN000000000000049907113: "49590" | Verified |
| F24 | Closest robotics field-engineer proxies: electro-mechanical and mechatronics technologists and technicians (17-3024); electrical and electronics repairers, commercial and industrial equipment (49-2094) | **$73,900** (17-3024); **$74,090** (49-2094) | n/a | 17-3024 employment 15,520 | OEUN000000000000017302413: "73900"; OEUN000000000000049209413: "74090" | Verified |

These are wage-only figures; fully loaded employer cost is higher. I did not source a benefits multiplier, so the anchors below are conservative floors.

### E. Channels, partner programs, hardware and NVIDIA licensing

| # | Finding | Number | Source | Exact quote | Verified? |
|---|---|---|---|---|---|
| F25 | Dell Pro Max with GB10 US list price | **$9,007** (128GB, 4TB, DGX OS 7). CALC from the page's deltas: 1TB = $9,007 − $2,830 = **$6,177**; 2TB = $9,007 − $2,450 = **$6,557** | Dell.com US product page (accessed 2026-10-03), https://www.dell.com/en-us/shop/cty/pdp/spd/dell-pro-max-fcm1253-micro | "Dell Price $9,007.00"; storage options "– $2,830.00" (1TB) and "– $2,450.00" (2TB) | Verified (two US product URLs show the same figure). **Conflict:** an earlier search snippet showed "$4,600.84", which is unverified and probably an older listing. Samsara's release lists "increases in the cost of memory and computing" as a risk (F1 PDF). Prices are volatile, so quote a range |
| F26 | NVIDIA AI Enterprise list pricing (self-managed) | $4,500 per GPU for 1 year; $18,000 for 5 years ("five years for the price of four"); $22,500 perpetual with 5 years of support; cloud $1 per GPU-hour; EDU/Inception price $1,125 per GPU per year (75% off) | NVIDIA docs, "Last updated on Sep 02, 2026", https://docs.nvidia.com/ai-enterprise/planning-resource/licensing-guide/latest/pricing.html | "$4,500 / GPU"; "$22,500 / GPU" with "5 years support"; "$1 / hour / GPU + CSP Instance Cost(s)"; "$1,125 / GPU" | Verified. The page does not list GB10, DGX Spark or workstation SKUs, and its eligibility wording for the Inception discount is ambiguous |
| F27 | NVIDIA Inception: free, no equity, preferred pricing on select products, go-to-market support that grows with engagement | Eligibility: at least 1 developer, a website, incorporated, less than 10 years old | NVIDIA, https://www.nvidia.com/en-us/startups/ (accessed 2026-10-03) | "Inception is free. The program doesn't have application fees, membership fees, or equity requirements."; "Members must employ at least one developer, maintain a working website, be officially incorporated, and be less than 10 years old."; "Preferred pricing is only available for select hardware and software products."; "Unlock go-to-market and other business opportunities as your engagement with NVIDIA grows." | Verified |
| F28 | Public process for a small ISV to get onto Dell's price list or into joint sales | **Not found.** The documented paths are OEM (F13), the AI Ecosystem Program (F14) and turnkey co-sell precedents (F12) | n/a | n/a | Not found |

### F. SaaS benchmarks (sanity check)

| # | Finding | Number | Source | Exact quote | Verified? |
|---|---|---|---|---|---|
| F29 | KeyBanc Capital Markets / Sapphire Ventures 2025 private SaaS survey | ARR growth 15% (2024), 20% expected (2025); net retention above 100%; gross retention near 90%; account-executive payback expected to shorten to 18 months by 2026 | Sapphire Ventures press release, 2025-11-13, https://sapphireventures.com/?p=258480; survey page https://info.sapphireventures.com/2025-keybanc-capital-markets-sapphire-ventures-saas-survey | "YoY ARR growth is expected to accelerate from 15% in 2024 to 20% in 2025"; "net retention has continued to remain above 100%"; "SaaS companies are maintaining gross retention near 90%"; "account executive payback periods expected to shorten to 18 months by 2026" | Verified. The detailed medians (subscription gross margin, CAC payback) are in the gated report, which I did not open |
| F30 | Same survey, more detailed medians reported by a secondary site | Median NDR 101% (2024), peak 109% (2021); CAC payback 16 months (2025) | cfo.successcoaching.co (secondary), https://cfo.successcoaching.co/ | Search snippet only | Unverified |
| F31 | Bessemer "Scaling to $100 Million" benchmarks | Gross retention "relatively consistent at 85-90%" | Bessemer Venture Partners, 2021-09-21, https://www.bvp.com/atlas/scaling-to-100-million | "relatively consistent at 85-90%" | Verified but **stale (pre-2022)**; context only |

---

## PROPOSAL / CALCULATION (ShiftLead pricing and GTM)

> Everything below is a proposal. Inputs cite findings (F#); arithmetic is labeled CALC. Assumptions are labeled ASSUMPTION and are not sourced.

### Design principles taken from the analogs

1. **Price the unit the customer already counts.**
   - Samsara and Motive price "per asset, per application/product" (F4, F8).
   - For ShiftLead the natural units are the **site**, which equals one Dell box, and the **industry pack**, which plays the role of an "application".
2. **Use multi-year terms that match device life.** Samsara's terms are 3-5 years (F4) and Motive's about 3 years (F8). Motive amortizes devices over 5 years (F8). Use **36-month** terms.
3. **Don't charge per user.** Assignment quality improves with every technician on the system, so per-seat pricing taxes the thing that creates value.
4. **Keep hardware on Dell's books.**
   - Motive bundles hardware and runs at a 70% gross margin, with hardware "basically break even" (snippet).
   - ShiftLead's software has no cloud-inference cost because it runs locally. If the customer buys the GB10 from Dell, ShiftLead keeps software margins and Dell books clean per-site hardware revenue.

### Three pricing structures, each tested on the example customer

**Example customer (ASSUMPTION):** a robotics/RaaS company with 25 customer sites, 20 robots per site (500 robots, matching the 20-robot demo) and 15 field engineers.

| Structure | Price (PROPOSAL) | Anchor (CALC, inputs cited) | Example ACV (CALC) | Pros / cons |
|---|---|---|---|---|
| **1. Per site + per technician seat** | $250 per site per month + $100 per technician per month | Site fee = $250 / ($50,340 / 12 = $4,195) = **6.0% of a dispatcher's median monthly wage** (F20). Seat = $100 / $5,377-$6,158 = **1.6-1.9% of a field technician's median monthly wage** (F22, F24) | 25 × $250 × 12 + 15 × $100 × 12 = **$93,000** | Familiar from field-service software, but it taxes adoption, and robotics teams have few seats relative to sites |
| **2. Per monitored asset (robot)** | $25 per robot per month, minimum 10 per site | $25 / $880-$2,000 = **1.25-2.8% of a robot's monthly RaaS fee** (F16) | 500 × $25 × 12 = **$150,000** | Speaks robotics' language and scales with the fleet. But it doesn't transfer to verticals without countable assets, and it decouples price from the Dell box |
| **3. Site plan + industry packs (RECOMMENDED)** | **$400 per site per month**, which includes the core, 1 industry pack, up to 25 monitored assets and unlimited technicians. Add-ons: **+$150 per site per month** for each extra pack, **+$15 per asset per month** above 25. 36-month term, billed annually. **GB10 bought through Dell** | $400 / $4,195 = **9.5% of a dispatcher's median monthly wage** (F20). $400 / $6,655 = **6.0% of a supervisor's** (F21). Per robot at 20 robots per site: $20, which is **1.0-2.3% of the RaaS fee** (F16) | 25 × $400 × 12 = **$120,000** | One SKU per Dell box, which makes it simple for Dell's channel. It mirrors Samsara's and Motive's per-asset, per-application structure. There are three expansion levers: sites, packs and assets |

### Recommended structure applied to the example customer

| Item | Value | Basis |
|---|---|---|
| Software ACV | **$120,000 per year** | CALC 25 × $400 × 12 |
| 3-year contract value | **$360,000** | CALC $120,000 × 3 |
| Hardware revenue to Dell (one-time, list price) | **$154,425-$225,175** | CALC 25 × $6,177 (1TB) to 25 × $9,007 (4TB) (F25). Volume or channel pricing will differ. The local model needs far less than 1TB of storage, so the 1TB configuration is likely enough (ASSUMPTION) |
| Optional bundled price (hardware amortized into the subscription) | $572-$650 per site per month, i.e. **$171,600-$195,000 per year** | CALC $400 + $6,177/36 (= $172) to $400 + $9,007/36 (= $250), no financing cost. **Caution:** if hardware passes through at cost and software COGS is 15% (ASSUMPTION), the blended gross margin falls to **52-64%**, below Motive's 70% and Samsara's 77-78% (F7, F2). Offer the bundle only through a leasing partner, and keep "buy the box from Dell" as the default |
| Expansion: second pack on all sites | +$45,000, giving **$165,000** ACV (+37.5%) | CALC 25 × $150 × 12 |
| Expansion: 100 sites | $480,000 ACV | CALC 100 × $400 × 12 |

**Payback against the value anchors (CALC, wage-only, so conservative).**

- **Break-even hours.** The software ($400 per month) pays back if it saves **2.4 supervisor-hours per site per week** ($400 / $38.39 / 4.33), or 3.8 dispatcher-hours ($24.20/hour).
  - Including the Dell box amortized over 36 months ($572-$650 per month), break-even is **3.4-3.9 supervisor-hours per week** (5.5-6.2 dispatcher-hours).
  - Inputs: F20, F21, F25.
- **Labor equivalents.**
  - The $120K ACV equals **2.4 dispatcher median wages** or **1.5 supervisor median wages** for all 25 sites (F20, F21). Per site, that is about 1/10 of a dispatcher.
  - It also equals **10.8-12.4%** of the 15 field engineers' median wage bill, which is $967,800-$1,111,350 (F22, F24).
- **Fleet revenue equivalent.**
  - The 500 robots at $880-$2,000 per month bring in $5.3M-$12.0M per year in RaaS revenue (F16).
  - The ACV is **1.0-2.3%** of that, so it breaks even if ShiftLead protects about 1-2 points of fleet availability on revenue tied to uptime.
- **Illustrative scenario (ASSUMPTIONS, not sourced).** ShiftLead absorbs 1.0 dispatcher FTE plus 0.5 supervisor FTE of coordination work ($90,270), returns 5% of field-engineer time ($55,425, using 17-3024 wages), and adds 0.5 points of fleet uptime ($26K-$60K).
  - Total value: **$172K-$206K per year**, or $146K wage-only.
  - Software-only payback: **7-8.4 months** (9.9 months wage-only).
  - All-in payback, including Dell hardware at list: **16-24 months**.
  - 3-year all-in ROI: **0.9-1.2x**.
- **What this means for the pitch.** The software fee is easy to justify, but the per-site box is the dominant first-year cost: $6.2K-$9.0K, or 1.3-1.9x the site's $4,800 first-year fee. Lead with sites where at least one of these holds:
  - the GB10 also runs other workloads (robot policy inference, as in the demo, or video);
  - downtime is contractually priced (RaaS uptime SLAs, F18);
  - there are many assets or engineers per box.

  This scenario leaves out benefits-loaded labor, travel costs and SLA penalties, so it is a floor.

### Sanity check against benchmarks

| Metric | ShiftLead target (ASSUMPTION) | Benchmark |
|---|---|---|
| Gross margin | 80%+ on software. Hardware is on Dell's books and there is no cloud inference cost | Samsara 77-78%, including devices and connectivity (F2); Motive 70% with bundled hardware (F7) |
| Net retention | 110%+ via more sites, packs and assets | KeyBanc/Sapphire: "above 100%" (F29). Motive: Core 110%, Large 126% (F7) |
| Gross retention | About 90% or better; 36-month terms help | KeyBanc/Sapphire "near 90%" (F29) |
| CAC payback | 18 months or less. CALC: $120K × 80% = $96K gross profit per year, so CAC up to $144K keeps payback at 18 months | KeyBanc/Sapphire account-executive payback expected at 18 months by 2026 (F29) |
| NVIDIA AI Enterprise | Don't bundle by default. ShiftLead serves its model with open-source vLLM, and the NVAIE list price of $4,500/GPU/yr would equal **94%** of a site's $4,800/yr software fee (CALC, F26). Pass it through only if a customer requires NVIDIA enterprise support | F26 |

### Go-to-market: land, then expand, then a new vertical (PROPOSAL)

| Phase | Target | Offer | Channel | Proof metric | Analog evidence |
|---|---|---|---|---|---|
| **1. Land (months 0-6)** | Robotics/RaaS companies with scarce field engineers. Robots have structured telemetry, and downtime has a price (F16, F18) | A 3-5 site pilot on the site plan with the robotics pack, converting to a 36-month term. The customer buys the GB10 through Dell | Direct sales, plus the hardware via Dell. Join **NVIDIA Inception** (free, F27). Submit a **Dell AI Ecosystem self-validated blueprint** for catalog listing and the "AI Ecosystem Certified" designation (F14) | Alarm-to-"right engineer en route" time; supervisor hours saved per site per week against the 2.4-3.9 hour break-even; trust-gate pass rate | Samsara and Motive land with one application, then add more (F4, F8) |
| **2. Expand (months 6-18)** | All of the customer's sites (25 → 100+) | Second pack (for example, inventory/throughput or robot-skill commissioning). The robotics company can embed ShiftLead in its own RaaS offering | Expansion led by account management; Dell co-sell on hardware refreshes | Net retention of 110% or more | Samsara: about 61% of ARR from $100K+ customers (F3). Motive: Large-customer NDR 126% (F7) |
| **3. New vertical (month 18+)** | Industrial maintenance and facilities. These are large technician pools: 439,640 industrial machinery mechanics and 1.53M general maintenance workers, coordinated by 617,500 first-line supervisors and 202,810 dispatchers (F20-F23) | Same core, new pack (connectors, detectors, vocabulary) | **Dell OEM** de-branded box carrying the ShiftLead brand once volume justifies it (F13); Dell AI Factory catalog and co-sell, following the Cohere North precedent (F12) | Share of ARR from outside robotics | Motive: 70% of ARR from outside its original vertical (F9) |

### Open items and gaps (not found in the time box)

- The revenue split for ISV software pre-installed on Dell, HPE or Lenovo hardware (F15).
- How a small ISV gets a SKU onto Dell's price list (F28). Ask Dell's judges directly; it is a good pitch question.
- Samsara's latest primary-source NRR figure (F5).
- List prices for robot fleet-management software (F19).
- Primary-source list prices for Verkada and Motive (F10, F11).
- The GB10 street price is moving: $9,007 today for 4TB, against roughly $4,600 earlier (F25). Re-check before the pitch.
