# ShiftLead business model research: shared brief

Read this first. Every research track works from it.

## The event
Dell Technologies x NVIDIA "Dell Pro Max with GB10" hackathon run by BuilderBase, Boston, Saturday Oct 3 2026.
40 teams, one day, code freeze 18:00 ET, top 8 pitch live to a Dell/NVIDIA judging panel. Requirement: an
always-on business agent that runs 100% locally on the Dell Pro Max with GB10 (no cloud LLM calls at runtime),
on the NemoClaw + OpenClaw + OpenShell stack, wired into a real channel (Discord), using tools without a human
driving each step, and targeting a real business workflow.

## The product: ShiftLead
An AI operations supervisor for physical operations: work where fixing a problem means a person has to physically
get somewhere. The loop it closes:

  detect -> decide who -> get them there -> verify the fix -> summarize

- Detect: code watches an operational data feed and flags problems (thresholds, stuck assets, errors,
  inventory mismatches, throughput drops, deadline risk).
- Decide who: the right person is qualified, available and can arrive before the deadline, accounting for their
  current location and commute/travel time (transit and traffic).
- Get them there / verify / summarize: tickets with a state machine and evidence, ETAs, a trust gate that only
  accepts a fix (or a new process, route, vendor, robot skill) when evidence says P(success rate >= 80%) >= 95%,
  and shift summaries of inventory status plus an action plan.
- Design rule: code enforces, the model explains. Thresholds, assignment, travel times and trust decisions are
  computed in code; the local LLM (Qwen3.6-35B-A3B, NVFP4, served by vLLM on the GB10) decides what to say, what to
  escalate and how to route, never the safety call itself.
- Why local: operations data, video, and where employees are all day never leave the site.

## Framing (decided)
- Umbrella / vision: the ops supervisor for physical operations, any industry where people must physically get there.
- Wedge / first deployment: robotics. The demo is a 20-robot simulated warehouse; GR00T N1.7 robot policies run on
  the same box and are commissioned through the trust gate. Robots have structured telemetry, and robot companies
  have scarce, expensive field engineers who travel between customer sites.
- Proof of transferability: a generic core (event engine, tickets, people/travel assignment, trust gate, briefs)
  plus per-industry adapters (data connectors, detectors, vocabulary).
- Honest gap claim (to verify, not assume): monitoring tools already detect problems, and field service tools
  (e.g. Salesforce Field Service) already schedule around skills and travel time. The gap is the handoff between them:
  today a person notices the alarm, creates the work order, picks who goes and chases the ETA.
- Working business model hypothesis: a per-site appliance (one Dell Pro Max GB10 per site, sold via Dell's channel)
  plus a software subscription per site, with industry packs (detectors + connectors) on a shared core.

## Rules for every track
1. Every number needs a source URL, the publisher, the publication date, and a short exact quote or table cell
   that contains it. Prefer primary sources (government statistics, company pricing pages, filings, official docs,
   the original survey) over blogs that repeat them. If a number appears only in a vendor blog or an SEO
   market-research summary, say so.
2. Never invent or estimate a number and present it as sourced. If you could not find something, say "not found".
   Clearly label any of your own calculations as calculations, with inputs shown.
3. Mark each finding: verified (you opened the page and saw the number) or unverified (seen only in a search
   snippet or secondhand).
4. Note conflicts between sources and give ranges rather than picking the most dramatic number.
5. Today is 2026-10-03. Prefer the most recent data; flag anything older than 2022.
6. Read-only on this machine except your own output file. Do not touch ~/hack/src, ~/warehouse, ~/hack/pitch,
   Docker containers or the NemoClaw sandbox; other sessions are actively working there.
7. Time box: about 20 minutes of research. Quality over volume: 8-15 strong, sourced findings beat 40 weak ones.
8. Write your full findings to your track file in /home/dell/hack/business/research/, then return a concise summary
   (under ~700 words) with the key numbers, sources and your recommendation for the pitch.
