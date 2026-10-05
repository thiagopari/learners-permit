# Handoff: continue Learner's Permit on the Linux laptop

Written 2026-10-04 on the Mac. Deadline: **Fri Oct 30, 10:00 AM PT** (submit Oct 29).
Exact commands with sources are in [RUNBOOK.md](RUNBOOK.md); this page is the order to do things in.
Plan, budget and cut lines: [PLAN.md](PLAN.md).

## Where things stand
- **Done, and tested on any machine (52 tests):**
  - `permit/`: one `/run` choke point with the Cedar policy, licences on Hyperion's gate (cap 100, scope, drift
    revocation), single-use approvals bound to one command, the Nemotron planner client, and the Tavily
    datasheet check (block-only).
  - The console, and `demo/four_beats.py` (refuse → earn → block → revoke) running on the mock runner.
  - `runners.robolab`, which runs RoboLab and reads `episode_results.jsonl`. It's tested against a fake RoboLab;
    **it has never run against the real one.**
- **Not done:** everything that needs a GPU or API keys. That's this page.

## The one constraint that shapes everything
The laptop GPU is an **RTX PRO 2000 Blackwell with 8 GB**. GR00T inference needs 16 GB+, Isaac Sim 5.1 lists 16 GB
as its minimum, RoboLab recommends 48 GB, and RoboLab's TiledCamera hangs on laptop Blackwell chips. So:
- **GPU work** runs on a **Nebius RTX PRO 6000 VM** (96 GB, RT cores).
- **The laptop** does git, the control plane, scripts, SSH, and video editing.

## Step 0: clone and check (15 min)
```bash
git clone git@github.com:thiagopari/learners-permit.git && cd learners-permit
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q tests        # expect: 52 passed
.venv/bin/python demo/four_beats.py        # refuse → earn → block → revoke
```

## Step 1: accounts and keys (today)
Keep keys in `~/.config/learners-permit.env` (`chmod 600`), never in the repo:
```bash
NEBIUS_API_KEY=...        # Token Factory
TAVILY_API_KEY=tvly-...
HF_TOKEN=hf_...           # read token, after accepting the Cosmos-Reason2-2B gate
```
1. **Nebius AI Cloud:**
   - Add a card; this tops up $25 first.
   - Billing → Apply promo code (the $100 from the Oct 2 event).
   - Set a **budget alert**.
   - Create a project in **uk-south2 or eu-south1**.
   - Administration → Limits → Quotas: "Total NVIDIA RTX PRO 6000 GPUs" should read **32**. Cut line **Oct 8**.
2. **Token Factory:** Top up → promo code ($100), then create an API key.
3. **Tavily:** get a key at app.tavily.com (free for students).
4. **Hugging Face:** accept the gate at huggingface.co/nvidia/Cosmos-Reason2-2B (approval is automatic), then create a **Read** token.

## Step 2: smoke-test the real services from the laptop (30 min)
```bash
set -a; . ~/.config/learners-permit.env; set +a
# confirm the exact Nemotron model id (default: nvidia/nemotron-3-super-120b-a12b)
curl -s -H "Authorization: Bearer $NEBIUS_API_KEY" https://api.tokenfactory.nebius.com/v1/models | jq -r '.data[].id' | grep -i nemotron
.venv/bin/python -c "from permit import planner, server; print(planner.plan('Put the red dishes in the bin', server.Permit().skills))"
.venv/bin/python -c "from permit import datasheet; print(datasheet.check('<a real part number>', 1.0))"
.venv/bin/python demo/four_beats.py        # now with real Nemotron + Tavily
```
If the model isn't found, the model lists only us-central1, so try
`export TOKEN_FACTORY_BASE_URL=https://api.tokenfactory.us-central1.nebius.com/v1/`.
**This counts for the rules:** a runtime Token Factory call satisfies "runs on Nebius", and the Tavily call qualifies
for the bonus.

## Step 3: the Nebius GPU VM (cut line Oct 8)
RUNBOOK §5.2:
1. Install the CLI and create a profile.
2. Create the VM: `--resources-platform gpu-rtx6000-a --resources-preset 1gpu-24vcpu-218gb`, image family
   `ubuntu24.04-cuda13.0` (driver 580), 300 GiB disk.
3. `nvidia-smi` should show an RTX PRO 6000 with 96 GB.

Costs about $1.80/h, so **stop the VM whenever you're not using it**. A stopped VM still counts against quota.

## Step 4: GR00T + RoboLab on the VM, then reproduce the baselines (cut line Oct 9)
1. **GR00T (RUNBOOK §1.1–1.5):**
   - `git clone --recurse-submodules https://github.com/NVIDIA/Isaac-GR00T && uv sync --python 3.12`
   - `uv run hf auth login`
   - Start the server **with `--host 127.0.0.1`**; its default listens on every interface:
     ```bash
     uv run python gr00t/eval/run_gr00t_server.py --model-path nvidia/GR00T-N1.7-DROID \
       --embodiment-tag OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT --device cuda --host 127.0.0.1 --port 5555 --use-sim-policy-wrapper
     ```
