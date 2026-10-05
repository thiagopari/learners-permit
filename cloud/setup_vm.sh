#!/usr/bin/env bash
# One unattended setup of the GPU VM: the GR00T N1.7 policy server, RoboLab on Isaac Sim 5.0, and this repo's control
# plane, ending with 2 real episodes through permit's own RoboLab runner. `cloud/vm.sh setup` copies the repo here and
# runs this in tmux. Log: ~/lp-setup.log. Versions used: ~/lp-versions.txt (quote them with your success rates).
#
# Re-runnable: finished installs are skipped. Every GPU step has a time limit, so a hang (Blackwell has known ones in
# TiledCamera and omni.cubric, docs/RUNBOOK.md section 4) costs minutes, not hours. It holds /run/lp-keepalive while
# it runs, so the idle guard doesn't power the VM off in the middle of a download.
set -euo pipefail
exec > >(tee -a ~/lp-setup.log) 2>&1
LP=~/learners-permit GR00T=~/Isaac-GR00T ROBOLAB=~/RoboLab
export PATH="$HOME/.local/bin:$PATH" OMNI_KIT_ACCEPT_EULA=Y
t0=$(date +%s)
step() { echo; echo "== [$(( ($(date +%s) - t0) / 60 )) min] $*"; }
server=""
sudo touch /run/lp-keepalive
# shellcheck disable=SC2154  # rc is assigned inside the trap itself
trap 'rc=$?; sudo rm -f /run/lp-keepalive; [ -z "$server" ] || kill -- "-$server" 2> /dev/null; echo $rc > ~/lp-setup.status' EXIT

step "GPU, driver and Vulkan"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
driver=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)
# Isaac Lab #3477: early 580 drivers break Warp on Blackwell; 580.95.05 fixed it for some reporters.
dpkg --compare-versions "$driver" ge 580.95.05 || { echo "driver $driver predates 580.95.05 (RUNBOOK section 4)"; exit 1; }
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ffmpeg git git-lfs tmux jq vulkan-tools python3-venv
vulkaninfo --summary 2>/dev/null | grep -i 'deviceName' | grep -q -i nvidia \
    || { echo "Vulkan sees no NVIDIA GPU, so Isaac Sim can't render (RUNBOOK section 5.3)"; exit 1; }
git lfs install
ffmpeg -version | head -1  # torchcodec 0.8.0 loads FFmpeg 4-7 only; Ubuntu 24.04 ships 6
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh

step "GR00T N1.7 (Python 3.12)"
[ -d "$GR00T" ] || git clone --recurse-submodules https://github.com/NVIDIA/Isaac-GR00T "$GR00T"
cd "$GR00T"
uv sync --python 3.12
uv run python -c "import torch; a = torch.cuda.get_arch_list(); print(torch.__version__, a)
assert 'sm_120' in a, 'this torch has no Blackwell kernels: RUNBOOK section 1.4'"

step "Model weights (Cosmos-Reason2-2B is gated: accept it on huggingface.co first)"
[ -s ~/.cache/huggingface/token ] || { echo "no Hugging Face token: run cloud/vm.sh setup with HF_TOKEN set"; exit 1; }
uv run hf auth whoami
uv run hf download nvidia/Cosmos-Reason2-2B > /dev/null
uv run hf download nvidia/GR00T-N1.7-DROID > /dev/null

step "RoboLab on Isaac Sim 5.0 (Python 3.11; RoboLab's default stack)"
[ -d "$ROBOLAB" ] || git clone https://github.com/NVlabs/RoboLab "$ROBOLAB"  # git-lfs is installed, so assets come too
cd "$ROBOLAB"
git lfs pull
[ -d .venv ] || uv venv --python 3.11
uv sync --extra isaac50

step "Versions"
{ date -u +%FT%TZ
  echo "driver $driver"
  echo "Isaac-GR00T $(git -C "$GR00T" rev-parse --short HEAD)"
  echo "RoboLab $(git -C "$ROBOLAB" rev-parse --short HEAD), isaac50"
  echo "learners-permit $(cat "$LP/.commit" 2>/dev/null || echo unknown)"; } | tee ~/lp-versions.txt

step "RoboLab's install check: one full episode (the first Isaac Sim boot compiles shaders, so it is slow)"
timeout -k 60 45m uv run pytest -q tests/

step "Learner's Permit control plane"
cd "$LP"
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
.venv/bin/python -m pytest -q tests

step "GR00T policy server on 127.0.0.1:5555"
cd "$GR00T"
CUDA_VISIBLE_DEVICES=0 setsid uv run python gr00t/eval/run_gr00t_server.py --model-path nvidia/GR00T-N1.7-DROID \
    --embodiment-tag OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT --device cuda --host 127.0.0.1 --port 5555 \
    --use-sim-policy-wrapper > ~/gr00t-server.log 2>&1 &
server=$!
for _ in $(seq 180); do  # up to 15 minutes: the first load reads several GB of weights
    grep -q -E "Server (is )?ready" ~/gr00t-server.log && break
    kill -0 "$server" 2>/dev/null || { tail -30 ~/gr00t-server.log; echo "the GR00T server died"; exit 1; }
    sleep 5
done
grep -q -E "Server (is )?ready" ~/gr00t-server.log || { tail -30 ~/gr00t-server.log; echo "not ready after 15 min"; exit 1; }

step "End to end: 2 episodes of BananaOnPlateTask (NVIDIA's README: 40/40) through permit's RoboLab runner"
cd "$LP"
ROBOLAB_DIR="$ROBOLAB" timeout -k 60 45m .venv/bin/python -c "from permit import runners
print(runners.robolab('BananaOnPlateTask', {'n17_droid': 5555}, retries=0)({'n17_droid': 2}))"

step "Done"
df -h / | tail -1
echo "The idle guard powers the VM off after 30 idle minutes; to stop it now, run cloud/vm.sh stop on the laptop."
