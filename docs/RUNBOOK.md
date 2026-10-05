# Learner's Permit - Linux runbook

GR00T N1.7 (DROID) policy server + RoboLab eval + fine-tuning + Isaac Sim on Blackwell + Nebius RTX PRO 6000.
Written 2026-10-04. Targets: (a) Ubuntu laptop, NVIDIA Blackwell sm_120, driver 580.173.02; (b) Nebius VM with RTX PRO 6000.

---

## 0. Read this first

**How this was sourced.** WebSearch was unavailable. Every fact comes from WebFetch of the URLs listed under each section (raw GitHub files, GitHub API listings, vendor docs). WebFetch summarizes pages with a small model, so code blocks below are "as returned by the tool" and can differ in whitespace/ordering from upstream. Anything inferred, taken from your memory notes, or not fetchable is marked **UNVERIFIED**. One cautionary tale: an early fetch of the nebius-physical-ai README claimed it names `uk-south2, eu-south1`; a neutral re-check showed it does not (section 5.1). Diff anything critical against upstream before you rely on it.

### 0.1 Blockers and traps (read before running anything)

1. **Laptop VRAM.** Your memory note (env_blackwell_torch.md) says the laptop GPU is an RTX PRO 2000 Blackwell, 8 GB. GR00T N1.7 inference needs "1 GPU with 16 GB+ VRAM" (Isaac-GR00T README); Isaac Sim 5.1 lists 16 GB as the minimum (RTX 4080 class); RoboLab recommends 48 GB+. Run the policy server AND RoboLab on the Nebius RTX PRO 6000 (96 GB). Use the laptop for the Python wrapper, result parsing, and CPU-only tests.
2. **RoboLab uses Isaac Lab `TiledCameraCfg`** (both cameras, 720x1280). Isaac Lab issues #4951 and #5001 report `TiledCamera` hanging forever on RTX 5090 *Laptop* (GB203) with Isaac Sim 5.1.0, while the desktop GB202 works; no fix, workaround is swapping to `Camera` (a code change in RoboLab). Your laptop is a different laptop Blackwell chip: expect risk. Nebius RTX PRO 6000 is GB202, the chip that worked in that report (with driver 570.211.01, not 580.x, so not proven for the 580 images, **UNVERIFIED**).
3. **Task name.** There is no `BananasInBinTask`. The 38/40 task in the GR00T README is `BananasInBinThreeTotalTask`; the other registered banana-bin tasks are `BananasInBinOneMoreTask` and `BananasOutOfBinTask`. `RedDishesInBinTask` is exact (README: 15/40). Task names carry the `Task` suffix.
4. **RoboLab install flag.** RoboLab's own README says `uv sync --extra isaac50` (Isaac Sim 5.0 / Isaac Lab 2.2.0) or `--extra isaac51`. The Isaac-GR00T RoboLab example README says plain `uv sync`; RoboLab's pyproject `[project].dependencies` contains neither `isaacsim` nor `isaaclab` and there is no `default-extras`; they exist only under the `isaac50`/`isaac51` extras (added in RoboLab v0.2.0 per CHANGELOG, 2026-07-07). So plain `uv sync` installs no simulator; the Isaac-GR00T example README is stale on this point. Use the extra.
5. **Git LFS.** RoboLab `.gitattributes` puts `*.usd *.obj *.glb *.stl *.hdf5 *.npz *.png *.jpg *.exr` in LFS (about 7 GB of assets). Install git-lfs BEFORE cloning or you get pointer files. The Isaac-GR00T `demo_data/droid_sample` parquet files are listed at 131 bytes each (looks like LFS pointers, **UNVERIFIED**); use `scripts/download_droid_sample.py` instead.
6. **`uv run` silently re-syncs.** Both repos pin torch to the cu128 index. If you override torch to cu129 (section 1.4) you must call `uv run --no-sync ...` or the venv's `python` directly, otherwise `uv run` reverts the wheels.
7. **nebius-physical-ai has no RoboLab/DROID-eval workflow.** Its Isaac Lab workbench is Isaac Lab 3.0.0b2.post1 + Isaac Sim 6.0.1 + Python 3.12 (container). RoboLab needs Isaac Sim 5.0/5.1 + Python 3.11. So for RoboLab use a plain VM (section 5.3), not the npa Isaac Lab container.
8. **`isaac-sim` needs RT cores.** H100/H200/B200/A100 cannot render (Isaac Sim docs: "GPUs without RT Cores (A100, H100) are not supported"). RTX PRO 6000 and L40S are fine.

### 0.2 Result format in one paragraph (details in section 2.4)

RoboLab appends one JSON object per finished episode to `<RoboLab>/output/<folder>/episode_results.jsonl`; the boolean is `"success"`. Unique key is `(env_name, episode)`. Lines are written per *run* (all `--num-envs` episodes of a run at once), not mid-episode. Videos are NOT referenced from the JSONL.

---

## 1. GR00T N1.7: install and DROID policy server

Sources:
- https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/README.md
- https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/examples/DROID/README.md
- https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/examples/RoboLab/README.md
- https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/pyproject.toml
- https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/gr00t/eval/run_gr00t_server.py
- https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/gr00t/policy/server_client.py
- https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/getting_started/policy.md
- https://huggingface.co/api/models/nvidia/GR00T-N1.7-DROID , .../GR00T-N1.7-3B , .../Cosmos-Reason2-2B
- https://huggingface.co/docs/hub/models-gated , https://huggingface.co/docs/huggingface_hub/guides/cli
- https://api.github.com/repos/NVIDIA/Isaac-GR00T/releases (tag `n1.7-release`, 2026-04-18, "Early Access"); latest main commit seen: 51d4c89 (2026-08-20)

Facts: Python `>=3.12,<3.13`; `torch==2.9.0`, `torchvision==0.24.0`, `transformers==4.57.3`, `flash-attn==2.8.3` (prebuilt wheel `+cu12torch2.9cxx11abiTRUE-cp312`), `torchcodec==0.8.0`, `numpy==1.26.4`; torch/torchvision/triton routed to `https://download.pytorch.org/whl/cu128` in `[tool.uv.sources]`. README: dGPU = CUDA 12.8 + Python 3.12; inference 16 GB+ VRAM; fine-tuning 40 GB+ VRAM. Releases: `n1.7-release` tag; use `main` for the DROID/RoboLab examples (the example READMEs live on main). To pin for reproducibility record `git rev-parse HEAD`.

