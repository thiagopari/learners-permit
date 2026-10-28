# Learner's Permit

> A Nemotron agent may command a GR00T skill only after Nebius-run trials prove it, only within the conditions
> tested, and it loses the licence the moment live results slip.

*Other robot agents ask when they're unsure; ours asks when it's unproven.*

Built for the **Nebius × NVIDIA Global AI Hackathon**, Physical AI track. All robot footage and results are from
**simulation** (NVIDIA Isaac Sim through RoboLab) on a Nebius GPU; there is no physical robot. It grows out of
**Hyperion** (Oct 3, 2026; see [Prior work](#prior-work)).

## Why
Vision-language-action (VLA) robot policies succeed on roughly 75–95% of sorting and kitting tasks in published
results; production picking expects about 99.9%. Someone has to decide which skills an AI may trigger, on what, and
for how long. Learner's Permit makes that decision in code, from evidence:

- **Earned.** The AI may command a skill only after a Nebius-run evaluation sweep shows, with 95% confidence, that it
  succeeds at least 80% of the time (a Bayesian sequential test). An *unattended* tier needs 99%: 298 straight
  successes.
- **Scoped.** A licence covers only the conditions tested (today: the commanded speed).
- **Revocable.** It's pulled automatically when live results slip. A Cosmos Reason 2 check that also suspends it when
  the scene changes is built and tested with a stand-in model, but **has not yet run on Nebius**.
- **Enforced, not prompted.** One Cedar policy decides every API request that can move the robot: `POST /run` (and
  the AI's `/orders` and `/agent/run`, which go through it) and the supervisor's commissioning trials. The requester's
  role comes from the session, never from the LLM. (Evaluation scripts run by someone with a shell on the GPU VM,
  like `cloud/measure.py`, drive RoboLab directly; the AI has no way to reach them.)

## What we measured (our own runs, Nebius RTX PRO 6000, Oct 24–28, 2026)
Zero-shot **GR00T N1.7-DROID** driving a simulated Franka arm in Isaac Sim 5.0 through NVIDIA's RoboLab, every
episode recorded (none dropped for finishing late):

| Task (RoboLab) | Scene | Episodes | Successes | P(rate ≥ 80%) | Licence |
|---|---|---|---|---|---|
| Bananas in the bin (`BananasInBinThreeTotalTask`) | default | 40 | **37** (92.5%) | 0.976 | **licensed** |
| Red dishes in the bin (`RedDishesInBinTask`) | default | 40 | **14** (35%) | ≈ 0 | **refused** |
| Bananas in the bin | random background, seed 1 | 20 | **20** (100%) | | |
| Bananas in the bin | random background, seed 2 | 20 | _TBD_ | | |

- NVIDIA's RoboLab README reports 38/40 and 15/40 for the first two; ours match closely, but they are our numbers.
- **Cost:** 40 episodes took 11.2 minutes on one RTX PRO 6000 at $1.80/h: **$0.34, or $8.40 per 1,000 episodes.**
- Reliability varies wildly from task to task (92.5% vs 35% here), which is why licences are per skill.
- A randomized background did **not** lower GR00T's success on bananas, so the drift revocation correctly never
  fired; we have no measured scene that makes the licensed skill fail.
- Every number in this table is from a real run. The offline demo (`demo/four_beats.py`) uses coin flips at these
  rates and says so on every line; it is not robot evidence.

## How it works
```
person ─order─▶ Nemotron planner ─skill calls─▶ POST /run ◀── the only path to the robot
                (Token Factory)                  │ Cedar: role × skill × object × bin × speed × hours × person in cell
                                                 │ licence: proven for this scope? (the trust gate, on Nebius sweeps)
                                                 │ Tavily datasheet: can only BLOCK (too heavy → denied, source cited)
                                                 ▼
                                  GR00T N1.7-DROID in Isaac Sim (RoboLab), Nebius RTX PRO 6000
                                                 │ live results ──▶ drift revokes the licence
                                                 │ Cosmos Reason 2 ──▶ a changed scene suspends it (not yet run on Nebius)
                                                 ▼
                       Nemotron explains every refusal, block and revocation to the supervisor
```
Rules the code enforces (`permit/`, tested in `tests/`; CI runs them on every push):
- **Identity:** the planner sees only the skill catalogue; any role, approver or extra argument it emits is dropped.
- **Approvals:** a supervisor's approval is single use, bound to one exact command, repeat count and person, and
  lasts 10 minutes.
- **Requesters:** the AI works only for people whose own role may request work.
- **Modes:** the AI never changes modes or speed limits, even with an approval.
- **Fail closed:** missing context means deny; a person in the cell caps everyone at 25% speed.
- **Outside evidence can only narrow:** a Tavily datasheet can block a pick, and a Cosmos scene check can suspend a
  licence; neither can ever allow anything.
- **Every no is explained, and the explanation can't lie about numbers:** Nemotron sees only audit facts (never the
  order text or web page text). An answer that quotes a number not in those facts, or gives a person a licence that
  belongs to a skill, is replaced by a template, and no explanation can change a decision.

## NVIDIA models used
| Model | Role | Where it runs |
|---|---|---|
| **Nemotron-3-Super-120B-A12B** (`nvidia/nemotron-3-super-120b-a12b`) | Planner (tool calling over the skill catalogue) and explainer | Nebius Token Factory |
| **GR00T N1.7-DROID** | The robot skill: a VLA policy driving a simulated Franka | Nebius AI Cloud, RTX PRO 6000 VM |
| **Cosmos-Reason2-2B** | Scene check: is the cell still the scene the licence was earned in? | Built to run on the same Nebius VM (`cloud/cosmos_server.py`; it isn't on Token Factory). **Not yet run on Nebius**: tested with a stand-in model only |

## Nebius services used
- **Token Factory:** every planner and explainer call, at runtime. OpenAI-compatible, so the `openai` client works
  with a new `base_url`; explanations run with reasoning off (1.3 s instead of 3–4 s).
- **AI Cloud Compute:** an RTX PRO 6000 Blackwell (96 GB) VM in uk-south2 runs GR00T and Isaac Sim (only RTX-class
  GPUs have the RT cores Isaac Sim needs). `cloud/vm.sh` creates it with `--recovery-policy fail` and a 30-minute idle
  guard, and spot runs are capped by a Nebius pricing policy (`cloud/price_cap.sh`).
- **Serverless AI Jobs:** `cloud/job.sh` packages a commissioning sweep as a job that checkpoints to Object Storage
  after every batch and resumes after preemption. Built and tested with a mock runner; not yet run on Nebius.

## Status (Oct 28, 2026)
- **Real and tested on Nebius:** Nemotron planner and explainer (Token Factory), Tavily datasheet check, GR00T N1.7 +
  Isaac Sim + RoboLab episodes through our runner, the baseline measurements above.
- **Built and tested with fakes, not yet run on Nebius:** the Cosmos Reason 2 server and scene check, the Serverless
  Job.
- **Not built:** fine-tuning GR00T (the "earn" beat uses a narrower scope instead), a physical robot.

## Run it
**Any machine, no GPU, no keys** (offline stand-ins for Nemotron and Tavily; coin-flip trials):
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q tests
.venv/bin/python demo/four_beats.py        # refuse → earn → block → revoke, on labelled stand-in trials
.venv/bin/python -m permit.server          # console at http://127.0.0.1:8099
```
**With real Nemotron and Tavily:** copy `.env.example` to `.env` (git-ignored) and fill in `NEBIUS_API_KEY` (Token
Factory) and `TAVILY_API_KEY`. The demo and server pick them up; the block beat then looks up a real part.

API calls (demo session tokens: `demo-sue` supervisor, `demo-olga` operator, `demo-max` maintenance):
```bash
curl -X POST localhost:8099/commission -H 'Authorization: Bearer demo-sue' -d '{"skill":"bananas_in_bin"}'
curl -X POST localhost:8099/orders -H 'Authorization: Bearer demo-olga' -d '{"text":"Put the bananas in the bin"}'
```
**On a Nebius GPU** (from Linux or WSL, with the `nebius` CLI and `NEBIUS_PROJECT_ID` and `HF_TOKEN` in `.env`):
```bash
cloud/vm.sh create      # RTX PRO 6000 VM with the idle guard (billing starts)
cloud/vm.sh setup       # GR00T N1.7, Isaac Sim 5.0, RoboLab; ends with 2 real episodes
cloud/vm.sh measure     # the table above, in tmux (about 1 h)
cloud/vm.sh record      # episodes with video; cloud/vm.sh dashboard replays them at localhost:8080
cloud/vm.sh cosmos      # Cosmos Reason 2 for the scene check (python -m permit.server --runner robolab --scene-check)
cloud/vm.sh stop        # a stopped VM bills only its disk; cloud/vm.sh delete removes it
```
The setup is hardened against what broke on a real VM: Isaac Sim's missing `libGLU`, NVIDIA's DCGM holding port 5555
(GR00T serves on 5600), a RoboLab bug in random backgrounds, and more; see `git log cloud/`.

## Repo map
| Path | What |
|---|---|
| `permit/` | **New:** the control plane (`server.py`), Cedar policy, the trust gate (`gate.py`), licences, Nemotron planner and explainer, Tavily check, Cosmos scene check, runners |
| `console/`, `demo/`, `tests/` | **New:** licence console, four-beat demo (offline, labelled stand-ins), tests |
| `cloud/` | **New:** the Nebius GPU VM (`vm.sh`, `setup_vm.sh`, idle guard, spot price cap), `measure.py`, the Cosmos server, the Serverless Job (`job.sh`, `job/`) |
| `docs/FEEDBACK.md` | Our feedback on Token Factory, AI Cloud and the NVIDIA tools |
| everything else | Hyperion (prior work): [docs/hyperion-README.md](docs/hyperion-README.md), [docs/hyperion-gb10-readme.md](docs/hyperion-gb10-readme.md) |

## Prior work
Hyperion, an AI ops supervisor for a simulated 20-robot warehouse, was built on **2026-10-03** at the Dell × NVIDIA
GB10 hackathon in Boston by Thiago Pari, Ferbin, Megha and Amal; its public upload, with that commit history, is
[github.com/mochi-bunny/navfix](https://github.com/mochi-bunny/navfix). Its one idea we carry forward is a
statistical trust gate deciding which robot skills an agent may use. In Hyperion that gate lived only in the LLM's
prompt: nothing read its result at runtime.

Learner's Permit is new work from the submission period, by this team (_TODO: list the three team members_):
- **The trust gate, rewritten from scratch** (`permit/gate.py`, our own code; Hyperion's `cell/bandit.py` isn't used),
  with 80% and 99% tiers and resumable sweeps.
- **Enforcement in code:** one `POST /run` choke point with Cedar policies; the gate's result is checked on every run.
- **Per-skill, per-scope licences** that drift and scene changes revoke.
- **Nemotron on Token Factory** as planner and explainer; the **Tavily** datasheet check.
- **GR00T N1.7-DROID in Isaac Sim** through RoboLab on Nebius, with the measurements above; the **Cosmos Reason 2**
  scene check; the Nebius VM tooling and the Serverless Job.

## License
Apache-2.0 for this repository's code. No model weights are included; GR00T, Cosmos and Nemotron are under NVIDIA's
model licenses.
