# Devpost: paste-ready text

Every number below is from a real run in this repo (see the README). Fields are in the order the form asks for them.

**Project name:** Learner's Permit

**Elevator pitch:** An AI may command a robot skill only after Nebius-run trials prove it, only where it was tested,
and only until the evidence changes.

**Team:** Gnana Shishir Kumar Chintapalli, Megha Manoj, Thiago Pari ·
**Track:** Physical AI · **City:** Boston · **Bonus prize:** Best Use of Tavily

**Links:** https://github.com/thiagopari/learners-permit · video: the public YouTube link

**About the project** (paste everything between the lines)

---
## Inspiration
Vision-language-action robot policies succeed on roughly 75–95% of sorting and kitting tasks in published results;
production picking expects about 99.9%. Our own runs of NVIDIA's GR00T N1.7 make the gap concrete: bananas into the
bin 37 times in 40, red dishes only 14 times in 40. An AI agent that can call either skill needs someone to decide
which skills it may trigger, on what, and for how long. We wanted that decided in code, from evidence, not in a prompt.

## What it does
A Nemotron agent turns a person's order into skill calls, and every call goes through one endpoint, `POST /run`, the
only path to the robot. There:
- a **Cedar** policy checks the person's role, taken from the session, never from the LLM;
- a **licence** check asks whether this skill has earned the right to run in this scope. A licence is issued only when
  a Nebius evaluation sweep shows, with 95% confidence, that the skill succeeds at least 80% of the time;
- outside evidence can only narrow a licence: **Tavily** finds a part's datasheet (too heavy: blocked, source cited) or
  an official recall notice (recalled: blocked, notice cited);
- after each run, **Nemotron-3.5-Super-VL** compares the camera frame with the one the licence was earned on. A changed
  scene revokes the licence, and so do live results that slip.

Then the agent goes back to asking a person, and Nemotron explains every no in plain English.

## How we built it
- **Nemotron-3-Super-120B on Nebius Token Factory:** the planner (OpenAI-style tool calling over a skill catalogue) and
  the explainer. Explanations are grounded: Nemotron sees only audit facts, and an answer quoting a number not in
  them, or giving a person a licence that belongs to a skill, is replaced by a template.
- **GR00T N1.7-DROID in Isaac Sim 5.0 through NVIDIA RoboLab**, on a Nebius **RTX PRO 6000** VM (Isaac Sim needs RT
  cores). Every episode is counted, none dropped for finishing late. 40 episodes took 11.2 minutes: $8.40 per 1,000
  episodes.
- **The trust gate:** a Beta-Bernoulli posterior with Thompson-sampling allocation across candidate policies.
  13 straight successes are enough for the 80% tier; the unattended 99% tier needs 298.
- **Cedar** at a single choke point; single-use supervisor approvals bound to one exact command.
- **Tavily, twice, both block-only:** search + extract for part datasheets, and search over official recall sites
  (CPSC, FDA, NHTSA...) for a notice that names the item. A page counts only if it names the part; on 7 real items it
  was right 7 times, blocking exactly the 3 under recall.
- **A vision scene check, chosen by measurement:** on our own frames, Cosmos-Reason2-2B (served on our Nebius VM)
  raised a false alarm on an unchanged scene 3 times in 3. Nemotron-3.5-Super-VL on Token Factory got 8/9 right with
  no false alarms, so it does the check.
- **Nebius Serverless AI Jobs:** the sweep packaged as a job that checkpoints to Object Storage and resumes after
  preemption. On Oct 28 it ran 4 batches of 20 real GR00T episodes on an RTX PRO 6000: 71/80, licensed, in 28.8
  minutes, at $10.80 per 1,000 episodes.
- **Beyond robots:** the same gate licenses a leaf-diagnosis skill per crop. Few-shot Nemotron-3.5-Super-VL earned a
  licence for peppers (37/40) but not tomatoes (85/100). A ResNet-18 we fine-tuned on a Nebius GPU in 12 seconds
  earned both, and each licence is pinned to that model's hash.

## Challenges we ran into
All fixed, all in `git log cloud/`: Isaac Sim segfaulted on the Nebius image until we installed `libGLU`; NVIDIA's DCGM
monitor holds port 5555, GR00T's default; a RoboLab bug broke random backgrounds; Nemotron's default reasoning ate the
token budget of short explanations; Tavily matched a made-up part number to a 19.7 kg truck leaf spring until we
required the page to name the part.

## Accomplishments that we're proud of
- Reproduced NVIDIA's zero-shot baselines on our own Nebius runs (37/40 and 14/40, against RoboLab's reported 38/40
  and 15/40), and turned them into enforced, explained, revocable permissions.
- Earn, revoke, refuse end to end on Nebius, nothing mocked. After a background change GR00T still succeeded, but the
  vision check saw "floor changed from tiled to wooden flooring" and revoked the licence before the robot had a chance
  to fail. The success rate alone wouldn't have caught it: under that background GR00T scored 20/20.

## What we learned
Evidence-gated autonomy only works if the evidence is enforced where the agent calls the robot, and if every outside
signal (web, vision, live results) can only take permission away.

## What's next for Learner's Permit
- Earn, not only refuse: fine-tune GR00T on its own successful red-dish episodes (the dataset builder is in
  `cloud/finetune/`) so the refused skill can earn its licence.
- Scope licences by phrasing and object colour, and put a real arm behind the same `POST /run`.
- CropAI: licence a crop-disease skill per cultivar and lighting from real field photos, and revoke it when the season
  or the light changes.
---

**Built with:** nvidia-nemotron, nvidia-gr00t, nvidia-cosmos, isaac-sim, robolab, nebius-token-factory,
nebius-ai-cloud, nebius-serverless, tavily, cedar, python, pytorch

**If the form asks for prior work:** paste the [Prior work](../README.md#prior-work) section of the README.
**If it asks for feedback on the sponsors' tools:** paste [FEEDBACK.md](FEEDBACK.md).
