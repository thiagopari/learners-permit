# Submission kit: Devpost text and the video script

Track: **Physical AI.** City: **Boston** (a teammate attended Builders & Brews on Oct 2). Bonus: **Best Use of Tavily**.
Deadline: Oct 30, 2026, 10:00 AM PT; aim for Oct 29. Fill the TODOs, then paste.

## Devpost fields

**Name:** Learner's Permit

**Tagline:** An AI may command a robot skill only after Nebius-run trials prove it, only where it was tested, and only
until the evidence changes.

**What it does**
Robot skills learned from data (VLA policies) are good, not perfect: our own runs of NVIDIA's GR00T N1.7 on
RoboLab tasks put the bananas in the bin 37 times in 40, and the red dishes only 14 times in 40. So which skills may an
AI agent trigger, on what, and for how long? Learner's Permit answers that in code, not in a prompt. A Nemotron agent
turns a person's order into skill calls, and every call goes through one endpoint, `POST /run`, the only path to the
robot. There a Cedar policy checks the person's role (from the session, never from the LLM), and a licence check asks:
has this skill earned the right to run, in this scope? A licence is issued only when a Nebius evaluation sweep shows,
with 95% confidence, that the skill succeeds at least 80% of the time. Outside evidence can only narrow it: a Tavily
datasheet lookup blocks a pick that's too heavy, citing its source, and live results that slip, or a scene that Cosmos
Reason 2 sees has changed, revoke it. Then the agent goes back to asking a person, and Nemotron explains every no in
plain English.

**How we built it**
- **Nemotron-3-Super-120B on Nebius Token Factory:** the planner (OpenAI-style tool calling over a skill catalogue) and
  the explainer. Explanations are grounded: Nemotron sees only audit facts, and an answer quoting a number not in them,
  or giving a person a licence that belongs to a skill, is replaced by a template.
- **GR00T N1.7-DROID in Isaac Sim 5.0 through NVIDIA RoboLab**, on a Nebius **RTX PRO 6000** VM in uk-south2 (Isaac Sim
  needs RT cores). Every episode is counted, none dropped for finishing late. Cost: $8.40 per 1,000 episodes.
- **The trust gate:** a Beta-Bernoulli posterior with Thompson-sampling allocation; 16 straight successes license a
  skill at 80%, 298 at the unattended 99% tier.
- **Cedar** at a single choke point; single-use supervisor approvals bound to one exact command.
- **Tavily** search + extract for part datasheets; a page counts only if it names the part.
- **Cosmos Reason 2** (built and tested with a stand-in model; TODO: say whether it ran on Nebius) compares each live
  run's scene with the one the licence was earned in.
- **Nebius Serverless AI Jobs:** the sweep packaged as a job that checkpoints to Object Storage and resumes after
  preemption (built and tested with a mock; TODO: say whether it ran on Nebius).

**Challenges we ran into** (all fixed, all in `git log cloud/`): Isaac Sim segfaulted on the Nebius image until we
installed `libGLU`; NVIDIA's DCGM monitor holds port 5555, GR00T's default; a RoboLab bug broke random backgrounds;
Nemotron's default reasoning ate the token budget of short explanations; Tavily matched a made-up part number to a
19.7 kg Toyota leaf spring until we required the page to name the part.

**Accomplishments:** reproduced NVIDIA's zero-shot baselines on our own Nebius runs (37/40 and 14/40 vs 38/40 and
15/40), and turned them into enforced, explained, revocable permissions. Found that randomized backgrounds barely
degraded GR00T on bananas (20/20, 16/20), so the licence correctly stayed.

**What we learned:** evidence-gated autonomy only works if the evidence is enforced where the agent calls the robot,
and if every outside signal (web, vision, live results) can only take permission away.

**What's next:** fine-tune GR00T on scripted demos so a refused skill earns its licence; licences scoped by phrasing
and object colour; a real arm behind the same `POST /run`.

**Built with:** nvidia-nemotron, nvidia-gr00t, nvidia-cosmos, isaac-sim, robolab, nebius-token-factory,
nebius-ai-cloud, nebius-serverless, tavily, cedar, python

**Prior work:** paste the [Prior work](../README.md#prior-work) section of the README.
**Feedback:** paste [docs/FEEDBACK.md](FEEDBACK.md).

## The video (under 3:00; the aha moment in the first 30 seconds)
Judges said (Oct 21): get to the aha moment fast. Label every robot shot **"Simulation: NVIDIA Isaac Sim"** on screen.
No third-party music or trademarks beyond the sponsors' own products.

| Time | Beat | On screen | Voice-over (draft) |
|---|---|---|---|
| 0:00–0:25 | **REFUSE** | Console: Olga orders "put the red dishes in the bin"; the row turns red: *skill not licensed*; Nemotron's explanation appears under it | "Olga asks the AI to clear the red dishes. It refuses. Not because it's unsure: because this skill hasn't earned a licence. Our own Nebius runs: 14 successes in 40." |
| 0:25–0:50 | The idea | Title card + the architecture diagram from the README | "Learner's Permit: an AI may command a robot skill only after trials prove it, only where it was tested, and only until the evidence changes." |
| 0:50–1:30 | **EARN** | Sim clip of GR00T putting bananas in the bin; licence card: 37/40, P(rate ≥ 80%) = 0.976, $8.40 per 1,000 episodes; then the same order runs | "Bananas earned theirs: a sweep on a Nebius RTX PRO 6000, 37 of 40, 97.6% confident it succeeds at least 80% of the time. Now the agent may run it, at the speed it was tested at." |
| 1:30–2:05 | **BLOCK** | Order with part "Makita XFD131"; Tavily finds the spec sheet: 1.72 kg over a 1.0 kg limit; denied, source URL shown | "The web can only narrow a licence. Tavily pulls the spec sheet: too heavy for this skill. Blocked, with the source cited." |
| 2:05–2:45 | **REVOKE** | ONLY what really happened. Today: the background runs (20/20 and 16/20) next to the drift rule, then the console revoking on live failures, labelled "offline stand-in". If Cosmos runs on Nebius before recording, show its real verdict instead | "We changed the background: GR00T still succeeded 20 of 20 and 16 of 20, not enough evidence of a drop, so the licence rightly stayed. If live results do slip, the licence is pulled automatically and the agent goes back to asking a person." |
| 2:45–2:58 | Close | Logos: Nebius Token Factory, AI Cloud, Nemotron, GR00T, Cosmos, Tavily; repo URL | "Other robot agents ask when they're unsure. Ours asks when it's unproven." |

Show for at least a minute in total the key modules working (the rules' requirement for projects without hardware):
the console, `POST /run` decisions, the licence cards and the sim clips. Record the console from the four-beat demo
with real keys (`python demo/four_beats.py` and `python -m permit.server`), and the clips with `cloud/vm.sh record`.

## Before submitting
- [ ] TODO: team members in the README's Prior work, and on Devpost
- [ ] Background-run numbers filled into the README table (and the REVOKE beat matches what happened)
- [ ] Secret scan of the full history: `gitleaks detect --source . --log-opts="--all"` (config in `.gitleaks.toml`)
- [ ] The repo is public, with the Apache-2.0 license at the top
- [ ] Video public on YouTube, under 3 minutes
- [ ] After submitting: `cloud/vm.sh delete`, so the disk stops billing; keep Token Factory testable until Dec 15