### 1.1 Prerequisites (Ubuntu 22.04/24.04, x86_64)

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg git git-lfs tmux jq
git lfs install
ffmpeg -version | head -1      # must be FFmpeg 4-7; torchcodec 0.8.0 cannot load FFmpeg 8 (Ubuntu 25.10+/26.04 ship 8)
curl -LsSf https://astral.sh/uv/install.sh | sh
# open a new shell so ~/.local/bin is on PATH
nvidia-smi                      # expect driver 580.x
```

### 1.2 Install (verbatim from the README)

```bash
git clone --recurse-submodules https://github.com/NVIDIA/Isaac-GR00T
cd Isaac-GR00T
uv sync --python 3.12
uv run python -c "import gr00t; print('GR00T installed successfully')"
```

(README also lists `git submodule update --init --recursive` if you cloned without submodules.) uv will print repeated `Installing flash-attn...`; the README says that is a cached wheel check, not a rebuild.

### 1.3 Gated backbone: nvidia/Cosmos-Reason2-2B

README: "GR00T's VLM backbone is `nvidia/Cosmos-Reason2-2B`, a gated model that every GR00T checkpoint (including the base `nvidia/GR00T-N1.7-3B`) loads on first use." Without access, loading fails with `GatedRepoError` / `401 Client Error`.

HF API (fetched 2026-10-04): `Cosmos-Reason2-2B` has `gated: "auto"` (automatic approval), license "NVIDIA Open Model License", Qwen3-VL architecture, 2.44B params, BF16. `nvidia/GR00T-N1.7-DROID` and `nvidia/GR00T-N1.7-3B` both report `gated: false`.

Steps:
1. Log in to huggingface.co (or create an account).
2. Open https://huggingface.co/nvidia/Cosmos-Reason2-2B and accept the gate (the page says "You need to agree to share your contact information to access this model"; you accept the NVIDIA Open Model License and share username/email). Access requests can only be made from a browser (HF docs). With `auto` approval you should get access immediately.
3. Create a token at https://huggingface.co/settings/tokens (a classic **Read** token is simplest; if you use a fine-grained token it must be allowed to read public gated repos, **UNVERIFIED** exact permission wording).
4. Log in on the machine (the `hf` CLI is what RoboLab's README uses; the Isaac-GR00T README says `huggingface-cli login`, same thing, older name):

```bash
cd Isaac-GR00T
uv run hf auth login                  # or: export HF_TOKEN=hf_xxxxxxxx   (README also allows this)
uv run hf auth whoami
# prove gated access works without downloading the 5 GB weights:
uv run python -c "from huggingface_hub import hf_hub_download as d; print(d('nvidia/Cosmos-Reason2-2B','config.json'))"
```

Offline/no-HF-egress note (from YOUR memory note project_gb10_hackathon, not from upstream docs): transformers 4.57.3 still calls the HF API for repo-id tokenizers even offline; you fixed it by pointing `model_name` in the checkpoint configs to a local dir whose path contains `nvidia/Cosmos-Reason2`. Only needed if the VM cannot reach HF.

### 1.4 Blackwell torch (laptop; on the VM only if the check fails)

Your memory note says cu126/cu128 wheels lacked sm_120 kernels on this laptop (`no kernel image is available`) and cu129 works. PyTorch's own 2.7 blog (https://pytorch.org/blog/pytorch-2-7/) says cu128 builds support Blackwell, and GR00T issues #733/#734 measure `torch 2.9.0+cu128` on an RTX 5090 (sm 12.0). These conflict; do not argue, test:

```bash
cd Isaac-GR00T
.venv/bin/python -c "import torch; print(torch.__version__, torch.cuda.get_arch_list())"   # want sm_120 in the list
```

If `sm_120` is missing or a kernel launch fails, swap in cu129 builds. Verified to exist on the index: `torch-2.9.0+cu129-cp312-cp312-manylinux_2_28_x86_64.whl` and `torchvision-0.24.0+cu129-cp312-cp312-manylinux_2_28_x86_64.whl` (https://download.pytorch.org/whl/cu129/torch/ , .../torchvision/). The prebuilt flash-attn wheel is `cu12torch2.9`, ABI-compatible with 2.9.0+cu129 (**UNVERIFIED** that it loads cleanly on sm_120; flash-attn >= 2.8.2 added sm_120 per GR00T PR #560).

```bash
uv sync --python 3.12
uv pip install --python .venv/bin/python \
  --reinstall-package torch --reinstall-package torchvision \
  "torch==2.9.0" "torchvision==0.24.0" --torch-backend=cu129
.venv/bin/python - <<'EOF'
import torch
print(torch.__version__, torch.cuda.get_device_name(0), torch.cuda.get_device_capability(0))
print(torch.cuda.get_arch_list())                      # must include sm_120
x = torch.randn(256, 256, device="cuda"); print((x @ x).sum().item())   # real kernel launch
EOF
# from now on NEVER plain `uv run` in this repo; use:
#   uv run --no-sync python ...      or      source .venv/bin/activate && python ...
```

`--torch-backend` is only available in the `uv pip` interface (uv docs: https://docs.astral.sh/uv/guides/integration/pytorch/); `uv sync` ignores it. Fallback spelling: `--index-url https://download.pytorch.org/whl/cu129`. **UNVERIFIED** on this exact stack. Also note the laptop is 8 GB: a successful torch check does not mean the 3B model will fit (section 0.1 item 1).

### 1.5 Launch the policy server for the DROID embodiment (Franka)

Checkpoint: **`nvidia/GR00T-N1.7-DROID`** (finetuned on DROID). Embodiment tag: **`OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT`** (a pretrain tag, also used by the base `nvidia/GR00T-N1.7-3B`). Default port **5555** (ZeroMQ REP socket).

For RoboLab (simulation), exactly as in both RoboLab READMEs:

```bash
cd Isaac-GR00T
CUDA_VISIBLE_DEVICES=0 uv run python gr00t/eval/run_gr00t_server.py \
    --model-path nvidia/GR00T-N1.7-DROID \
    --embodiment-tag OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT \
    --device cuda \
    --host 127.0.0.1 \
    --port 5555 \
    --use-sim-policy-wrapper
```

(Laptop with the cu129 override: replace `uv run python` with `uv run --no-sync python`.)

Ready line (README and server_client.py): `Server is ready and listening on tcp://127.0.0.1:5555`. First launch downloads the checkpoint (2 safetensors shards, roughly 6 GB, my estimate from 3B params in BF16) plus the Cosmos-Reason2-2B backbone files (roughly 5 GB, estimate).

Variants:

```bash
# real-robot DROID (no sim wrapper) -- from examples/DROID/README.md
uv run python gr00t/eval/run_gr00t_server.py \
    --model-path nvidia/GR00T-N1.7-DROID \
    --embodiment-tag OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT

# zero-shot base model
uv run python gr00t/eval/run_gr00t_server.py \
    --model-path nvidia/GR00T-N1.7-3B \
    --embodiment-tag OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT --device cuda:0

# no weights, no HF gate: replay a dataset's actions (pipeline plumbing test only; getting_started/policy.md)
uv run python gr00t/eval/run_gr00t_server.py \
    --dataset-path demo_data/droid_sample \
    --embodiment-tag OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT --execution-horizon 8
```

`ServerConfig` defaults (run_gr00t_server.py): `embodiment_tag="new_embodiment"`, `device="cuda"`, `host="0.0.0.0"` (careful: world-listening if you omit `--host`), `port=5555`, `strict=True`, `use_sim_policy_wrapper=False`. Port busy: `ZMQError: Address already in use` -> pass `--port <other>`. The server has no TLS; optional `api_token` exists on PolicyClient/Server. Bind to 127.0.0.1 and keep RoboLab on the same host.

Health check from any Python with the GR00T env (README: `policy.ping()`):

```bash
uv run python - <<'EOF'
from gr00t.policy.server_client import PolicyClient
print("ping ok:", PolicyClient(host="127.0.0.1", port=5555, timeout_ms=15000).ping())
EOF
```

### 1.6 Offline smoke test (no server, no RoboLab)

```bash
uv pip install jsonlines
uv run python scripts/download_droid_sample.py          # 3 episodes (~170 MB) -> demo_data/droid_sample (GR00T LeRobot v2)
uv run python scripts/deployment/standalone_inference_script.py \
    --model-path nvidia/GR00T-N1.7-DROID \
    --dataset-path demo_data/droid_sample \
    --embodiment-tag OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT \
    --traj-ids 1 2 \
    --inference-mode pytorch \
    --execution-horizon 8
```

DROID README: episode 0 may have an empty language instruction, use `--traj-ids 1 2`. Base-model reference: average MSE about 0.0149 on the sample.

---

## 2. RoboLab: setup and evaluating the GR00T N1.7-DROID server

Sources:
- https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/examples/RoboLab/README.md
- https://raw.githubusercontent.com/NVlabs/RoboLab/main/README.md , pyproject.toml , CHANGELOG.md , .gitattributes
- https://raw.githubusercontent.com/NVlabs/RoboLab/main/policies/gr00t/README.md , run.py , client.py
- https://raw.githubusercontent.com/NVlabs/RoboLab/main/docs/environment_run.md , data.md , dashboard.md , analysis.md , env_vram_size_guide.md , known_issues.md , camera.md
- https://raw.githubusercontent.com/NVlabs/RoboLab/main/robolab/eval/runner.py , summarize.py , robolab/core/logging/results.py , robolab/core/environments/env.py , robolab/constants.py
- https://raw.githubusercontent.com/NVlabs/RoboLab/main/robolab/tasks/_metadata/task_table.csv , robolab/tasks/benchmark/*.py
- https://api.github.com/repos/NVlabs/RoboLab/releases (latest v0.3.1, 2026-08-12)

Versions (RoboLab README): Ubuntu 22.04+, **Python 3.11**, **Isaac Sim 5.0.0 + Isaac Lab 2.2.0** (extra `isaac50`, "default") or **Isaac Sim 5.1.0 + Isaac Lab 2.3.2.post1** (extra `isaac51`); the extras are mutually exclusive and "Contact-rich dynamics (grasping, object settling) are not invariant across the two stacks". NVIDIA RTX GPU, 48 GB+ VRAM recommended, ~8 GB disk (assets ~7 GB), "30 GPU hours / 100 tasks at 1.4 it/s". Torch comes from the cu128 index (`torch = { index = "pytorch-cu128" }`).

### 2.1 Setup (Python 3.11 venv)

