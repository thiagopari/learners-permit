# Track B: Market size, buyer and momentum (ShiftLead)

Researched 2026-10-03, 13:33-13:55 CDT. Rules from BRIEF.md applied:
- **Verified** means I opened the page or primary dataset and saw the number. **Unverified** means I saw it only in a search snippet or secondhand.
- **SEO** marks a figure that comes only from a market-research summary page. These firms disagree with each other by 2-10x, so treat them as brackets, not facts.
- All BLS figures were pulled from the official BLS Public Data API (api.bls.gov). The bls.gov HTML tables return HTTP 403 to automated fetches. The Census CBP API now requires a key, so I used BLS QCEW for establishment counts.

---

## 1. Findings table

| # | Finding | Number | Source (publisher, date, URL) | Exact quote / table cell | Verified? |
|---|---|---|---|---|---|
| 1 | US employment, Installation, Maintenance and Repair Occupations (SOC 49-0000) | **6,086,190** (3.9% of 155,495,730 total US employment; calculation) | BLS OEWS, May 2025 estimates. BLS API series `OEUN000000000000049000001` and `OEUN000000000000000000001`. Human-readable table: https://www.bls.gov/oes/2025/may/oes490000.htm | API cell: `2025, A01, 6086190`; all occupations `2025, A01, 155495730` | Verified (BLS API) |
| 2 | Field-tech occupations, US employment (May 2025) | Maintenance and Repair Workers, General **1,529,700**; Industrial Machinery Mechanics **439,640**; HVAC Mechanics and Installers **409,670**; Telecom Equipment Installers (except line) **140,920**; Telecom Line Installers **97,720**; Medical Equipment Repairers **65,990**; Electrical and Electronics Repairers, Commercial/Industrial **65,010**; Millwrights **40,330**; Electro-Mechanical and Mechatronics Technicians **15,520**; Wind Turbine Service Technicians **9,980** | BLS OEWS May 2025 via API. Series `OEUN0000000000000` + SOC + `01` (499071, 499041, 499021, 492022, 499052, 499062, 492094, 499044, 173024, 499081) | API cells, e.g. `499041 -> 2025 A01 439640` | Verified (BLS API) |
| 3 | Mean annual wage, robotics-adjacent techs (May 2025) | 49-0000 **$63,320**; Industrial Machinery Mechanics **$68,460**; Electrical and Electronics Repairers, Comm./Ind. **$75,570**; Electro-Mechanical and Mechatronics Techs **$76,420**; Medical Equipment Repairers **$65,930** | BLS OEWS May 2025 via API (datatype 04) | e.g. `OEUN000000000000049904104 -> 2025 A01 68460` | Verified (BLS API) |
| 4 | Global deskless workforce (Emergence Capital) | **2.7 billion**, **~80%** of global workforce | Emergence Capital, "The State of Technology for the Deskless Workforce", Nov 2020. https://emcap.com/technology-for-the-deskless-workforce-2020 | "2.7 billion employees around the world that are not desk-bound for the majority of their role"; "Approximately 80% of the global workforce is considered 'deskless.'" | Verified that the original says it. **Flag:** dated 2020 (older than 2022), and the report cites no source or method for 2.7B. |
| 5 | "Physical operations" share of GDP (company estimate) | **>40% of global GDP** | Samsara Inc. Form 10-K, FY2026 (FYE Jan 31, 2026). https://www.sec.gov/Archives/edgar/data/1642896/000162828026018167/iot-20260131.htm | "We estimate that these industries represent over 40% of the global GDP." (industries listed include field services, logistics, manufacturing, utilities, healthcare) | Verified (company estimate in an SEC filing, not independent) |
| 6 | Samsara (Connected Operations platform for physical ops) ARR | **$2.125B ARR, +30% YoY** (Q2 FY2027, ended Aug 1, 2026) | Samsara Q2 FY2027 earnings release, Sep 3, 2026. https://s29.q4cdn.com/853855404/files/content_files/Q2-2027-Earnings-Press-Release-Draft-FINAL.pdf | "Ending ARR of $2.125 billion, representing 30% year-over-year growth" | Verified |
| 7 | Professional service robots sold worldwide in 2024 (IFR World Robotics 2025) | ~**200,000** units (+9%); transport and logistics **102,900** (+14%); medical ~16,700 (+91%) | IFR press release, Frankfurt, Oct 7, 2025. https://ifr.org/ifr-press-releases/news/service-robots-see-global-growth-boom | "The total number of service robots sold for professional use reached almost 200,000 units in 2024, marking a 9% increase." "With 102,900 units (+14%) sold in 2024, more than every other professional service robot was built for the application class transportation and logistics." | Verified. World Robotics 2026 service-robot data not found yet (usually released in October). |
| 8 | Robots-as-a-Service growth (IFR) | RaaS fleet **+31%**; RaaS in transport/logistics **+42%** (2024) | Same IFR release, Oct 7, 2025 | "The robot-as-a-service fleet (RaaS) has grown impressively by 31%." "RaaS enjoyed growing popularity with a growth rate of 42% in 2024" | Verified |
| 9 | Mobile robot market revenue (Interact Analysis) | **just under $5B (2024) -> $14B (2030)**; 2030 forecast cut from $15.6B (May 2025) because of tariffs | CFO Dive, Jan 20, 2026, reporting Interact Analysis. https://www.cfodive.com/news/mobile-robot-sales-projected-reach-14b-2030/809950/ | "mobile robot revenue will increase from just under $5 billion in 2024 to $14 billion in 2030"; "downwardly revised $15.6 billion estimate for 2030 that Interact Analysis forecast in May 2025" | Verified (secondary; the Interact report is paywalled). Caution: Interact's 2021-era forecast of "$18 billion" revenue and 2.1M robots shipped by 2025 (controleng.com snippet, unverified) overshot badly. |
| 10 | Amazon robot fleet (largest single fleet; builds and runs it in-house, so not a buyer) | **1,000,000** robots; **300+** facilities; DeepFleet cuts robot travel time **10%** | Amazon (aboutamazon.com), undated page (press coverage dates it to July 2025, unverified). https://www.aboutamazon.com/news/operations/amazon-million-robots-ai-foundation-model | "We've just deployed our 1 millionth robot"; "our global network that now spans more than 300 facilities worldwide" | Verified (quotes); date unverified |
| 11 | Locus Robotics (AMR vendor running fleets at customer sites) | **150+** customers at **350+** sites | The Robot Report, Apr 24, 2025. https://www.therobotreport.com/locus-robotics-surpasses-5b-picks-warehouse-automation/ | "Locus Robotics customers include more than 150 leading retail, e-commerce, healthcare, third-party logistics (3PL), and industrial brands at over 350 sites worldwide." | Verified. "Tens of thousands of robots" and "6 billion picks" (BusinessWire, Oct 22, 2025): unverified (403). |
| 12 | Symbotic: field service-heavy robot vendor | ~**2,000** FTE, **about half at customer sites**; backlog **~$22.5B** | Symbotic Form 10-K FY2025 (FYE Sep 27, 2025). https://www.sec.gov/Archives/edgar/data/1837240/000183724025000278/sym-20250927.htm | "As of September 27, 2025, we employed approximately 2,000 full-time employees..."; "Approximately half are located across customer sites where they install, commission, and maintain our systems."; "We have approximately $22.5 billion of backlog as of September 27, 2025" | Verified. "37 operational systems" (Q2 FY2026 call): unverified snippet. |
| 13 | DHL x Boston Dynamics (Stretch) | **1,000+** additional robotic units (MOU); DHL invested **>EUR 1B** in contract-logistics automation over 3 years | Boston Dynamics press release, May 13, 2025. https://bostondynamics.com/news/dhl-signs-mou-for-additional-1000-robot-deployment/ | "DHL Group has invested over €1 billion in automation in its contract logistics division over the past three years alone" | Verified. Pattern: collaboration since 2018, commercial in 2023, then an MOU to scale (pilot, then land-and-expand). |
| 14 | US warehousing and storage establishments (NAICS 493, private) | **23,848** (2026 Q1); 23,697 (2025 Q4); employment 1,859,296 (Mar 2026) | BLS QCEW via BLS API series `ENUUS000205493` (establishments) and `ENUUS000105493` (employment) | API cells: `2026 Q01 23848`; `2025 Q04 23697`; `2026 M03 1859296` | Verified (BLS API). Census CBP 2023 "22,000 establishments" is an unverified snippet. **Undercount:** DCs run by wholesalers/retailers are classified in NAICS 42/44-45. |
| 15 | US hospitals | **6,100** total; **5,121** community hospitals (FY2024 survey data) | American Hospital Association, "Fast Facts on U.S. Hospitals, 2026" (PDF, Feb 2026). https://www.aha.org/system/files/media/file/2026/02/Fast-Facts-on-US-Hospitals-2026-Infographics.pdf | "Number of Hospitals by Type (Total 6,100), FY2024"; "Community Hospitals by Ownership Type (Total 5,121), FY 2024" | Verified (PDF text extracted) |
| 16 | US public EV charging sites | **82,581** station locations; **260,486** ports | US DOE Alternative Fuels Data Center, "data last updated: 10/3/2026". https://afdc.energy.gov/stations/states | Table cells "82,581" and "260,486" | Verified |
| 17 | Buyer evidence: robot vendor field service leader | Locus **Director of Field Services**: owns dispatch, coverage, uptime KPIs; **40-60% travel** | Locus Robotics job posting on Built In (Wilmington, MA); removed Jan 20, 2026. https://builtin.com/job/director-field-services/7976188 | "Own technician scheduling, dispatching, and coverage models to improve response times and reduce travel"; "Define and report KPIs to track uptime, repair efficiency, and overall fleet health"; "Build, lead, and scale a field services organization of internal technicians and external partners"; "This role requires 40-60% travel across the U.S., Canada, and Mexico." | Verified. Symbotic "Leader of Service Operations" (Jul 24, 2025: "on-site maintenance, field service coordination, lifecycle management"): unverified (page 404). |
| 18 | Incumbent agentic field service (sharpens the gap claim) | Salesforce **Agentforce for Field Service**; scheduling takes 17 min (change 15, cancel 12), cut to "<5 min"; GA May-June 2025 | Salesforce newsroom, Apr 9, 2025. https://www.salesforce.com/news/stories/agentforce-for-field-service-announcement/ | "Agentforce for Field Service automates scheduling, paperwork, and reporting"; the dispatcher agent weighs "job duration, available parts, and traffic data" (from search summary of same page) | Verified (headline and stats); traffic-data phrase seen via search summary |
| 19 | Momentum: ServiceTitan IPO (trades/field service software) | Dec 12, 2024; **$71**/share; **~$625M** raised; first-day close $101, **~$8.9B** market cap | NBC New York (CNBC syndication), Dec 12, 2024. https://nbcnewyork.com/news/business/money-report/servicetitan-pops-to-101-in-cloud-software-vendors-nasdaq-debut-after-selling-shares-at-71/6064414/ | $71 IPO price, ~$625M raised, $101 close, ~$8.9B market cap; quarterly revenue $198.5M, ~24% YoY | Verified |
| 20 | Momentum: MaintainX (maintenance/CMMS + AI) | **$150M Series D at $2.5B** valuation, Jul 9, 2025; 11,000+ companies; 11M+ assets | MaintainX newsroom, Jul 9, 2025. https://www.getmaintainx.com/newsroom/maintainx-raises-150m | "$150M in Series D funding"; "$2.5B"; "turn their frontline professionals into the knowledge workers they deserve to be with AI" | Verified |
| 21 | Momentum: IFS buys an AI-agent company for industrial/field service | TheLoops acquisition announced **Jun 26, 2025** (agents modelled on "field technicians") | Verdantix blog, Sep 22, 2025. https://verdantix.com/vantage/blog/ifs-moves-deeper-into-autonomous-ai-with-theloops-acquisition | "On June 26, 2025, IFS announced the acquisition of TheLoops"; "pre-defined domain-specific agents, modelled on real-world personas such as customer order managers and field technicians" | Verified. IFS's 7bridges deal (Aug 2025): unverified snippet. |