2. **RoboLab (RUNBOOK §2.1–2.3):**
   - Install git-lfs **before** cloning.
   - `uv sync --extra isaac50` (plain `uv sync` installs no simulator).
   - Smoke test on `BananaOnPlateTask`, then run 40 envs of `BananasInBinThreeTotalTask` and `RedDishesInBinTask`.
3. **Done when:** your numbers are near NVIDIA's (about 38/40 and 15/40). **Write your numbers into PLAN.md and quote
   those**, not NVIDIA's. Physics differ between Isaac Sim 5.0 and 5.1, and on Blackwell.

## Step 5: Learner's Permit against real GR00T (cut line Oct 11, the must-ship)
On the VM, with the GR00T server up:
```bash
git clone git@github.com:thiagopari/learners-permit.git && cd learners-permit
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
export ROBOLAB_DIR=~/RoboLab   # plus the keys from step 1
.venv/bin/python -m permit.server --runner robolab --port 8099
```
From the laptop, open a tunnel (`ssh -L 8099:localhost:8099 $USER@$VM_IP`), open http://localhost:8099, then:
```bash
curl -X POST localhost:8099/commission -H 'Authorization: Bearer demo-sue' -d '{"skill":"bananas_in_bin"}'
curl -X POST localhost:8099/commission -H 'Authorization: Bearer demo-sue' -d '{"skill":"red_dishes_in_bin","arms":["n17_droid"]}'
curl -X POST localhost:8099/orders -H 'Authorization: Bearer demo-olga' -d '{"text":"Put the red dishes in the bin"}'
```
- **Batches:** commissioning runs 20 episodes per RoboLab launch. Each launch boots Isaac Sim, roughly 10–20 min per
  launch (RUNBOOK §2.3), and a decision takes 1–5 launches.
- **Live runs:** use `"repeat": n` on `/run` or `/agent/run` to run n episodes under one decision.
- **The first real run is the moment of truth for `runners.robolab`.** If it raises "expected N episodes, got M",
  read the RoboLab output it prints. The parser follows RUNBOOK §2.4: `success` per row, de-duplicated by
  `(env_name, episode)`.
- **Before anything leaves localhost,** set `PERMIT_SESSIONS` to real tokens; the demo tokens are printed in the public README.
  The server binds 127.0.0.1 only.

## Step 6: fine-tune (stretch; cut lines Oct 14 data replay, Oct 20 beats baseline)
1. **Scripted expert demos** in the RedDishesInBin scene, written in DROID's 17-D LeRobot v2 layout. Copy
   `modality.json` verbatim from RUNBOOK §3.2.
   - **Risk:** RoboLab's exporter writes LeRobot v3 with joint-position state, so expect a conversion step
     (`convert_v3_to_v2` plus `compute_eef_9d`).
2. **Validate 5 episodes before generating 1,000** (RUNBOOK §3.3): `repair_lerobot_metadata.py --dry-run`,
   `verify_droid_rotation_correction.py`, then `standalone_inference_script.py`.
3. **Train on the VM** (RUNBOOK §3.1, `USE_WANDB=0`). Start from `nvidia/GR00T-N1.7-DROID`, or the 3B base as in the
   recipe. Run 5–10K steps; checkpoint every 1,000 if you use spot instances.
4. **Serve the fine-tuned checkpoint on port 5556** (arm `n17_droid_ft` in `permit/skills.json`) and commission it.
   If it never beats the baseline, the video shows the gate refusing it. That's still a valid result.

## Step 7: video and submission (Oct 26–29)
- **Video:** the 4 beats from the console, plus RoboLab clips (`--video-mode all`). **Label sim footage as simulation.**
  No third-party trademarks (no "Gemini"). Under 3 min, on YouTube.
- **Go public:**
  ```bash
  gitleaks git .
  gh repo edit thiagopari/learners-permit --visibility public --accept-visibility-change-consequences
  ```
- **Turn on CI:** the Mac's gh login lacked the `workflow` scope.
  ```bash
  gh auth refresh -h github.com -s workflow
  mkdir -p .github/workflows && git mv docs/ci/tests.yml .github/workflows/tests.yml
  git commit -m "Enable CI" && git push
  ```
- **Devpost:** Physical AI track, city **Boston**. Paste the prior-work note from the README. Add tool feedback.

## Gotchas collected so far
- **torch:** `uv run` silently re-syncs torch. After any cu129 override, use `uv run --no-sync`.
- **Drivers:** Isaac Sim 5.0 with an early 580 driver gives a Warp `cuDeviceGetUuid` error, so update the driver.
- **Server errors:** if the GR00T server says `SVD did not converge`, save the task name and the server log.
- **VRAM:** always run RoboLab `--headless`; it leaks VRAM otherwise.
- **Never parse RoboLab's exit code;** count the JSONL rows. The runner already does this.
