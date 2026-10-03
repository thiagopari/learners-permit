# Track A: Pain and ROI numbers for ShiftLead

Research date: 2026-10-03. About 20 minutes of research. "Verified" means I opened the page or PDF and saw the number myself.
"Unverified" means I saw it only in a search snippet or secondhand. Vendor-sponsored sources are labeled.

## 1. Findings table (strong findings)

| # | Finding | Number | Source (publisher, date, URL) | Exact quote | Verified? |
|---|---|---|---|---|---|
| 1 | Cost of one hour of unplanned downtime at large manufacturing plants, by sector | **$36,000/h (FMCG) up to $2.3M/h (Automotive)** | Siemens, "The True Cost of Downtime 2024" (PDF dated Jun 2024; data Apr 2019 to Mar 2023; 181 online interviews at large industrial orgs in Automotive, FMCG, Heavy Industry, Oil & Gas). https://assets.new.siemens.com/siemens/assets/api/uuid:1b43afb5-2d07-47f7-9eb7-893fe7d0bc59/TCOD-2024_original.pdf | "At the bottom end, the costs of a lost hour are now $36,000 in Fast Moving Consumer Goods. At the top end, they are $2.3 million in the Automotive sector – or more than $600 a second." | Verified (vendor-published survey; covers large manufacturers, not warehouses) |
| 2 | Downtime cost per hour for small and mid-size manufacturers | **up to $150,000/h at the top end** | Siemens TCOD 2024, same PDF, p.6 | "Downtime costs can be significant for SMEs, reaching $150,000 an hour at the top end." | Verified |
| 3 | How often plants go down and for how long | **25 incidents/month; 27 h/month (about 326 h/yr) per large plant** | Siemens TCOD 2024, same PDF | "Plants now suffer an average of 25 downtime incidents a month per facility, down from 42 in 2019." / "An average large plant still loses 27 hours a month to unplanned downtime, down from 39 in 2019" | Verified |
| 4 | **Recovery is getting slower, partly because skilled maintenance people left.** This is the closest published proxy for "time to get the right person there" | **49 min (2019) to 81 min now (+32 min, +65%)** | Siemens TCOD 2024, same PDF, p.10 | "Five years ago, it took an average of 49 minutes to get production back up and running following downtime. Now, it takes 81 minutes." and "Many businesses lost skilled maintenance labour during the so-called post-Covid 'great resignation', creating a skills and knowledge gap, which led to longer recovery times." | Verified |
| 5 | Total downtime cost for the Fortune Global 500 (Siemens extrapolation) | **$1.4 trillion/yr = 11% of revenue** | Siemens TCOD 2024, same PDF | "We estimate that the world's 500 biggest companies lose almost $1.4 trillion annually through unplanned downtime, equivalent to 11% of their revenues." | Verified (an extrapolation, not a measurement) |
| 6 | Downtime cost for an **average distribution center** | **more than $10k/h**; vendor claims "$170k annual labor savings from reducing downtime by 40 percent" | Honeywell Intelligrated, "Connected Distribution Center: Increase Reliability" product page (undated). https://automation.honeywell.com/us/en/products/warehouse-automation/solutions-by-strategy/connected-distribution-center/increase-reliability | "The cost of downtime in an average DC can be more than $10k per hour." | Verified (vendor marketing, methodology not given) |
| 7 | Real distribution center case: idle labor cost of downtime | **17 h avoided in 4 months, about $40,000 idle labor; works out to about $2,350/h for idle labor alone (my calculation: $40,000 / 17 h)** | Honeywell Forge case study, "Automation That Delivers" (US retailer DC; PDF created Mar 2023). https://process.honeywell.com/content/dam/forge/en/documents/distribution-centers-documents/Automation_That_Delivers_CaseStudy.pdf | "They also avoided 17 hours of unplanned downtime, saving an estimated $40,000 in idle labor, and increased system capacity." (Infographic on the same PDF says "$42k".) | Verified (vendor case study; footnote: "Savings based on number of workers per site and hourly pay rate") |
| 8 | Sortation downtime cost | **more than $10,000/h** | Robotics 24/7, Apr 10, 2020 (Honeywell Intelligrated content). https://www.robotics247.com/article/connected_assets_limit_downtime_and_maximize_profits | "Sortation system downtime can cost an operation more than $10,000 per hour." | Verified (older than 2022, vendor-attributed) |
| 9 | E-commerce and logistics facilities have frequent stoppages and too few technicians | **80% had 6 or more unplanned downtime events in 12 months; 35% name too few skilled technicians as a top barrier to uptime; 95% of VPs say one major event would match (55%) or exceed (40%) their annual automation spend** | MultiSensor AI / Censuswide, "Uptime Economy: 2026" press release, Sep 16, 2026 (n=152 maintenance practitioners and VP Ops in ecommerce distribution and logistics). https://finviz.com/news/392563/multisensor-ai-survey-91-of-ecommerce-distribution-and-logistics-professionals-approved-automation-their-teams-were-not-ready-to-maintain | "Eighty percent of respondents say their facility experienced six or more unplanned downtime events affecting fulfillment, sortation or distribution operations in the past 12 months" / "Thirty-five percent of all respondents say a lean workforce and not enough skilled technicians is a top barrier to improving uptime" | Verified (vendor-sponsored: MultiSensor sells condition monitoring) |
| 10 | Field service first-time fix (FTF) rate and time to resolution | **FTF 77% average, 88% top performers, 60% bottom; MTTR 4.5 days average (2.5 top, 10 bottom)** | Aquant, "2026 Field Service Benchmark", Feb 19, 2026 (161 service orgs, about 30M service events, 7M assets, $8.3B service cost, 3 years). https://aquant.ai/resources/post/aquants-2026-field-service-benchmark-companies-can-unlock-up-to-26-in-service-cost-savings-by-scaling-knowledge-across-the-workforce | FTF "industry benchmark: 77%", "Top performers: 88%", "Bottom performers: 60%"; MTTR "Industry benchmark: 4.5 days" | Verified (vendor benchmark built from real work-order data, the strongest FTF source found) |
| 11 | Failed visits are a big share of service cost, and many trucks roll needlessly | **Failed visits = 25% of total service cost (median), 44% for bottom performers, 14% for top; "1 in 5 cases could be resolved remotely"** | Aquant 2026 benchmark, same URL | "1 in 5 cases could be resolved remotely, yet many teams still roll a truck—turning what could be a 1.4% cost impact into 18.3%." | Verified (vendor) |
| 12 | Most service issues still need a person on site | **55% of leaders say only 1 to 10% of issues can be resolved remotely or by self-service; 40% say 11 to 20%; 75% saw an 11 to 30% FTF gain from remote diagnostics** | Geotab, "The 2025 State of Field Service Report" (n=100 field service leaders; PDF created Sep 2026). https://www.geotab.com/CMS-GeneralFiles-production/NA/brochures/2025/field-service-operations/StateofFieldService2025%28ec%29RPT7Geotab.pdf | "most service issues still require on-site intervention. At 55%, a slight majority of respondents state that only 1-10% of their service issues can be resolved through remote service or customer self-service, while 40% report a slightly higher range of 11-20%." | Verified (vendor-sponsored, small sample) |
| 13 | Technician shortage reported by service leaders | **68% cite a technician shortage** | Aquant, Industrial Equipment page (undated). https://www.aquant.ai/industries/industrial-equipment | "68% of field service leaders cite a technician shortage" | Verified (vendor; methodology not shown) |
| 14 | Dispatcher overhead: technicians per dispatcher | **average 21:1; laggards 10 to 15:1; leaders "greatly exceed" 21:1** | IFS blog, "The death of the service dispatch", Jun 21, 2019, citing Gartner 2019 Magic Quadrant for FSM. https://blog.ifs.com/the-death-of-the-service-dispatch/ | Average ratio "21:1"; lagging firms "10-15 technicians per dispatcher" | Verified as a secondary source (Gartner original not opened; **older than 2022**) |
| 15 | Labor shortage: industrial machinery mechanics, maintenance workers and millwrights | **547,300 jobs (2025); +14% 2025 to 2035; about 51,900 openings/yr; median $64,100/yr ($30.82/h)** | US BLS Occupational Outlook Handbook, last modified Aug 27, 2026. https://www.bls.gov/ooh/installation-maintenance-and-repair/industrial-machinery-mechanics-and-maintenance-workers-and-millwrights.htm | "About 51,900 openings for industrial machinery mechanics, machinery maintenance workers, and millwrights are projected each year, on average, over the decade." / "Many of those openings are expected to result from the need to replace workers who transfer to different occupations or exit the labor force, such as to retire." | Verified (primary, government) |
| 16 | Labor shortage: HVAC mechanics and installers | **440,900 jobs; +11% 2025 to 2035; about 40,600 openings/yr; median $61,010 ($29.33/h)** | US BLS OOH, last updated Aug 27, 2026. https://www.bls.gov/ooh/installation-maintenance-and-repair/heating-air-conditioning-and-refrigeration-mechanics-and-installers.htm | "About 40,600 openings for heating, air conditioning, and refrigeration mechanics and installers are projected each year" | Verified (primary) |
| 17 | Labor cost loading factor (used in the ROI) | **wages = 70.0% of employer compensation, so loaded cost = wage / 0.70 (x1.43)** | US BLS, Employer Costs for Employee Compensation, June 2026 (released Sep 9, 2026). https://www.bls.gov/news.release/ecec.nr0.htm | "Wages and salaries averaged $32.82 and accounted for 70.0 percent of employer costs" | Verified (primary) |
| 18 | Retail inventory shrink | **1.6% of sales in FY2022 (up from 1.4%), $112.1B** | National Retail Federation, National Retail Security Survey 2023, Sep 26, 2023. https://nrf.com/research/national-retail-security-survey-2023 | "1.6%, up from 1.4% in FY 2021" / "that shrink represents $112.1 billion in losses" | Verified. This is still the **latest NRF shrink rate**: NRF reportedly stopped publishing a shrink rate in 2024 (Retail Dive / NPR coverage, **unverified**) |
| 19 | Robot vendors still need humans on the floor, even at best-in-class levels | **"99.9% uptime", local assist rate "< 1% of operating time", 24/7/365 remote command center, contracted performance guarantee** | Vecna Robotics, Performance Guarantee page (fetched 2026-10-03); guarantee announced Nov 2, 2023 (Robotics 24/7). https://www.vecnarobotics.com/performance-guarantee/ | "99.9% uptime < 1% local assist rate" / "The Pivotal™ Command Center ensures you get the help you need without a wait time, with a local assist rate of < 1% of operating time." | Verified (vendor marketing claim) |
| 20 | RaaS price and what service it includes | **$1,900 to $2,200 per robot per month; maintenance included; on-site support is an optional add-on; uptime and throughput guarantees "tailored"** | Brightpick, "How Brightpick's Robots-as-a-Service works", Jun 10, 2025. https://brightpick.ai/resources/how-brightpicks-raas-works/ | "Full-service maintenance is included, covering 24/7 remote support, preventive and emergency maintenance." / "Brightpick's RaaS contracts include uptime and throughput guarantees, tailored to your operational needs" | Verified (vendor) |
| 21 | Robot vendors' field engineers live on the road | **travel "up to 85%", plus on-call and after-hours emergency support** | HAI Robotics USA, Field Service Engineer I job posting (closed; post date not shown). https://app.trinethire.com/companies/170457-hai-robotics-u-s-a/jobs/119132-field-service-engineer-i | Travel requirement: "up to 85%" | Verified (primary: job posting) |