### Software category brackets (top-down; mostly SEO market-research numbers)

| Category | Firm: figure | Verified? |
|---|---|---|
| **Field service management (FSM), global** | **Verdantix** (analyst firm, Oct 23, 2025): **$4.7B (2024) -> $9.2B (2030), 12% CAGR**. https://www.verdantix.com/venture/report/market-size-and-forecast--field-service-management-software-2024-2030-global | Verified |
| | Global Market Insights (Dec 2025): $5.49B (2025) -> $23.61B (2035), 16% CAGR. https://www.gminsights.com/industry-analysis/field-service-management-market | Verified page; **SEO** |
| | Grand View Research: $11.78B by 2030, 13.3% CAGR (via a reseller page) | Unverified, **SEO** |
| | Valuates Reports: $24.29B by 2030, 19.7% CAGR | Unverified, **SEO** (outlier) |
| FSM, US only | IBISWorld $2.8B (2025); P&S Intelligence $2.4B (2025) -> $6.6B (2032); MarketsandMarkets US $1.38B (2025) -> $2.16B (2030) | Unverified, **SEO** (2x spread) |
| CMMS | The Business Research Co. $1.45B (2025); Market.us $1.38B (2024) -> $3.55B (2034), 9.9% CAGR | Unverified, **SEO** |
| Workforce management | MarketsandMarkets $8.38B (2025) -> $13.03B (2030), 9.2%; Fortune Business Insights $11.60B (2025); Data Bridge $55.06B (2024) (outlier) | Unverified, **SEO** |
| AIOps | TBRC $11.16B (2025); Market Research Future $12.43B (2025); IMARC $32.5B (2025); MarketsandMarkets $32.4B by 2028, 22.7% CAGR (page verified, but the report is dated Aug 2023) | Mostly unverified, **SEO**; 3x spread |
| RaaS | GMI $2.21B; Coherent $2.42B; Fortune BI $2.70B; BIS Research $3.10B (all 2025); TBRC $26.93B (outlier, broad definition) | Unverified, **SEO** |
| Mobile robots (hardware-led) | Interact Analysis: just under $5B (2024) -> $14B (2030) (row 9) | Verified (secondary) |

