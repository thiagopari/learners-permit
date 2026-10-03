#!/usr/bin/env bash
# Run on the GB10 right after plugging in the HACK drive:
#   bash /media/$USER/HACK/setup_on_box.sh        (or wherever the drive mounted)
# Copies models to the internal NVMe, loads the images, checks the GPU, starts the cell container
# and both GR00T policy servers. About 15-25 minutes, mostly copying and `docker load`.
set -euo pipefail
USB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HOME/hack"
log() { echo; echo "== [$(date +%H:%M:%S)] $* =="; }

log "Box"
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader || true
docker version --format 'docker {{.Server.Version}}'
df -h "$HOME" | tail -1

log "Copy models, checkpoints and notes to the internal disk"
mkdir -p "$DEST" "$HOME/.cache/huggingface"
rsync -a --info=progress2 "$USB/hf/" "$HOME/.cache/huggingface/"
rsync -a --info=progress2 "$USB/ckpt" "$USB/src" "$USB/notes" "$DEST/"

log "Load images (vLLM for NemoClaw, and hack/cell)"
for t in "$USB"/images/*.tar; do echo "loading $(basename "$t")"; docker load -i "$t"; done
docker image inspect --format '{{index .RepoTags 0}}  {{.Architecture}}' \
  nvcr.io/nvidia/vllm:26.05.post1-py3 hack/cell

log "GPU visible inside the cell image"
docker run --rm --gpus all hack/cell nvidia-smi -L

if ! ls -d "$HOME/.cache/huggingface/hub/models--nvidia--Cosmos-Reason2-2B/snapshots/"* >/dev/null 2>&1; then
  cat <<'EOF'

!! Cosmos-Reason2-2B is not on the drive. GR00T loads it as its vision-language backbone, so the
!! policy servers below will fail until it is downloaded (about 5 GB, gated: accept its terms on Hugging Face):
!!   docker exec -it cell bash -c 'export HF_HUB_OFFLINE=0; hf auth login && hf download nvidia/Cosmos-Reason2-2B'
!! (run that after the cell container starts, then restart the servers; log out with `hf auth logout` before leaving)
EOF
fi

log "Start the cell container and both GR00T servers (libero_10 on 5555, libero_goal on 5556)"
docker rm -f cell >/dev/null 2>&1 || true
docker run -d --name cell --gpus all --network host --ipc host \
  -e NVIDIA_DRIVER_CAPABILITIES=all -e NO_ALBUMENTATIONS_UPDATE=1 \
  -v "$HOME/.cache/huggingface:/hf" -v "$DEST/ckpt:/ckpt" -v "$DEST/src/app:/app" \
  hack/cell sleep infinity
for pair in "libero_10 5555" "libero_goal 5556"; do
  set -- $pair
  docker exec -d cell bash -c "python gr00t/eval/run_gr00t_server.py \
    --model-path /ckpt/GR00T-N1.7-LIBERO/$1 --embodiment-tag LIBERO_PANDA \
    --use-sim-policy-wrapper --host 127.0.0.1 --port $2 > /tmp/gr00t_$1.log 2>&1"
done

cat <<'EOF'

Done. Next, by hand:
  1. Wait for both servers:   docker exec cell tail -f /tmp/gr00t_libero_10.log   (look for "Server is ready and listening")
  2. Smoke rollout, two episodes (time it; it sizes the live commissioning):
       docker exec -it cell bash -c 'gr00t/eval/sim/LIBERO/libero_uv/.venv/bin/python gr00t/eval/rollout_policy.py \
         --n-episodes 2 --n-envs 1 --policy-client-host 127.0.0.1 --policy-client-port 5555 \
         --max-episode-steps 720 --n-action-steps 8 \
         --env-name libero_sim/LIVING_ROOM_SCENE2_put_both_the_alphabet_soup_and_the_tomato_sauce_in_the_basket'
  3. Drawer task on both policies (should be low on 5555, high on 5556):
       same command with --policy-client-port 5555 / 5556 and --env-name libero_sim/open_the_middle_drawer_of_the_cabinet
  4. NemoClaw onboarding (managed vLLM). The image is already loaded, so its digest pull only fetches
     the manifest; the weights are in ~/.cache/huggingface. Export HF_TOKEN first.
If something fails, see notes/gb10-hackathon-handoff.md section 7.3 and section 8 (gotchas).
EOF
