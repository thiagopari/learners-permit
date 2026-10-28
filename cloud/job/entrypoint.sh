#!/usr/bin/env bash
# Runs inside the Serverless Job: check the GPU, fetch weights, start the GR00T policy server, then run one
# commissioning sweep (LP_MODE=sweep, the default) or the first session's measurements (LP_MODE=measure).
#
# Everything the run produces goes to $LP_RESULTS/$LP_RUN_ID, a folder in the mounted Object Storage bucket: the job's
# own disk is wiped when it ends. The sweep's checkpoint is copied there after every batch, so a preempted or failed
# job, restarted with the same LP_RUN_ID, continues from its last finished batch.
#
# Time limits: every step has its own, and the whole run stops LP_BUDGET_MIN minutes after start (keep it under the
# job's --timeout), so results are always copied out before the platform kills the container.
set -euo pipefail
# /opt for cloud/job/Dockerfile; /home/permit for Dockerfile.vm, which packages a VM where setup passed
P=${LP_PREFIX:-/opt} LP=${LP_PREFIX:-/opt}/learners-permit GR00T=${LP_PREFIX:-/opt}/Isaac-GR00T ROBOLAB=${LP_PREFIX:-/opt}/RoboLab
: "${LP_RUN_ID:?set LP_RUN_ID (cloud/job.sh run sets it)}"
dest=${LP_RESULTS:-/results}/$LP_RUN_ID
mkdir -p "$dest"
exec > >(tee -a "$dest/job.log") 2>&1
t0=$(date +%s) budget=${LP_BUDGET_MIN:-210}
step() { echo; echo "== [$(( ($(date +%s) - t0) / 60 )) min] $*"; }
left() { echo $(( budget - ($(date +%s) - t0) / 60 )); }  # minutes left in the run's budget
server=""

finish() {
    local rc=$?
    [ -z "$server" ] || kill -- "-$server" 2> /dev/null || true
    # RoboLab's per-episode results and any recorded video, for the licence card's clips
    [ ! -d "$ROBOLAB/output" ] || cp -r "$ROBOLAB/output/." "$dest/robolab-output/" 2> /dev/null || true
    [ ! -f ~/gr00t-server.log ] || cp ~/gr00t-server.log "$dest/"
    echo "$rc" > "$dest/status"
    echo "exit status $rc (0 = the run finished; the sweep's verdict is in summary.json)"
}
trap finish EXIT
mkdir -p "$dest/robolab-output"
cp "$P/versions.txt" "$dest/versions.txt" 2> /dev/null || true

step "GPU, driver and Vulkan"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader | tee -a "$dest/versions.txt"
vulkaninfo --summary 2> /dev/null | grep -i 'deviceName' | grep -q -i nvidia \
    || { echo "Vulkan sees no NVIDIA GPU, so Isaac Sim can't render. Is the platform one with RT cores?"; exit 1; }

step "Model weights"
cd "$GR00T"
if [ "${HF_HUB_OFFLINE:-0}" = 1 ]; then
    echo "baked into the image (Dockerfile.vm): no download, no HF token needed"
else  # GR00T's backbone (Cosmos-Reason2-2B) is gated: accept it on huggingface.co, and pass HF_TOKEN as a secret
    : "${HF_TOKEN:?no HF_TOKEN: cloud/job.sh run passes it with --env-secret}"
    [ ! -d /cache ] || export HF_HOME=/cache/huggingface  # an optional mounted volume saves the download next time
    timeout -k 30 30m uv run hf download nvidia/Cosmos-Reason2-2B > /dev/null
    timeout -k 30 30m uv run hf download nvidia/GR00T-N1.7-DROID > /dev/null
fi

step "GR00T policy server on 127.0.0.1:5600"
CUDA_VISIBLE_DEVICES=0 setsid uv run python gr00t/eval/run_gr00t_server.py --model-path nvidia/GR00T-N1.7-DROID \
    --embodiment-tag OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT --device cuda --host 127.0.0.1 --port 5600 \
    --use-sim-policy-wrapper > ~/gr00t-server.log 2>&1 &
server=$!
for _ in $(seq 180); do  # up to 15 minutes
    ss -ltn | grep -q "127.0.0.1:5600 " && break  # it prints no "ready" line: the open port is the signal
    kill -0 "$server" 2> /dev/null || { tail -30 ~/gr00t-server.log; echo "the GR00T server died"; exit 1; }
    sleep 5
done
ss -ltn | grep -q "127.0.0.1:5600 " || { tail -30 ~/gr00t-server.log; echo "not listening after 15 min"; exit 1; }

cd "$LP"
export ROBOLAB_DIR=$ROBOLAB LP_STATE=$dest
[ "$(left)" -gt 5 ] || { echo "no time left in the ${budget}-minute budget"; exit 1; }
case "${LP_MODE:-sweep}" in
sweep)
    step "Commissioning sweep: ${LP_SKILL:?set LP_SKILL}, tier ${LP_TIER:-supervised} ($(left) min left)"
    timeout -k 60 "$(left)m" .venv/bin/python cloud/job/sweep.py
    ;;
measure)
    step "The first session's measurements: cloud/measure.py ($(left) min left)"
    HOME_OUT=~/lp-measurements.jsonl
    timeout -k 60 "$(left)m" .venv/bin/python cloud/measure.py || rc=$?
    [ ! -f "$HOME_OUT" ] || cp "$HOME_OUT" "$dest/measurements.jsonl"
    exit "${rc:-0}"
    ;;
*) echo "LP_MODE must be sweep or measure"; exit 1 ;;
esac