**Conflicts:** global FSM software in 2024-25 clusters at **$4.7B-$6B** with credible sources, while 2030 forecasts range from $9.2B to $24.3B. AIOps 2025 ranges from $11B to $32.5B. Each RaaS and WFM bracket has one outlier at roughly 10x the rest. On the slide, use Verdantix (FSM) and Interact Analysis (mobile robots). Footnote the rest as a range.

**Not found within the time box:** a primary-source count of US warehouses that run robot fleets (the key unknown in the wedge SAM); per-site license pricing from any robot-ops or FSM vendor (InOrbit appears to price "per robot, pay-as-you-go", but this is an unverified snippet because the plans page returned 404); which budget line funds this at robot vendors or 3PLs; Agility Robotics and Zebra/Fetch fleet sizes.

---

## 2. Sizing calculation (all CALCULATIONS; inputs shown)

### 2a. Candidate per-site markets (US)

Formula: **annual revenue = sites x price per site per month x 12.** Annual price per site is $6,000 at $500/mo, $18,000 at $1,500/mo and $36,000 at $3,000/mo.

| Site type (US) | Sites (source) | @ $500/mo | @ $1,500/mo | @ $3,000/mo |
|---|---|---|---|---|
| Warehousing and storage establishments | 23,848 (row 14) | $143.1M | $429.3M | $858.5M |
| Hospitals | 6,100 (row 15) | $36.6M | $109.8M | $219.6M |
| Public EV charging locations | 82,581 (row 16) | $495.5M | $1.49B | $2.97B |
| **Total, three site types (illustrative umbrella TAM)** | **112,529** | **$675.2M** | **$2.03B** | **$4.05B** |