```bash
sudo apt install -y ffmpeg git-lfs && git lfs install          # LFS BEFORE clone (see 0.1 item 5)
git clone https://github.com/NVlabs/RoboLab.git
cd RoboLab
git lfs pull                                                   # harmless if already fetched
uv venv --python 3.11
source .venv/bin/activate
uv sync --extra isaac50                                        # Isaac Sim 5.0.0 / Isaac Lab 2.2.0 (README default)
# alternative, mutually exclusive:  uv sync --extra isaac51    # Isaac Sim 5.1.0 / Isaac Lab 2.3.2.post1
export OMNI_KIT_ACCEPT_EULA=Y                                  # required once (Isaac Sim docs and Dockerfile use YES; Y is what the RoboLab README uses)
uv run python policies/gr00t/run.py --help                     # sanity: imports Isaac, prints flags
uv run pytest tests/                                           # optional: "isaaclab importable, all task definitions valid, env factory populated, one full episode runs"
```

Dual-stack option from the README: `UV_PROJECT_ENVIRONMENT=.venv uv sync --extra isaac50` and `UV_PROJECT_ENVIRONMENT=.venv-51 uv sync --extra isaac51`.

First run compiles shaders and may take several minutes (general Isaac Sim behavior, **UNVERIFIED** in these docs). Always use `--headless` for multi-task runs: RoboLab known issue "GPU VRAM usage grows each time an environment is created and destroyed" without it.

### 2.2 Start the server first (section 1.5), then smoke-test with a task that works

README smoke test (expected near 40/40 per the GR00T README):

```bash
cd RoboLab
OMNI_KIT_ACCEPT_EULA=Y CUDA_VISIBLE_DEVICES=0 uv run python policies/gr00t/run.py \
    --headless \
    --remote-host 127.0.0.1 \
    --remote-port 5555 \
    --task BananaOnPlateTask \
    --num-envs 10 \
    --num-runs 1 \
    --open-loop-horizon 8 \
    --instruction-type default \
    --video-mode none
```

### 2.3 Evaluate the target tasks for N episodes

Task names (from `robolab/tasks/_metadata/task_table.csv` and the task files): `BananasInBinThreeTotalTask` ("Make sure there are 3 (three) bananas in the grey bin.", 60 s episodes), `BananasInBinOneMoreTask` ("Put one (1) more bananas in the grey bin.", 60 s), `RedDishesInBinTask` ("Put the red dishware in the grey bin", 60 s; success = both `mug` and `bowl` in `grey_bin` with gripper detached). Verify the class names exist in your checkout:

```bash
grep -rn "class BananasInBinThreeTotalTask\|class RedDishesInBinTask" robolab/tasks/benchmark/
```

**Episodes per task = `--num-envs` x `--num-runs`** (runner.py: `total_episodes = ... num_runs * num_envs`). `--num-envs` runs in parallel in one sim; use `--num-runs` to split when VRAM is short (RoboLab docs example: 20 episodes = 10 envs x 2 runs). RoboLab README validation used 40 episodes per task. RoboLab's per-task `num_envs` ceilings on a 48 GB L40 (headless): BananasInBinThreeTotalTask 80, BananasInBinOneMoreTask 80, RedDishesInBinTask 100 (policy server not mentioned in the measurement, so leave headroom on a shared GPU).

```bash
cd RoboLab
OMNI_KIT_ACCEPT_EULA=Y CUDA_VISIBLE_DEVICES=0 uv run python policies/gr00t/run.py \
    --headless \
    --remote-host 127.0.0.1 \
    --remote-port 5555 \
    --task BananasInBinThreeTotalTask RedDishesInBinTask \
    --num-envs 40 \
    --num-runs 1 \
    --open-loop-horizon 8 \
    --instruction-type default \
    --video-mode none \
    --output-folder-name lp_eval_001
```

Variants:
- N=100 episodes/task: `--num-envs 50 --num-runs 2` (or `--num-envs 100` if VRAM allows).
- Keep videos + score/failure reasons (GR00T README "inspectable diagnostic runs"): replace `--video-mode none` with `--video-mode all --enable-subtask` (`--enable-subtask` is already default True in argparse; `--video-mode` choices: `all|viewport|sensor|none`, default `all`).
- Resume a crashed/interrupted run: re-issue the same command with the same `--output-folder-name`; completed tasks/runs are skipped (`Task ... already done. Skipping.`).
- Adaptive sampling instead of fixed N: `--num-episodes-adaptive MAX_N --ci-pp-width 0.14` (stops per task when the 95% Beta CI is narrow enough; N then varies).
- `--open-loop-horizon 8` is what the GR00T README validated (client default is 10). `--instruction-type` = `default|vague|specific`.

Default output folder if you omit `--output-folder-name`: `<timestamp>_gr00t` (`get_timestamp()` = `%Y-%m-%d_%H-%M-%S`, `POLICY = "gr00t"`), with `_<instruction_type>` appended when not `default`. Folder lives at `<RoboLab repo>/output/<folder>/` (`PACKAGE_DIR` = repo root; `DEFAULT_OUTPUT_DIR = os.path.join(PACKAGE_DIR, "output")`).

Runtime ballpark (RoboLab docs): about 15 min per task per run at 1-2 it/s; one task with 40 envs is on the order of 10-20 min on one GPU. The server is shared by all envs.

### 2.4 What the eval prints and saves per episode

Quoted README lines (Isaac-GR00T examples/RoboLab/README.md, "Outputs And Dashboard"):

> "For throughput sweeps, use `--video-mode none`. RoboLab still writes run summaries, task logs, HDF5 trajectories, timing, and per-task result rows."
> "`--video-mode all` writes both policy/sensor and viewport mp4s beside the task outputs."
> "`--enable-subtask` populates score and failure-reason fields when task subtask tracking is available."
> "The dashboard uses `episode_results.jsonl` as the canonical per-episode summary and discovers mp4s, per-env logs, and HDF5 files from each task directory."

**(a) Console, one line per finished episode** (robolab/core/logging/results.py `update_experiment_results`; green for success, red for failure):

```python
run_name = f"{env_name}_{episode}"
if succ:
    print(f"{GREEN}{run_name} complete:{RESET}",
          ", ".join([f"{k}: {v}" for k, v in run_summary.items() if k not in ("env_name", "episode")]))
else:
    print(f"{RED}{run_name} complete:{RESET}", ", ".join(...same...))
episode_results.append(run_summary)
append_episode_to_jsonl(episode_results_file, run_summary)
```

with `GREEN = '\033[92m'`, `RED = '\033[91m'`, `RESET = '\033[0m'`. Constructed from the code, NOT captured from a live run:

```
<ESC>[92mRedDishesInBinTask_3 complete:<ESC>[0m task_name: RedDishesInBinTask, run_name: ..., run: 0, env_id: 3, policy: gr00t, instruction: Put the red dishware in the grey bin, instruction_type: default, attributes: [...], success: True, score: 1.0, reason: ..., episode_step: 412, duration: 27.5, dt: 0.0667, metrics: {...}, events: {...}, timing: {...}
```

