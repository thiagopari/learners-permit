#!/usr/bin/env bash
# Collect GR00T's own successful RedDishesInBin episodes for filtered behaviour cloning, on the GPU VM.
#   bash collect.sh FIRST_SEED LAUNCHES ENVS
# Each launch is one RoboLab run of ENVS recorded episodes on its own seed. Training seeds start at FIRST_SEED
# (1001); evaluation later uses other seeds. After each launch, extract.py keeps the successes (small videos and
# arrays) and the raw HDF5 (~2 GB per episode) is deleted before the next launch, so the disk never fills.
set -uo pipefail
first=${1:-1001} launches=${2:-10} envs=${3:-20}
out=~/finetune/episodes; mkdir -p "$out"
log=~/finetune/collect.jsonl
for ((i = 0; i < launches; i++)); do
    seed=$((first + i)) folder=lp_rf_$((first + i))
    cd ~/RoboLab && rm -rf "output/$folder"
    t0=$(date +%s)
    OMNI_KIT_ACCEPT_EULA=Y timeout -k 60 3600 ~/.local/bin/uv run python policies/gr00t/run.py --headless \
        --remote-host 127.0.0.1 --remote-port 5600 --task RedDishesInBinTask --num-envs "$envs" --num-runs 1 \
        --open-loop-horizon 8 --instruction-type default --video-mode none --record-image-data --seed "$seed" \
        --output-folder-name "$folder" > ~/finetune/launch_$seed.log 2>&1
    rc=$?
    if [ -f "output/$folder/episode_results.jsonl" ]; then
        res=$(~/RoboLab/.venv/bin/python ~/learners-permit/cloud/finetune/extract.py "output/$folder" "$out" "$seed")
    else
        res='{"error": "no episode_results.jsonl"}'
    fi
    rm -rf "output/$folder"  # the raw recording: ~2 GB per episode
    echo "{\"seed\": $seed, \"exit\": $rc, \"minutes\": $(( ($(date +%s) - t0) / 60 )), \"extract\": $res}" | tee -a "$log"
    echo "successes so far: $(ls "$out" | wc -l)"
done
