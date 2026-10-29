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
- **Tavily**, twice, both block-only: search + extract for part datasheets (too heavy → blocked), and search over
  official recall sites (CPSC, FDA, NHTSA...) for a notice that names the item (recalled → blocked, notice cited).
  A page counts only if it names the part; on 7 real items, exactly the 3 under recall were blocked.
- **A vision scene check** compares each live run's scene with the one the licence was earned in. We measured
  Cosmos-Reason2-2B (served on our Nebius VM) against Nemotron-3.5-Super-VL (Token Factory) on our own frames: Cosmos
  raised false alarms on an unchanged scene 3 times in 3, so the check uses Nemotron-3.5-Super-VL (8/9, no false
  alarms).
- **Nebius Serverless AI Jobs:** the sweep packaged as a job that checkpoints to Object Storage and resumes after
  preemption (it ran on Nebius on Oct 28: 4 batches of 20 real GR00T episodes on an RTX PRO 6000, 71/80, licensed, $10.80 per
  1,000 episodes).

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
and object colour; a real arm behind the same `POST /run`. And beyond robot arms: the gate licenses any model's skill
within the conditions it was tested in: we already license a few-shot crop-disease skill per crop (Nemotron-3.5-Super-VL
on real PlantVillage photos: pepper 37/40, licensed; tomato 85/100, not yet). Next, CropAI: field photos, licensed per
cultivar and lighting, revoked when the season or the light changes.

**Built with:** nvidia-nemotron, nvidia-gr00t, nvidia-cosmos, isaac-sim, robolab, nebius-token-factory,
nebius-ai-cloud, nebius-serverless, tavily, cedar, python

**Prior work:** paste the [Prior work](../README.md#prior-work) section of the README.
**Feedback:** paste [docs/FEEDBACK.md](FEEDBACK.md).

## The video (under 3:00; the aha moment in the first 30 seconds)
Judges said (Oct 21): get to the aha moment fast. Label every robot shot **"Simulation: NVIDIA Isaac Sim"** on screen.
No third-party music or trademarks beyond the sponsors' own products.

| Time | Beat | On screen (all real; the source is in brackets) | Voice-over (draft) |
|---|---|---|---|
| 0:00–0:20 | **REFUSE** | Terminal: `python demo/four_beats.py` with real keys; "Put the red dishes in the bin" → DENY, *skill not licensed*, Nemotron's explanation; then the red-dishes sim clip [`results/clips/…RedDishes…mp4`, 14/40 in `docs/results/measurements.jsonl`] | "Olga asks the AI to clear the red dishes. It refuses: not because it's unsure, but because this skill hasn't earned a licence. On our own Nebius runs, GR00T managed 14 of 40." |
| 0:20–0:40 | The idea | Title card + the README's architecture diagram | "Learner's Permit: an AI may command a robot skill only after trials prove it, only where it was tested, and only until the evidence changes." |
| 0:40–1:15 | **EARN** | Bananas sim clip [`results/clips/…Bananas…mp4`]; licence card 37/40, P = 0.976; then the Serverless Job log: batches 16/20 → 71/80, licensed, $10.80 per 1,000 episodes [`docs/results/serverless-job-2026-10-28.log`] | "Bananas earned theirs: 37 of 40, 97.6% confident it succeeds at least 80% of the time. And the same sweep runs as a Nebius Serverless Job: 80 episodes, licensed, about a cent per episode." |
| 1:15–1:45 | **BLOCK** | Same terminal run: "The item is part Makita XFD131" → Tavily finds the spec sheet, 1.724 kg > 1.0 kg, denied with the source URL; then a Fisher-Price Rock 'n Play → Tavily finds the CPSC recall notice → denied, notice cited, Nemotron explains [`docs/results/recall-2026-10-29/`] | "The web can only narrow a licence. Tavily pulls the spec sheet: too heavy for this skill. And for an item under an official recall, Tavily finds the CPSC notice: blocked, with the notice cited." |
| 1:45–2:25 | **REVOKE** | The two real frames side by side, tiles then wood [`docs/results/e2e-revoke-2026-10-28/*.jpg`]; the log lines: vision check "floor changed from tiled to wooden" → licence revoked → next request denied, with Nemotron's explanation [`e2e.jsonl`] | "Then the scene changed. GR00T still succeeded, but the licence was evidence about the old scene, and the vision check saw the floor had changed. Licence revoked, before the robot had to fail. The agent goes back to asking a person." |
| 2:25–2:42 | Beyond robots | The crop table: few-shot Nemotron-VL (pepper 37/40 licensed, tomato 85/100 not) vs a ResNet-18 trained in 12 s on Nebius (both licensed, 119/120 and 80/80 held out) [`docs/results/crop-2026-10-29*/`] | "The same licence works for any model. Few-shot leaf diagnosis earned a licence for peppers but not tomatoes; a model we trained on Nebius earned both. Each licence is tied to that exact model." |
| 2:42–2:58 | Close | Logos: Nebius Token Factory and AI Cloud, Nemotron, GR00T, Tavily; repo URL | "Other robot agents ask when they're unsure. Ours asks when it's unproven." |

Don't show: the offline demo's coin-flip licence numbers as if they were robot runs (only its Nemotron and Tavily
parts are real), or Cosmos as the scene checker (it was measured and not used).

Show for at least a minute in total the key modules working (the rules' requirement for projects without hardware):
the console, `POST /run` decisions, the licence cards and the sim clips. Record the console from the four-beat demo
with real keys (`python demo/four_beats.py` and `python -m permit.server`), and the clips with `cloud/vm.sh record`.

## Before submitting
- [ ] Team on Devpost: Gnana Shishir Kumar Chintapalli, Thiago Pari, Megha (add Megha's surname in the README too)
- [ ] Background-run numbers filled into the README table (and the REVOKE beat matches what happened)
- [ ] Secret scan of the full history: `gitleaks detect --source . --log-opts="--all"` (config in `.gitleaks.toml`)
- [ ] The repo is public, with the Apache-2.0 license at the top
- [ ] Video public on YouTube, under 3 minutes
- [ ] After submitting: `cloud/vm.sh delete`, so the disk stops billing; keep Token Factory testable until Dec 15
