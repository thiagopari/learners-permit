# Learner's Permit

> A Nemotron agent may command a GR00T skill only after Nebius-run trials prove it, only within the conditions
> tested, and it loses the licence the moment live results slip.

Built for the **Nebius × NVIDIA Global AI Hackathon** (Physical AI track). It grows out of **Hyperion**, an AI ops
supervisor for robot fleets built on 2026-10-03 (see [Prior work](#prior-work)).

## Why
Published robot policies that turn vision and language into actions (VLA policies) reach roughly 75–95% on
sorting and kitting; production picking expects about 99.9%. Someone has to decide which skills an AI may
trigger, on what, and for how long. Here that decision is made in code and backed by evidence:

- **Licences are earned.** A skill is commanded by the AI only after an evaluation sweep shows
  P(success rate ≥ 0.8) ≥ 0.95. That is a Bayesian sequential test: Hyperion's gate, `cell/bandit.py`, with one
  backward-compatible parameter added. An "unattended" tier needs P(rate ≥ 0.99), which takes 298 straight successes.
- **Licences are scoped.** They cover only the conditions that were tested; today that's the commanded speed.
- **Licences are revocable.** Once live runs slip, the licence is pulled automatically.
- **Roles are enforced, not prompted.** One Cedar policy at one endpoint. The role comes from the session,
  never from the LLM.

## How it works
```
person ─order─▶ Nemotron planner ─skill calls─▶ POST /run ◀── the only path to the robot
                (Token Factory)                  │ Cedar: role × skill × object × bin × speed × hours × person in cell
                                                 │ licence: proven for this scope? (gate on Nebius eval sweeps)
                                                 │ Tavily datasheet: can only BLOCK (too heavy → denied, source cited)
                                                 ▼
                                         GR00T N1.7 policy (Isaac Sim / RoboLab) ─live results─▶ revoke on drift
```
Rules the code enforces (`permit/`, tested in `tests/`):
- **Identity:** the planner sees only the skill catalogue. Any role, approver or extra argument it emits is dropped.
- **Approvals:** a supervisor's approval is a single-use token, bound to one exact command, repeat count and person,
  and valid for 10 minutes.
- **Requesters:** the AI works only for people whose own role may request work, so maintenance can't use it to
  launder a pick their role forbids.
- **Modes:** the AI never changes modes or speed limits, even with an approval.
- **Fail closed:** missing context means deny. A person in the cell caps everyone at 25% speed.
- **The web can only narrow:** a datasheet can block a pick but never allow one.

## Run it (any machine, no GPU, no keys)
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q tests        # 62 tests
.venv/bin/python demo/four_beats.py        # refuse → earn → block → revoke (mock runner)
.venv/bin/python -m permit.server          # console at http://127.0.0.1:8099
```
API calls (demo session tokens: `demo-sue` supervisor, `demo-olga` operator, `demo-max` maintenance):
```bash
curl -X POST localhost:8099/commission -H 'Authorization: Bearer demo-sue' -d '{"skill":"bananas_in_bin"}'
curl -X POST localhost:8099/orders -H 'Authorization: Bearer demo-olga' -d '{"text":"Put the bananas in the bin"}'
```
Optional real services:
- `NEBIUS_API_KEY` switches the planner to Nemotron on Token Factory (`NEMOTRON_MODEL`, default `nvidia/nemotron-3-super-120b-a12b`).
- `TAVILY_API_KEY` turns on the datasheet check.
- Without them, the server says so and uses offline stand-ins.

## Status (2026-10-04)
- **Done:**
  - Control plane: `permit/server.py`, plus the Cedar policy and its tests.
  - Licences on Hyperion's gate (cap raised from 40 to 100 trials).
  - Nemotron planner client and Tavily check.
  - Console, mock runner, and the four-beat demo.
- **Next (Linux laptop + Nebius):**
  - The RoboLab runner with GR00T N1.7-DROID.
  - Reproduce the zero-shot baselines.
  - Nebius eval sweeps and the fine-tune.
- **Read next:** [docs/LINUX_HANDOFF.md](docs/LINUX_HANDOFF.md). Plan, budget and cut lines: [docs/PLAN.md](docs/PLAN.md).

## Repo map
| Path | What |
|---|---|
| `permit/` | **New:** Learner's Permit control plane, Cedar policy, licences, planner, Tavily check, runners |
| `console/`, `demo/`, `tests/` | **New:** licence console, four-beat demo, 62 tests |
| `cloud/` | **New:** the Nebius GPU VM: `vm.sh` (create, setup, stop) from the laptop, an unattended setup, and an idle guard |
| `cell/bandit.py` | Hyperion's commissioning gate, reused (plus a `min_trials` parameter for the 99% tier) |
| everything else | Hyperion (prior work): repo map in [docs/hyperion-README.md](docs/hyperion-README.md), the GB10 submission README in [docs/hyperion-gb10-readme.md](docs/hyperion-gb10-readme.md) |

## Prior work
Hyperion was built on **2026-10-03** at the Dell × NVIDIA GB10 hackathon in Boston by Thiago Pari, Ferbin, Megha
and Amal. The hackathon window opened Aug 26, and the commit history records the dates. All four agreed to
open-source it.
The team's own public upload of the same code, with its Oct 3 commit history, is
[github.com/mochi-bunny/navfix](https://github.com/mochi-bunny/navfix).

New in Learner's Permit:
- Enforcing the gate in code (in Hyperion it was only a prompt).
- Cedar RBAC at a single choke point.
- Per-skill, per-scope licences with drift revocation.
- The Nemotron planner on Token Factory, and the Tavily datasheet check.
- GR00T N1.7 skills in Isaac Sim with Nebius evaluation.

## License
Apache-2.0 for this repository's code. No model weights are included; GR00T and Nemotron are under NVIDIA's
model licenses.