Caveats: (1) This counts only three site types. Factories, telecom, utilities and retail are left out, so it understates the umbrella. (2) A $1,500-$3,000/month price does not fit a small EV charging site. That segment would more likely be sold per network or per port, so the EV row overstates at the high price points. (3) The NAICS 493 count leaves out DCs run by wholesalers and retailers.

### 2b. Robotics wedge SAM (US warehouses running robot fleets)

Input: 23,848 NAICS 493 establishments (sourced). **Assumption (not sourced):** 10% / 20% / 30% of these run a robot fleet. No primary source for this share was found, and it is the first thing to validate.

| Penetration assumption | Sites | @ $500/mo | @ $1,500/mo | @ $3,000/mo |
|---|---|---|---|---|
| Low (10%) | 2,385 | $14.3M | $42.9M | $85.9M |
| **Mid (20%)** | **4,770** | **$28.6M** | **$85.9M** | **$171.7M** |
| High (30%) | 7,154 | $42.9M | $128.8M | $257.5M |

### 2c. Robotics wedge SOM (3-year, US)

SOM = 2% or 5% of the mid-case SAM sites (4,770). **Assumption.**

| Capture | Sites | @ $500/mo | @ $1,500/mo | @ $3,000/mo |
|---|---|---|---|---|
| 2% | 95 | $0.57M ARR | $1.71M ARR | $3.42M ARR |
| 5% | 239 | $1.43M ARR | $4.30M ARR | $8.60M ARR |