Other console lines (runner.py): `[RoboLab] Running {run_name}: '{env_cfg.instruction}' (run {run_idx}, {num_envs} envs)` (cyan), `[RoboLab] Task `{task_env}` already done. Skipping.`, `Loaded N existing results from <dir>.` on resume, and a final summary table (`summarize_experiment_results(episode_results, show_timing=True)`; format not captured, do not parse it). On a crash policies/gr00t/run.py prints `[RoboLab] Terminated with error: {e}` (cyan); whether the process exit code is non-zero is **UNVERIFIED** (the docs' sample `run_eval.py` does `sys.exit(1)`), so do not rely on the exit code: count JSONL rows instead.

**(b) File `output/<folder>/episode_results.jsonl`** (append-only, one JSON object per line; `append_episode_to_jsonl`: `f.write(json.dumps(episode) + "\n")`). Built by `build_run_summary` (robolab/eval/summarize.py):

```python
episode_id = run_idx * num_envs + env_id
summary = {
    "env_name": task_env,
    "task_name": task_name if task_name is not None else env_cfg._task_name,
    "run_name": run_name,
    "run": run_idx,
    "episode": episode_id,
    "env_id": env_id,
    "policy": policy,                      # "gr00t"
    "instruction": env_cfg.instruction,
    "attributes": env_cfg._task_attributes,
    "success": env_result["success"],      # bool, or None if the env never terminated
    "episode_step": env_result["step"],
    "duration": env_result["step"] * dt if env_result["step"] else 0,
    "dt": dt,
    "metrics": traj_metrics or {},
    "events": events or {},
}
# conditionally: instruction_type, timing; with subtask tracking: score, reason
```

Success semantics (robolab/core/environments/env.py): `get_env_results()` returns `{'env_id', 'success', 'step'}` per env and `self._env_results[eid] = bool(self.termination_manager.terminated[eid])`, i.e. success = the task's success termination fired; False = time-out/truncation. One sample row from docs/data.md (pi05 run; gr00t rows have the same keys, plus `run`, `env_id`, `timing`):

```json
{"env_name": "RubiksCubeAndBananaTask", "task_name": "RubiksCubeAndBananaTask", "run_name": "RubiksCubeAndBananaTask_1", "episode": 1, "policy": "pi05", "instruction": "Put the cube and the banana in the bowl", "instruction_type": "default", "attributes": ["conjunction", "simple"], "success": true, "score": 1.0, "reason": "Completed subtask 'pick_and_place' 1/1", "episode_step": 232, "duration": 15.467, "dt": 0.06666666666666667, "metrics": {"ee_sparc": -3.971, "ee_path_length": 1.126}, "events": {"TARGET_OBJECT_DROPPED": 4}}
```

Field list per docs/data.md: identification `env_name, task_name, run_name, episode, run, env_id, policy`; `instruction, instruction_type, attributes`; `success, score, reason`; `episode_step, duration, dt`; trajectory `metrics` (ee_sparc, joint_sparc_mean, ee_isj, joint_isj, ee_path_length, joint_rmse_mean, ee_speed_max, ee_speed_mean); timing (`policy_inference_s`, `env_step_s`, `video_write_s`, `wall_total_s`, `it_per_sec`, ...); `events` (`WRONG_OBJECT_GRABBED, GRIPPER_HIT_TABLE, GRIPPER_HIT_OBJECT, GRIPPER_FULLY_CLOSED, TARGET_OBJECT_DROPPED, MULTIPLE_OBJECTS_GRABBED, OBJECT_BUMPED, OBJECT_MOVED, OBJECT_OUT_OF_SCENE`).

**(c) Directory layout** (docs/data.md):

```
output/
└── <output_folder>/
    ├── episode_results.jsonl
    ├── <ENV_NAME>/
        ├── run_0.hdf5                       # Run 0 data (demo_0..demo_{N-1} for N envs)
        ├── run_1.hdf5                       # Run 1 data (if num_runs > 1)
        ├── log_0_env0.json                  # Run 0, env 0 subtask log
        ├── {instruction}_0_env0.mp4         # Run 0, env 0 observation video
        ├── {instruction}_0_env0_viewport.mp4
        └── env_cfg.json
```

Video path is not stored in the JSONL row (the sample has no video field; **UNVERIFIED** for gr00t). Build it from the row: `output/<folder>/<env_name>/` + glob `*_{run}_env{env_id}.mp4` (and `*_viewport.mp4`). Videos exist only with `--video-mode all|sensor|viewport`.

**(d) Parse it from a Python wrapper.** Treat `success` None as failure (the code does `if succ:`), de-duplicate on `(env_name, episode)` (resume can re-append), and check completeness yourself:

```python
import json, pathlib, collections

def read_episodes(folder: str):
    p = pathlib.Path(folder) / "episode_results.jsonl"
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []
    uniq = {(r["env_name"], r["episode"]): r for r in rows}          # last write wins
    return list(uniq.values())

def per_task(folder: str, expect_per_task: int, tasks):
    eps = read_episodes(folder); out = {}
    for t in tasks:
        s = [bool(r.get("success")) for r in eps if r["env_name"] == t]
        out[t] = {"k": sum(s), "n": len(s), "complete": len(s) == expect_per_task}
    return out

# per_task("RoboLab/output/lp_eval_001", 40, ["BananasInBinThreeTotalTask", "RedDishesInBinTask"])
```

Human-readable summaries from RoboLab itself (docs/analysis.md): `python analysis/read_results.py lp_eval_001 --task BananasInBinThreeTotalTask RedDishesInBinTask`, `python analysis/check_results.py lp_eval_001 --verbose --diagnose`, `python analysis/compile_results.py "lp_eval_*" -o results.jsonl`. Dashboard: `uv run robolab-dashboard --output-dir output --port 8080` (binds 0.0.0.0:8080 per docs; on the VM reach it via SSH tunnel, do not open the port).

Known failure to log: GR00T README troubleshooting: "If the server returns `SVD did not converge`, save the task name and server log" (numerical issue in the action decode path, not an install problem). "If RoboLab crashes before launching IsaacSim, check for duplicate argparse flags between RoboLab and IsaacLab's `AppLauncher`."

Reference results to compare against (GR00T README, 40 episodes/task, `nvidia/GR00T-N1.7-DROID`, 8-step horizon, 4 denoising steps): BananaOnPlateTask 40/40, BananasInBinThreeTotalTask 38/40, UnstackRubiksCubeTask 38/40, SauceBottlesCrateTask 33/40, RedDishesInBinTask 15/40; overall 8.58% over 4,800 episodes / 120 tasks (N1.6 baseline 7.25% over 1,200).

---

## 3. Fine-tuning N1.7 for DROID

Sources:
- https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/examples/DROID/README.md
- https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/getting_started/finetune_new_embodiment.md , data_preparation.md , hardware_recommendation.md
- https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/examples/finetune.sh
- https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/gr00t/configs/finetune_config.py , gr00t/configs/data/embodiment_configs.py , gr00t/data/embodiment_tags.py , gr00t/configs/model/gr00t_n1d7.py
- https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/demo_data/droid_sample/meta/modality.json , info.json
- https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/scripts/download_droid_sample.py , scripts/repair_lerobot_metadata.py , scripts/verify_droid_rotation_correction.py , scripts/lerobot_conversion/README.md
- https://github.com/Rao-Sanaullah/GR00TN1.7 (community RTX 5090 guide, third party)

### 3.1 The command

`launch_finetune.py` for the DROID embodiment (built-in tag, so no `--modality-config-path`; the DROID README's `finetune.sh` run omits it, the script adds it only conditionally):

```bash
cd Isaac-GR00T
CUDA_VISIBLE_DEVICES=0 uv run python gr00t/experiment/launch_finetune.py \
    --base-model-path nvidia/GR00T-N1.7-3B \
    --dataset-path /data/droid_style_ds \
    --embodiment-tag OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT \
    --num-gpus 1 \
    --output-dir /data/ckpt/droid_ft \
    --max-steps 20000 \
    --save-steps 1000 \
    --save-total-limit 5 \
    --global-batch-size 32 \
    --dataloader-num-workers 4 \
    --color-jitter-params brightness 0.3 contrast 0.4 saturation 0.5 hue 0.08
```

Official 8-GPU DROID recipe (examples/DROID/README.md; "uses the small `demo_data/droid_sample` (3 episodes) for quick validation. For production training, replace `--dataset-path` with the full DROID dataset", full set `lerobot/droid_1.0.1`, about 358 GB, 95k+ episodes):

```bash
NUM_GPUS=8 MAX_STEPS=20000 GLOBAL_BATCH_SIZE=640 SAVE_STEPS=1000 uv run bash examples/finetune.sh \
    --base-model-path nvidia/GR00T-N1.7-3B \
    --dataset-path demo_data/droid_sample \
    --embodiment-tag OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT \
    --output-dir /tmp/droid_finetune
```

`finetune.sh` defaults: `NUM_GPUS=1 MASTER_PORT=29500 SAVE_STEPS=1000 MAX_STEPS=10000 GLOBAL_BATCH_SIZE=32 SHARD_SIZE=1024 NUM_SHARDS_PER_EPOCH=100000 EPISODE_SAMPLING_RATE=0.1 DATALOADER_NUM_WORKERS=4 USE_WANDB=1`, fixed `--learning_rate 1e-4 --weight_decay 1e-5 --warmup_ratio 0.05 --save_total_limit 5`; single GPU uses `python` with `CUDA_VISIBLE_DEVICES`, multi GPU uses `torchrun --nproc_per_node=$NUM_GPUS`. (Heads-up: `USE_WANDB=1` by default; set `USE_WANDB=0` or log in to W&B.) Direct multi-GPU form from the README: `uv run torchrun --nproc_per_node=8 --master_port=29500 gr00t/experiment/launch_finetune.py ... --num-gpus 8`.

Useful `FinetuneConfig` fields (finetune_config.py): `global_batch_size=64` ("Total batch summed across all GPUs in one forward/backward, BEFORE gradient accumulation"), `gradient_accumulation_steps=1`, `learning_rate=1e-4`, `max_steps=10000`, `save_steps=1000`, `save_total_limit=5`, `num_gpus=1`, `dataloader_num_workers=2`, `tune_llm=False`, `tune_visual=False`, `tune_projector=True`, `tune_diffusion_model=True`, `state_dropout_prob=0.2` (model config default 0.8; lower it if tasks depend on proprioception), `use_percentiles=True`, `save_only_model=False`, `resume_from_checkpoint=False`, `dataset_path` accepts an `os.pathsep`-separated list of dataset roots. `--help` lists everything: `uv run python gr00t/experiment/launch_finetune.py --help`.

### 3.2 LeRobot v2 dataset layout (GR00T-flavored v2.1) and DROID `meta/modality.json`

Layout of `demo_data/droid_sample` (directory listings via GitHub API):

```
my_droid_ds/
├── meta/
│   ├── info.json            # codebase_version "v2.1", robot_type "droid", fps 15, features (below)
│   ├── episodes.jsonl       # {"episode_index": 0, "tasks": [...], "length": 416}
│   ├── tasks.jsonl          # {"task_index": 0, "task": "put the cube in the bowl"}
│   ├── modality.json        # GR00T-specific
│   ├── stats.json           # auto-computed by GR00T (or by scripts/repair_lerobot_metadata.py)
│   └── relative_stats.json  # auto-computed
├── data/chunk-000/episode_000000.parquet ...
└── videos/chunk-000/
    ├── observation.images.exterior_1_left/episode_000000.mp4
    └── observation.images.wrist_left/episode_000000.mp4
```

`info.json` from the sample: `"codebase_version": "v2.1"`, `"robot_type": "droid"`, `"fps": 15`, `"data_path": "data/chunk-{episode_chunk:03d}/episode_{episode_index:06d}.parquet"`, `"video_path": "videos/chunk-{episode_chunk:03d}/{video_key}/episode_{episode_index:06d}.mp4"`, `"chunks_size": 1000`, features `observation.images.exterior_1_left` and `observation.images.wrist_left` (dtype video, shape [180, 320, 3]), `observation.state` (float32 [17]), `action` (float32 [17]), `task_index` (int64 [1]). Videos: MP4, named `observation.images.<name>`; the sample script stream-copies when possible, else re-encodes with `libx264 -crf 23`.

Parquet columns (data_preparation.md): `observation.state` (concatenated 1D float32), `action` (concatenated 1D float32), `timestamp`, `task_index`, `episode_index`, `index`, `next.reward`, `next.done`; language for DROID is read through `task_index` -> `tasks.jsonl`.

`meta/modality.json` for the DROID embodiment (copied from the sample; copy this file verbatim):

```json
{
  "state": {
    "eef_9d":           {"start": 0,  "end": 9},
    "gripper_position": {"start": 9,  "end": 10},
    "joint_position":   {"start": 10, "end": 17}
  },
  "action": {
    "eef_9d":           {"start": 0,  "end": 9},
    "gripper_position": {"start": 9,  "end": 10},
    "joint_position":   {"start": 10, "end": 17}
  },
  "video": {
    "exterior_1_left": {"original_key": "observation.images.exterior_1_left"},
    "wrist_left":      {"original_key": "observation.images.wrist_left"}
  },
  "annotation": {
    "language.language_instruction": {"original_key": "task_index"}
  }
}
```

The embodiment's modality config (gr00t/configs/data/embodiment_configs.py, key `oxe_droid_relative_eef_relative_joint`) uses these names:

```python
"video":    ModalityConfig(delta_indices=[-15, 0], modality_keys=["exterior_image_1_left", "wrist_image_left"]),
"state":    ModalityConfig(delta_indices=[0], modality_keys=["eef_9d", "gripper_position", "joint_position"]),
"action":   ModalityConfig(delta_indices=list(range(40)), modality_keys=["eef_9d", "gripper_position", "joint_position"],
              action_configs=[ActionConfig(rep=RELATIVE, type=EEF, format=XYZ_ROT6D, state_key="eef_9d"),
                              ActionConfig(rep=ABSOLUTE, type=NON_EEF, format=DEFAULT, state_key="gripper_position"),
                              ActionConfig(rep=RELATIVE, type=NON_EEF, format=DEFAULT, state_key="joint_position")]),
"language": ModalityConfig(delta_indices=[0], modality_keys=["annotation.language.language_instruction"]),
```

Reading it: cameras = external left (`exterior_image_1_left`) + wrist left (`wrist_image_left`), two frames each (t-15 and t); state = 17D (9D eef = XYZ + rot6D, 1D gripper, 7D joints); action = 40-step chunk of the same 17D with eef and joints RELATIVE, gripper ABSOLUTE. DROID README: the raw dataset names `exterior_1_left`/`wrist_left` map to `exterior_image_1_left`/`wrist_image_left` ("The data loader auto-maps by position — no manual renaming needed"). RoboLab's client sends `video.exterior_image_1_left`, `video.wrist_image_left`, `state.eef_9d`, `state.joint_position`, `state.gripper_position`, `annotation.language.language_instruction`, images resized to 180x320 HWC uint8 with no letterboxing. The dataset stores absolute values (download_droid_sample.py computes `action.eef_9d` from `action.cartesian_position`); that the loader applies the RELATIVE conversion at train time per `ActionConfig` is inferred from the config (**UNVERIFIED**).

### 3.3 Convert / verify a dataset

- `scripts/download_droid_sample.py` is the reference converter (DROID LeRobot v3.0 -> GR00T v2.1, uses `gr00t.data.state_action.droid_frame.compute_eef_9d` for cartesian XYZ+euler -> 9D XYZ+rot6D). Args: `--output-dir demo_data/droid_sample --num-episodes 3 --cache-dir /tmp/droid_download_cache`.
- LeRobot v3 -> v2 for any HF dataset (separate venv, README says run from `scripts/lerobot_conversion` because it has its own pyproject):

```bash
cd scripts/lerobot_conversion && uv venv && source .venv/bin/activate
uv pip install -e . --verbose
python convert_v3_to_v2.py --repo-id <DATASET_REPO_ID>
```

- RoboLab -> LeRobot exporter exists (`python scripts/convert_to_lerobot.py --input output/<folder> [--robot-type droid --fps 15]`) but emits **LeRobot v3.0**, `observation.state` = joint positions, camera keys `observation.images.<camera>`, i.e. NOT the 17D DROID layout. Its help text says it reads task folders containing `data.hdf5`, while eval runs write `run_N.hdf5` (**UNVERIFIED** that it accepts eval output). You would need convert_v3_to_v2 plus your own remap/`compute_eef_9d` step (**UNVERIFIED** effort).
- Checks (there is no dedicated "validate dataset" CLI):

```bash
cd Isaac-GR00T
# 1. metadata/files consistent? (drops episodes whose files are missing; --dry-run only reports)
uv run python scripts/repair_lerobot_metadata.py /data/droid_style_ds --embodiment-tag OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT --dry-run
# 2. DROID rotation convention of your eef_9d vs the pretrained normalization stats (exit 0 = PASS)
uv run python scripts/verify_droid_rotation_correction.py --dataset-path /data/droid_style_ds
# 3. data loads and base model gives sane MSE/MAE on your episodes (zero-shot)
uv run python scripts/deployment/standalone_inference_script.py \
    --model-path nvidia/GR00T-N1.7-3B --dataset-path /data/droid_style_ds \
    --embodiment-tag OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT --traj-ids 0 1 \
    --inference-mode pytorch --execution-horizon 8
# 4. repo-config consistency only (modality.json examples vs MODALITY_CONFIGS), not your dataset:
uv run python scripts/validate_hf_config_alignment.py
```

- After training, open-loop eval (README; the second form needs a server launched WITHOUT `--use-sim-policy-wrapper`, **UNVERIFIED** compatibility):

```bash
uv run python gr00t/eval/open_loop_eval.py \
    --dataset-path /data/droid_style_ds \
    --embodiment-tag OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT \
    --model-path /data/ckpt/droid_ft/checkpoint-20000 \
    --traj-ids 0 --execution-horizon 8
```

Troubleshooting from the fine-tune guide: flat/rising MSE across checkpoints = LR too low or data not loading; flat constant prediction = `modality.json` key mismatch; huge/NaN MSE = normalization problem, check `meta/stats*`.

### 3.4 Recommended steps, batch size, GPU memory

- Hardware doc (hardware_recommendation.md): fine-tuning "minimum 1 GPU with 40 GB+ VRAM"; default tuning (projector + diffusion head, LLM/ViT frozen) keeps peak VRAM "under ~35 GB per GPU"; `--tune-llm` or `--tune-visual` needs 80 GB+ per GPU; recommended 4-8x H100/L40 with global batch 64-640; full scale 8x RTX PRO 6000 (96 GB each) at batch 640. A 96 GB RTX PRO 6000 can hold a larger per-GPU batch than 32; start at 32 and raise while watching `nvidia-smi` (the ~35 GB figure is not tied to a batch size in the docs, **UNVERIFIED**).
- Effective batch per optimizer step = `global_batch_size` x `gradient_accumulation_steps`. The community RTX 5090 (32 GB) guide used `--global-batch-size 4 --gradient-accumulation-steps 8` and optionally `--no-tune-projector` (third party, **UNVERIFIED**).
- Steps: guide example 2,000 steps at batch 32 for a 5-episode toy set; DROID recipe 20,000 steps at batch 640 (save every 1,000). README Training Tips: "Prioritize large batch sizes within hardware constraints and train for thousands of steps"; "Expect 5-6% variance between runs".
- Data volume (FAQ): about 100 trajectories for simple tasks, 500+ for complex scenes.
- The dataloader is CPU-based (FAQ): keep `--dataloader-num-workers >= 4`; the Nebius `1gpu-24vcpu-218gb` preset has 24 vCPUs.
- Enable held-out eval during training with `--eval-strategy steps --eval-steps 500` (fine-tune guide; the flags are not in `FinetuneConfig` as fetched, **UNVERIFIED**).
- Run it on the Nebius RTX PRO 6000, not the 8 GB laptop.

---

## 4. Isaac Sim on Blackwell (RTX 50-series / sm_120)

Sources:
- https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/requirements.html and https://docs.isaacsim.omniverse.nvidia.com/latest/installation/requirements.html
- https://docs.isaacsim.omniverse.nvidia.com/5.1.0/overview/known_issues.html , .../latest/overview/known_issues.html , .../5.1.0/installation/install_python.html
- https://api.github.com/repos/isaac-sim/IsaacSim/releases , https://api.github.com/repos/isaac-sim/IsaacLab/releases
- https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html and .../pip_installation.html
- https://api.github.com/search/issues?q=repo:isaac-sim/IsaacLab+... (issues #3477, #4261, #4371, #4951, #4961, #5001, #5671), IsaacSim issues (Blackwell search)
- https://raw.githubusercontent.com/NVlabs/RoboLab/main/docs/known_issues.md , docs/env_vram_size_guide.md
- https://pytorch.org/blog/pytorch-2-7/

| Isaac Sim | Released | Python | Linux driver stated in docs | Blackwell evidence | Usable by RoboLab |
|---|---|---|---|---|---|
| 5.0.0 | 2025-08-08 | 3.11 | **UNVERIFIED** (5.0 docs return 404) | Isaac Lab #3477: RTX PRO 6000 Blackwell + driver 580.65.06 gave a Warp `cuDeviceGetUuid` init error (open; some users fixed on 580.95.05, others not) | yes, `--extra isaac50` (Isaac Lab 2.2.0) |
| 5.1.0 | 2025-10-21 | 3.11 | **580.65.06** (minimum and tested) | Requirements table lists GeForce RTX 5080 as "Good" and RTX PRO 6000 Blackwell as "Ideal"; maintainer on #4951: "driver must be a 580 supported driver, e.g., 580.65.06". Docs banner: "Unsupported release" | yes, `--extra isaac51` (Isaac Lab 2.3.2.post1) |
| 6.0.0 / 6.0.1 | 2026-06-04 / 2026-06-22 | 3.12 | not fetched | nebius-physical-ai validated Isaac Lab 3.0.0b2.post1 + Sim 6.0.1.0 on RTX PRO 6000 | no |
| 6.1.0 | 2026-09-10 | 3.12 | **595.58.03** tested (users report running it on 580.126.20) | RTX PRO 6000 Blackwell is the "Ideal" GPU | no |
| 7.0.0a1 | 2026-09-18 (prerelease) | - | - | - | no |

Support for sm_120 in 4.5 and earlier: **UNVERIFIED** (docs 404); assume not supported. Isaac Lab pairing: v2.2.1 (2025-08-29) <-> Sim 5.0; v2.3.0 (2025-10-28, "built on Isaac Sim 5.1") through v2.3.2 (2026-02-02) <-> Sim 5.1; v3.0.0-beta2 (2026-06-17) <-> Sim 6.0; v3.0.0-beta2.patch1 <-> 6.0.1; v3.0.0-EA (2026-09-16) <-> Sim 6.1 (GA targeted end of Oct 2026). Your driver 580.173.02 meets the 5.1 minimum (580.65.06) and is newer than the 580.95.05 that fixed some #3477 reports; it is below the 595.58.03 that 6.1 was tested on (not necessarily a blocker).

Hardware table (5.1.0 docs): minimum GeForce RTX 4080 / 16 GB VRAM / 32 GB RAM / 4 cores; good RTX 5080 / 16 GB / 64 GB; ideal RTX PRO 6000 Blackwell / 48 GB / 64 GB. "GPUs without RT Cores (A100, H100) are not supported." Ubuntu 22.04/24.04. pip install needs GLIBC 2.35+. Mobile/laptop GPUs are not listed anywhere in the requirements.

Torch with Isaac Lab (pip docs; the page itself never mentions Blackwell): `pip install -U torch==2.7.0 torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu128` (RoboLab's pyproject already routes torch to cu128). Isaac Lab #4371: the PyPI-default `torch==2.7.0` (cu126) fails on sm_120; "torch==2.9.0 works". Whether your laptop needs a cu129 swap inside the RoboLab venv: **UNVERIFIED**, check `torch.cuda.get_arch_list()` the same way as section 1.4.

Known issues relevant to you:
1. **TiledCamera hang on laptop Blackwell** (Isaac Lab #4951 and #5001, Isaac Sim 5.1.0 / Isaac Lab 0.53.1): RTX 5090 Laptop (GB203), driver 590.48.01, process at 100% CPU for 10+ minutes, root cause in `omni.replicator` tiled rendering on that chip; desktop 5090 (GB202, driver 570.211.01) works. Workaround: `Camera` instead of `TiledCamera`. Closed without a fix; maintainers suggested retesting on Isaac Sim 6.0.x / Isaac Lab 3.0. RoboLab is hard-wired to `TiledCameraCfg`.
2. **`omni.cubric` deadlock on sm_120** (Isaac Lab #5671, "missing sm_120 cubin causes env.reset() hang via PhysX-Fabric", closed 2026-05-18, no public details). RoboLab calls `create_env(..., use_fabric=True)`. Whether `use_fabric=False` avoids it: **UNVERIFIED**.
3. Isaac Sim 5.1 known issue: Franka Open Drawer example fails on Blackwell unless `self._physics_rate` is raised to 600. Contact-rich physics can differ on Blackwell (and RoboLab warns grasp dynamics differ between 5.0 and 5.1), so re-measure rather than trusting published success rates.
4. Isaac Lab #4261 (open): `TiledCameraCfg` placement problem when reusing existing USD camera prims, Isaac Sim 5.1.0 on RTX PRO 6000 Blackwell.
5. Isaac Sim 5.1 known issue: viewport resolutions above available VRAM -> `ERROR_OUT_OF_DEVICE_MEMORY`. RoboLab: always `--headless` (VRAM leak otherwise); its env ceilings were measured on a 48 GB L40.
6. Isaac Lab #3477: early 580.x drivers + Blackwell: Warp `cuDeviceGetUuid` error at startup. Update the driver if you see it.
7. GR00T issue #590 (open): G1 whole-body eval on an RTX 5080 Laptop gave about 1% success vs 58% expected; cause unknown. Treat laptop-Blackwell sim numbers as suspect.
8. Isaac Sim 6.1 issues seen on Blackwell (RTX Lidar ray types, `simulation_app.update()` livelock on 5090 in IsaacSim #729): not relevant to RoboLab on 5.x.

Practical call: do the RoboLab evals on the Nebius RTX PRO 6000 (GB202, 96 GB); on the laptop only try `uv run pytest tests/` and a 1-env smoke test if you want to find out, expecting possible TiledCamera hangs and out-of-memory at 8 GB.

---

## 5. Nebius: RTX PRO 6000 VM, quota, and nebius-physical-ai

Sources:
- https://github.com/nebius/nebius-physical-ai (README.md, docs/quickstart.md, docs/install.md, docs/configuration.md, docs/cluster-backends.md, docs/fleet-rtx-pro-6000-mig.md, docs/orchestration/skypilot-setup.md, docs/workbench/image-gpu-compatibility-matrix.md, docs/workbench/mk8s-gpu-driver-strategy.md, docs/workbench/isaac-lab-3.md, docs/workbench/guides/quadruped-isaac-lab.md, docs/workbench/container-image-catalog.md, docs/workbench/huggingface-token.md, docs/workbench/runtime-modes.md, docs/workbench/preemptible-vms.md, docs/workbench/isaac-arena.md, docs/workbench/cookbooks/groot-1-7-training.md, docs/cli/groot.md, docs/cli/isaac-lab.md, workflows/testing/groot-1-7-finetune.yaml, workflows/testing/isaac-arena-evaluation-rtxpro.yaml, docs/workbench/troubleshooting/known-footguns.md), all under https://raw.githubusercontent.com/nebius/nebius-physical-ai/main/
- https://docs.nebius.com/compute/virtual-machines/types , /overview/regions , /compute/resources/quotas-limits , /overview/quotas , /compute/virtual-machines/manage , /compute/quickstart , /compute/storage/boot-disk-images , /cli/install , /cli/configure , /cli/reference/compute/instance/create , /cli/reference/compute/platform/list , /cli/reference/quotas/quota-allowance/list

### 5.1 Region: uk-south2 or eu-south1?

- Nebius platform docs: RTX PRO 6000 platform **`gpu-rtx6000-a`** is in **uk-south2 and eu-south1**; the plain **`gpu-rtx6000`** is in **us-central1** only. Presets for both: `1gpu-24vcpu-218gb` (1 GPU, 24 vCPU, 218 GiB RAM) and `8gpu-192vcpu-1744gb`. GPU: RTX PRO 6000 Blackwell, 96 GB GDDR7. Regions: uk-south2 = United Kingdom, eu-south1 = Madrid, Spain.
- Default quota "Total NVIDIA RTX PRO 6000 GPUs" (regular VMs, no reservation): **32 in uk-south2, 32 in eu-south1, 0 in us-central1** (also Regular VMs 12 and Preemptible VMs 8 per region; non-GPU vCPUs 200).
- The nebius-physical-ai repo does NOT hard-code uk-south2 or eu-south1 in anything I read. Its examples use `region: us-central1` + `gpu-rtx6000` (cluster-backends.md fleet YAML, fleet-rtx-pro-6000-mig.md) and `eu-north1` (configuration.md, CLI install URL); mk8s-gpu-driver-strategy.md says the `rtx-rendering` profile "selects `gpu-rtx6000`, or preserves an explicitly resolved zonal variant such as `gpu-rtx6000-a`". Use either uk-south2 or eu-south1 (both have `gpu-rtx6000-a` and 32-GPU default quota); the choice is just which region your Nebius project lives in. Region is a property of the project, so create/use a project in that region and a CLI profile bound to it. Your memory note ("use RTX PRO 6000 in uk-south2/eu-south1, default quota is 0 in us-central1, H100s can't render Isaac Sim") matches the docs above.
- Driver on npa-tested RTX PRO 6000 nodes: 580.126.09, 580.159.04, 580.173.02 (same 580.173.02 as your laptop). CUDA 13.0 image + 580.x driver runs cu128/cu129 PyTorch wheels fine (driver is backward compatible; **UNVERIFIED** in these docs).

### 5.2 Nebius CLI: install, profile, quota, create a VM

```bash
# install (official docs)
curl -sSL https://artifacts.nebius.cloud/cli/install.sh | bash
exec -l $SHELL
nebius version
# or the version nebius-physical-ai pins/tests (0.12.254):
#   curl -fsSL https://storage.eu-north1.nebius.cloud/cli/install.sh | NEBIUS_CLI_VERSION=0.12.254 bash
#   export PATH="${HOME}/.nebius/bin:${PATH}"

# one profile per project/region (docs: "separate profile for each project ... region-specific configuration")
export PROFILE_NAME=lp-eu-south1
export PROJECT_ID=<project-id-of-a-project-in-eu-south1-or-uk-south2>
nebius profile create --profile $PROFILE_NAME \
    --endpoint api.nebius.cloud --federation-endpoint auth.nebius.com \
    --parent-id $PROJECT_ID                       # opens a browser for federation login
nebius profile list

# (tenant admin) create a project in the wanted region (nebius-physical-ai docs/configuration.md):
#   nebius iam v2 project create --parent-id "$TENANT_ID" --name "$PROJECT_NAME" --region eu-south1 --format json

# what exists in this project/region
nebius compute platform list --parent-id $PROJECT_ID           # look for gpu-rtx6000-a and preset 1gpu-24vcpu-218gb
nebius compute image list-public --region eu-south1            # confirm image family ubuntu24.04-cuda13.0
nebius quotas quota-allowance list --parent-id $PROJECT_ID --all --format json   # read current GPU/vCPU/disk quotas
```

**Requesting quota** (Nebius docs, /overview/quotas): web console only. Administration -> Limits -> Quotas tab -> select the service (Compute) -> in the row of the quota (e.g. "Total NVIDIA RTX PRO 6000 GPUs") click the menu -> **Change quota** -> enter the new value and send. Only users in a group with the `admin` role can do it; track the request in the support center (console.nebius.com/support). No CLI request method, processing time, or per-quota ID string is documented (**UNVERIFIED**; the CLI can only list: `nebius quotas quota-allowance list`). Note from the docs: a VM and its resources count against quota "from its creation to deletion, regardless of whether it is running or stopped", and Nebius auto-reduces quotas that sit far below usage (email with a grace period, typically 2 days). With the 32-GPU default in uk-south2/eu-south1 you likely need no increase for a 1-GPU (or 8-GPU) VM. Your memory-note cut line "Oct 8 Nebius quota" can become "verify the quota row shows 32".

**Create the VM** (platform/preset from the types page; image family recommended for RTX PRO 6000 platforms: `ubuntu24.04-cuda13.0` = CUDA 13.0 + NVIDIA driver 580.x; alternative `ubuntu24.04-cuda13-latest`; `ubuntu24.04-cuda12` has driver 570.x, avoid). Flags are from /compute/quickstart and /compute/virtual-machines/manage; `--parent-id` is marked required in the CLI reference (the profile normally supplies it, passing it is harmless):

```bash
export SUBNET_ID=$(nebius vpc subnet list --parent-id $PROJECT_ID --format jsonpath='{.items[0].metadata.id}')

export USER_DATA=$(jq -Rrs '.' <<EOF
#cloud-config
users:
  - name: $USER
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/bash
    ssh_authorized_keys:
      - $(cat ~/.ssh/id_ed25519.pub)
EOF
)

export VM_ID=$(nebius compute instance create \
  --parent-id $PROJECT_ID \
  --name lp-rtx6000 \
  --resources-platform gpu-rtx6000-a \
  --resources-preset 1gpu-24vcpu-218gb \
  --boot-disk-managed-disk-name lp-rtx6000-boot \
  --boot-disk-managed-disk-type network_ssd \
  --boot-disk-managed-disk-size-gibibytes 300 \
  --boot-disk-managed-disk-block-size-bytes 4096 \
  --boot-disk-managed-disk-source-image-family-image-family ubuntu24.04-cuda13.0 \
  --boot-disk-attach-mode READ_WRITE \
  --cloud-init-user-data "$USER_DATA" \
  --network-interfaces "[{\"name\": \"eth0\", \"subnet_id\": \"$SUBNET_ID\", \"ip_address\": {}, \"public_ip_address\": {}}]" \
  --format jsonpath='{.metadata.id}')

export VM_IP=$(nebius compute instance get --id $VM_ID --format json \
  | jq -r '.status.network_interfaces[0].public_ip_address.address | split("/")[0]')
ssh $USER@$VM_IP
nvidia-smi                       # expect RTX PRO 6000 Blackwell, 96 GB, driver 580.x
```

Do not use `root`/`admin` as the cloud-init user (docs). 300 GiB is my sizing (Isaac Sim pip wheels, ~7 GB RoboLab assets, HF weights, outputs; the docs example uses 50 GiB, **UNVERIFIED** that 300 is right). For 8 GPUs (DROID recipe) use `--resources-preset 8gpu-192vcpu-1744gb`.

Stop/delete: `nebius compute instance stop --id $VM_ID` (still counts against quota); `nebius compute instance delete --id $VM_ID`. Check `nebius compute disk list --parent-id $PROJECT_ID` afterwards for a leftover boot disk (**UNVERIFIED** whether managed boot disks are deleted with the VM). The workbench docs say npa-managed GPU VMs are preemptible by default (`--no-preemptible` to disable); a raw `nebius compute instance create` as above is not.

### 5.3 Plain-VM run of the whole stack (recommended for RoboLab)

On the VM, repeat sections 1.1-1.5 (GR00T + server) and 2.1-2.4 (RoboLab) unchanged. Differences: `tmux`, 127.0.0.1 everywhere, no cu129 swap unless the section 1.4 check fails, and headless Vulkan must work for Isaac Sim rendering. Pre-flight on the VM (the Vulkan check is **UNVERIFIED** for this image; install `vulkan-tools` and, if no device shows, the matching `libnvidia-gl-580*` package):

```bash
sudo apt-get install -y vulkan-tools && vulkaninfo --summary | head -30     # must list the RTX PRO 6000
tmux new -s gr00t       # window 1: server (section 1.5)
tmux new -s robolab     # window 2: eval  (section 2.3)
# dashboard over SSH tunnel from your laptop:  ssh -L 8080:localhost:8080 $USER@$VM_IP
```

### 5.4 What nebius-physical-ai gives you (SkyPilot / npa workbench)

The repo is a control plane ("npa") that runs workloads on **Nebius Managed Kubernetes via SkyPilot** (SkyPilot 0.12.2 pinned) or, for workbenches, on managed or bring-your-own VMs. Quickstart commands (README, docs/install.md, docs/configuration.md):

```bash
git clone https://github.com/nebius/nebius-physical-ai.git
cd nebius-physical-ai
python3 -m venv .venv && source .venv/bin/activate
pip install -e npa
npa --version
curl -fsSL https://storage.eu-north1.nebius.cloud/cli/install.sh | NEBIUS_CLI_VERSION=0.12.254 bash
export PATH="${HOME}/.nebius/bin:${PATH}"
npa configure                                         # tenant/project/region; provisions a bucket by default
npa workbench health preflight --checks nebius --json
# gated HF models (docs/workbench/huggingface-token.md):
npa configure --prepare-catalog-access                # lists gated assets; you must accept licences on huggingface.co yourself
export HF_TOKEN=hf_xxx                                # or put it in ~/.npa/credentials.yaml under tokens.HF_TOKEN
npa workbench health access --prepare
```

Kubernetes + SkyPilot route (docs/orchestration/skypilot-setup.md, docs/workbench/mk8s-gpu-driver-strategy.md, docs/cluster-backends.md):

```bash
npa cluster up --gpu-workload-profile rtx-rendering   # picks gpu-rtx6000 (or an explicitly resolved zonal variant such as gpu-rtx6000-a); validates Vulkan on every GPU node
npa skypilot bootstrap
export NPA_SKYPILOT_BIN="$(npa skypilot status --bin-path)"
npa skypilot verify --cluster "<npa-cluster-context>" --kubeconfig "<selected-kubeconfig>"
# the repo's own RTX PRO 6000 example (MIG split, needs a capacity block group; us-central1 in the example):
npa cluster up --gpu-nodes 2 --gpu-platform gpu-rtx6000 --gpu-preset 1gpu-24vcpu-218gb \
  --capacity-block-group "$NPA_CAPACITY_BLOCK_GROUP" --mig --mig-strategy mixed --mig-config all-balanced
# tear down when finished:
npa destroy --project "<alias>" --all
```

SkyPilot accelerator spellings used in the repo: `RTXPRO6000:1` (skypilot-setup.md, byof-droid-policy-learning.yaml) and `RTXPRO-6000-BLACKWELL-SERVER-EDITION:1` (isaac-arena-evaluation-rtxpro.yaml). Whether mk8s RTX PRO 6000 nodes can be had without a reservation/capacity block group: **UNVERIFIED** (the example passes one; plain VMs under the default quota need none).

Workbenches (docs/workbench/isaac-lab-3.md, quadruped-isaac-lab.md, docs/cli/groot.md, docs/cli/isaac-lab.md):

```bash
# Isaac Lab (Isaac Lab 3.0.0b2.post1 + Isaac Sim 6.0.1.0, Ubuntu 24.04, Python 3.12, CUDA 12.8, PyTorch 2.11; container only, "Native VM installation unsupported for generation 3")
npa workbench isaac-lab deploy --runtime container --gpu-type "<discovered-rtx-platform>" --gpu-preset "<matching-preset>"
npa workbench isaac-lab list
npa workbench isaac-lab system-info          # confirms the GPU is RT-capable (RTX PRO 6000 or L40S; H100/H200/B200 not)
npa workbench isaac-lab train --task Isaac-Velocity-Flat-Anymal-C-v0 --num-envs 1024 --steps 200 --output-path s3://<bucket>/isaac-lab/anymal-flat/
npa workbench isaac-lab eval --task Isaac-Velocity-Flat-Anymal-C-v0 --input-path s3://<bucket>/isaac-lab/anymal-flat/ --num-episodes 20 --max-steps-per-episode 1000 --success-metric survival --min-success-rate 0.90 --output-path s3://<bucket>/isaac-lab/anymal-flat-eval/

# GR00T workbench subcommands (docs/cli/groot.md): deploy ("a GR00T runtime VM with Isaac Lab available for sim evaluation"), register-byovm, download, finetune, eval, serve, infer, convert, status, system-info
npa workbench groot --help
npa workbench groot deploy --help            # exact flags for deploy/serve/finetune are NOT in the docs I could fetch: UNVERIFIED, read --help
# bring-your-own VM pattern (documented for lerobot; same shape expected for groot/isaac-lab, UNVERIFIED):
#   npa workbench <tool> -p "<alias>" -n "<name>" deploy --runtime byovm --host "<ssh-host>" --ssh-user ubuntu --ssh-key ~/.ssh/id_ed25519
# public image (GR00T-N1.7-3B inference; validated on B200 and RTX PRO 6000; Isaac Sim/Lab are fetched at runtime under ACCEPT_EULA):
docker pull ghcr.io/nebius/nebius-physical-ai/npa-groot:0.1.0
```

GR00T N1.7 fine-tune workflow shipped in the repo (workflows/testing/groot-1-7-finetune.yaml, docs/workbench/cookbooks/groot-1-7-training.md): a 4-step optimizer smoke test on **B200:2**, not RTX PRO 6000 (its doc: "It does not request RTX PRO 6000"). Submit shape: `npa workbench workflow submit workflows/testing/groot-1-7-finetune.yaml --run-id <id> --var bucket=<bucket> --var source_data_uri=s3://<bucket>/datasets/<ds>/ --var gpu_type=B200 --var gpu_count=2 --var per_device_batch_size=1 --var gradient_accumulation_steps=1 --var global_batch_size=2 --registry <registry>/npa-groot:<tag> --secret-env HF_TOKEN`. Nothing in the repo covers RoboLab, DROID eval, or Isaac Sim 5.x; the closest RTX PRO 6000 eval is Isaac Lab-Arena (`workflows/testing/isaac-arena-evaluation-rtxpro.yaml`, GR1 microwave replay). The repo's own footgun list notes "Xet Transfer Rejects Gated Cosmos Downloads" (a specific package pair breaks; newer releases fix it).

Honest recommendation: for this project the Nebius CLI plain VM (5.2 + 5.3) is the shortest path; use npa only if you want S3 artifact plumbing or managed clusters.

---

## 6. UNVERIFIED / open items checklist

1. `uv pip install ... --torch-backend=cu129` on this exact stack, and whether the cu128 default already works on the laptop (conflicting evidence, section 1.4).
2. flash-attn 2.8.3 wheel kernels on sm_120 (fix claimed in GR00T PR #560; GR00T issues #733/#734 show cu128 on 5090).
3. RoboLab exit code on failure; `policy` field value `"gr00t"`; absence of a video-path field in JSONL for GR00T runs.
4. RoboLab on Isaac Sim 5.0 vs 5.1 on Blackwell: which stack produced the published 8.58%; 5.0 Blackwell driver requirement; `use_fabric` hang workaround.
5. (Resolved from pyproject: plain `uv sync` installs no simulator; use `--extra isaac50|isaac51`. Left here because the Isaac-GR00T example README still says plain `uv sync`.)
6. Whether Isaac-GR00T `demo_data/*` needs git-lfs (131-byte parquet files listed).
7. 5.3 Vulkan availability on `ubuntu24.04-cuda13.0` GPU image; boot-disk cleanup on VM delete; 300 GiB sizing.
8. `npa workbench groot|isaac-lab deploy` exact flags; mk8s RTX PRO 6000 without capacity block group; BYOVM flags for groot/isaac-lab.
9. Nebius quota approval time and CLI path (none documented).
10. DROID fine-tune: batch-size vs VRAM mapping on 96 GB; relative-action conversion at load time (inferred); `--eval-strategy` flags; fine-grained HF token permission wording.
11. Laptop capability: 8 GB VRAM from your memory note, not re-checked here (`nvidia-smi --query-gpu=name,memory.total --format=csv`).