### Seen, but weak or not usable (do not put on a slide)

| Claim | Where seen | Status |
|---|---|---|
| Aberdeen: manufacturing downtime averages $260,000/h | ReliaMag, itsupplychain.com (secondhand); the original Aberdeen report was not opened and is likely about 2016 | Unverified. Older than 2022 |
| Aberdeen: FTF of 88% best-in-class, 80% average, 63% laggards | PTC blog and other vendor blogs (PTC page returned 403) | Unverified. Older. Aquant 2026 (#10) supersedes it |
| Aberdeen: 33% of dispatches need a second trip, 19% because of insufficient information | Vendor blog search snippet | Unverified |
| Truck roll cost: $150 to $500 (SightCall), $200 to $300 (CareAR), about $1,000 (TSIA) | Smarty.com article (vendor blog, undated) repeats all three: https://www.smarty.com/articles/truck-roll-costs | The blog is verified as saying it; the TSIA original was **not found**. Use only as a $150 to $1,000 range |
| Technician day: 28% wrench time, 22% travel, 17% waiting, and so on | SEO / vendor blog snippet (oxmaint / reliamag) | Unverified. Do not use |
| McKinsey: frontline managers spend 30 to 60% of their time on admin work and meetings | Search snippet; McKinsey page timed out; from a **2009** survey | Unverified. Older than 2022 |
| Honeywell: an average DC loses about $20k/h; "$50k to $250k/h" from Intelligrated customer feedback | Search snippets only | Unverified. Conflicts with the verified ">$10k/h" (#6) |
| DeHoratius & Raman (Management Science 54(4), 2008): 65% of about 370,000 inventory records across 37 stores were inaccurate | Abstract seen in search snippets (IDEAS/RePEc, INFORMS) | Unverified (paper not opened). **2008** |
| WERC DC Measures: best-in-class inventory count accuracy by location of 99.5% or better | Vendor blog snippet; the WERC 2025 report (released Sep 18, 2025) is gated | Unverified |
| Locus Robotics Director of Field Services: 40 to 60% travel; Formic: "customers pay nothing for downtime" | Search snippets | Unverified |
| AMR fleet "6.8 stoppages/week" and "MTTR 47 to 11 min" case studies | Oxmaint content-marketing pages | Not credible enough. Do not use |

### Not found (honest gaps)
- **A rigorous, recent survey of how much time dispatchers or supervisors spend on manual coordination** (phone calls, chasing ETAs). Only proxies were found: the 21:1 tech-to-dispatcher ratio (2019) and the McKinsey 2009 admin-time figure.
- **Time from alarm to dispatch** as a published benchmark. The nearest number is Siemens' 81-minute average from stoppage to restart (#4).
- **Annual downtime hours for warehouses** (as opposed to manufacturing plants). Only "6 or more events/yr" for 80% of facilities (#9) was found.
- **Independent AMR intervention rate or MTTR data.** Only vendor claims were found (Vecna, under 1% local assist).
- **Public dollar values for missed SLAs or RaaS credits.** Contracts mention guarantees and credits (Vecna, Brightpick) but publish no numbers.
- **Verified WERC inventory-accuracy values** (gated).

### Conflicts and ranges
- **$/hour of downtime for a distribution center:** about $2,350/h counting idle labor only (#7, calculation) to more than $10k/h for an average DC (#6). Siemens' $36k/h (#1) is a large FMCG *manufacturing* plant, and $260k/h (Aberdeen, unverified) is all manufacturing. **Use $10k/h as the DC anchor and show the others as context only.**
- **Average FTF:** 77% (Aquant 2026, from work-order data) vs 80% (Aberdeen, older and secondhand). Use Aquant.
- **Truck roll:** $150 to about $1,000+, depending on whether indirect costs are counted. No primary source was verified.

---

## 2. CALCULATION: illustrative per-site annual value of ShiftLead (mid-size robotic warehouse)

**This is my own calculation, not a sourced figure.** Every input is either traced to a finding (#) above or marked **ASSUMPTION**.

**Site (ASSUMPTION):** one mid-size robotic warehouse with 20 AMRs (matches the demo), 2 shifts/day x 8 h, 260 operating days/yr (4,160 operating h/robot/yr).

**What ShiftLead changes (ASSUMPTION about the mechanism):** it doesn't prevent failures. It shortens the time from alarm to the right person arriving, cuts the coordination work (work order, picking who goes, ETA chasing, shift summary), and raises first-time fix by sending the right skill with the right context.

### Inputs

| Input | Conservative | Mid | Aggressive | Source / basis |
|---|---|---|---|---|
| A. Throughput-affecting incidents per year | 6 | 24 | 60 | 6 = MultiSensor threshold, "six or more" events for 80% of facilities (#9). 24 and 60 are **ASSUMPTIONS** (Siemens large plants average 300/yr, #3; not applied to a DC) |
| B. Minutes of response time saved per incident | 10 | 20 | 32 | **ASSUMPTION**. 32 = the full 49 to 81 min recovery-time gap that Siemens partly blames on lost skilled labor (#4) |
| C. Downtime hours avoided/yr (A x B / 60) | 1.0 | 8.0 | 32.0 | calculation |
| D. Cost per downtime hour | $2,353 | $10,000 | $36,000 | Conservative: idle labor only, $40k / 17 h (#7). Mid: "average DC can be more than $10k per hour" (#6). Aggressive: Siemens FMCG large plant (#1); an **upper bound** for a DC |
| E. Dispatchable events/day (robot assists, faults, inventory mismatches) | 5 | 10 | 20 | **ASSUMPTION**. Sanity check: Vecna's best-in-class "<1% local assist" rate (#19) x 20 robots x 4,160 h is about 832 robot-hours/yr of local assists (calculation) |
| F. Coordination minutes saved per event | 3 | 5 | 8 | **ASSUMPTION** (no published time-and-motion data found) |
| G. Shift-summary minutes saved per shift (x 2 shifts) | 10 | 20 | 30 | **ASSUMPTION** |
| H. Supervisor/dispatcher hours saved/yr ((E x F + 2 x G) x 260 / 60) | 151.7 | 390.0 | 953.3 | calculation |
| I. Loaded labor rate | $44.03/h | $44.03/h | $44.03/h | BLS median $30.82/h for industrial machinery mechanics (#15) divided by 0.70 wage share (#17). A proxy: supervisor pay is likely higher, so this is conservative |
| J. On-site vendor technician visits/yr | 12 | 24 | 52 | **ASSUMPTION** |
| K. First-time-fix gain (percentage points) | +3 (77% to 80%) | +6 (77% to 83%) | +11 (77% to 88%) | Baseline 77% and top 88% from Aquant 2026 (#10). The size of the gain is an **ASSUMPTION** |
| L. Repeat visits avoided/yr (J x K x 1 repeat per failed fix) | 0.36 | 1.44 | 5.72 | calculation (1 repeat per failure is an **ASSUMPTION**) |
| M. Cost per truck roll | $300 | $600 | $1,000 | $150 to $500 / $200 to $300 / about $1,000 from vendor blogs (unverified table). $600 is an **ASSUMPTION** (midpoint) |

### Result (calculation)

| Value line | Conservative | Mid | Aggressive |
|---|---|---|---|
| Downtime avoided (C x D) | $2,353 | $80,000 | $1,152,000 |
| Supervisor/dispatcher time (H x I) | $6,678 | $17,171 | $41,974 |
| Repeat truck rolls avoided (L x M) | $108 | $864 | $5,720 |
| **Total per site per year** | **about $9.1k** | **about $98k** | **about $1.2M** |
| Share from downtime | 26% | 82% | 96% |

**Reading the result:**
- **The value comes almost entirely from downtime minutes.** The result is far more sensitive to D ($/h) and B (minutes saved) than to anything else. If the aggressive case uses $10k/h instead of $36k/h, its downtime line drops from $1.15M to $320k.
- **Break-even framing (calculation):** at the >$10k/h average DC (#6), **each avoided downtime hour (for example 3 incidents x 20 min) covers about $10k of annual ShiftLead cost.** This rule of thumb is more defensible than any single ROI total.
- **Truck-roll savings are small per site but matter to the robot vendor**, who pays for the visits and owes the uptime guarantees (#19, #20). For a vendor with 100 sites in the mid case: 100 x 1.44 = 144 repeat visits avoided, about $86k/yr (calculation). This points to robot vendors and RaaS providers as a second buyer.
- **Robot rent isn't where the value is:** $1,900 to $2,200 per robot-month (#20) over about 347 operating h/month is about $5.50 to $6.35 per robot-hour (calculation). An idle robot is cheap. An idle *site* (people, orders, cutoffs) is what costs $2k to $10k+/h.

---

## 3. Recommendations: which numbers belong on the pitch slide

- **Lead with the Siemens "81 minutes" number. It is ShiftLead's problem, measured:** "Getting production back after a stoppage now takes 81 minutes, up from 49 in 2019, and Siemens blames part of that on lost skilled maintenance labour" (Siemens TCOD 2024, #4). Pair it with "the average DC loses more than $10k per hour of downtime" (Honeywell Intelligrated, #6). Avoid $2.3M/h automotive and the unverified $260k/h Aberdeen figure. Judges will see them as cherry-picked for a warehouse wedge.
- **Shortage line (government source): "About 51,900 openings a year for industrial machinery mechanics through 2035, +14%, mostly replacing retirees" (BLS OOH 2026, #15).** Back it with "35% of e-commerce/logistics facilities say too few skilled technicians is a top barrier to uptime" (MultiSensor/Censuswide, Sep 2026, #9). Together they make the case: make every technician trip count.
- **Robotics wedge line: even best-in-class robots need people.** Vecna advertises a local-assist rate under 1% of operating time (#19). That is still about 832 robot-hours/yr of human assists for a 20-robot fleet (calculation), and each one is a dispatch decision. Robot vendors' field engineers travel "up to 85%" (HAI Robotics, #21). Field service FTF averages 77% vs 88% for top performers, and failed visits make up 25% of service cost (Aquant 2026, #10, #11).
- **ROI slide: show the mid case (about $98k/site/yr, 82% from avoided downtime) labeled "illustrative, assumptions shown"**, plus the rule of thumb "1 avoided downtime hour is about $10k". Keep the aggressive case ($1.2M) off the slide or in a footnote. The conservative case (about $9k) is worth showing in Q&A, because it shows the value depends on response-time minutes, which is exactly what ShiftLead targets.
- **Put "who pays" on the business-model slide:** per-site truck-roll savings are small, but the robot vendor or RaaS provider carries the visits and the uptime guarantees across many sites. That supports selling to robot vendors as well as site operators. Leave inventory shrink (NRF 1.6% of sales, FY2022) on a secondary "transferability" slide: it is retail data, not warehouse-robot data.