**Cross-check (calculation):** one vendor partnership the size of Locus (350+ sites worldwide, row 11) would be 350 x $6k-$36k = **$2.1M-$12.6M ARR** ($6.3M at $1,500/mo). So the SOM can be framed as "one or two robot-vendor partnerships".

**Value anchor (calculation):** $1,500/site/month = $18,000/yr = **26%** of one industrial machinery mechanic's mean annual wage ($68,460, row 3), before benefits and travel. $3,000/month = 53%; $500/month = 9%. If ShiftLead saves a fraction of one technician's time or truck rolls per site, it pays for itself.

Excluded: the per-site appliance hardware (Dell Pro Max GB10) and industry-pack upsell. Both add to these numbers but belong to other tracks.

---

## 3. Recommendations for the market slide

1. **Lead bottom-up, not with analyst TAMs.** Suggested funnel: "6.1M US maintenance and repair workers (BLS, May 2025) -> 23,848 US warehouses (BLS QCEW) -> robotics wedge SAM $29M-$172M/yr (mid-case 20% robot penetration, $500-$3,000/site/month)". Show the formula on the slide and label the 20% as an assumption to validate.
2. **Use at most two category anchors, both credible.** FSM software is **$4.7B (2024) -> $9.2B (2030)** (Verdantix). Mobile robots are **~$5B -> $14B** (Interact Analysis). Add IFR's **102,900 logistics robots sold in 2024 (+14%)** and **RaaS fleet +31%** for wedge momentum. Avoid the $23-55B SEO numbers; a Dell/NVIDIA panel will discount them.
3. **Make the buyer concrete.** Use the Locus "Director of Field Services" posting, which owns "technician scheduling, dispatching, and coverage models to improve response times and reduce travel" and uptime KPIs, with 40-60% travel. Add Symbotic's ~1,000 staff working at customer sites. The buyer is the robot vendor's VP/Director of Field Service or Customer Success (secondary: 3PL Director of Operations or Automation). How they buy, pilot first and then expand across sites, is evidenced by DHL's path: Locus at 35 sites, Stretch pilot then a 1,000-unit MOU. The budget line was not found; present it as a hypothesis (service cost of goods at the vendor, site ops budget at the 3PL).
4. **Use momentum to sharpen the gap, not just to show heat.** Cite ServiceTitan's IPO (~$8.9B at first close, Dec 2024), MaintainX at $2.5B (Jul 2025), Samsara at $2.1B ARR, +30% YoY (Sep 2026), whose 10-K estimates physical operations at >40% of global GDP, and the 2025 AI-agent launches from Salesforce (Agentforce for Field Service) and IFS (TheLoops). Incumbents already do travel-aware scheduling ("traffic data"), so the claim must be what they don't do: telemetry-triggered dispatch, a verified fix through the trust gate, and on-site local inference.
5. **Footnote or drop the 2.7B deskless figure.** The Emergence Capital original (Nov 2020) gives no methodology. If the vision slide needs a global number, use Samsara's ">40% of global GDP" (SEC filing, company estimate) or the BLS figures instead.
