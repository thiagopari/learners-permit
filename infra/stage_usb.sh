#!/usr/bin/env bash
# Fill the HACK drive on the laptop: models, the NemoClaw vLLM image, the cell image, notes.
# Usage: bash ~/hack-build/stage_usb.sh [ckpt|qwen|cosmos|models|vllm|cell|notes|all]
set -euo pipefail
USB="${USB:-/media/$USER/HACK}"
STEP="${1:-all}"
export PATH="$HOME/.local/bin:$PATH"
HF="$HOME/.venvs/hf/bin/hf"
[ -w "$USB" ] || { echo "Drive not writable at $USB (mount it and chown it to $USER first)"; exit 1; }
mkdir -p "$USB"/{images,hf,ckpt,src,notes}
log() { echo "[$(date +%H:%M:%S)] $*"; }

# The cache goes on the drive, but the login token stays on the laptop (never copied to the loaner box)
hfenv() {
  export HF_HOME="$USB/hf" HF_TOKEN_PATH="$HOME/.cache/huggingface/token" \
         HF_XET_CHUNK_CACHE_SIZE_BYTES=0 HF_XET_HIGH_PERFORMANCE=1
}

ckpt() {
  hfenv
  log "GR00T LIBERO checkpoints (libero_10 and libero_goal, inference files only)"
  # The hf CLI takes one pattern per --include flag (extra words become literal filenames)
  "$HF" download nvidia/GR00T-N1.7-LIBERO --local-dir "$USB/ckpt/GR00T-N1.7-LIBERO" \
    --include "libero_10/*.json" --include "libero_10/model-*.safetensors" \
    --include "libero_goal/*.json" --include "libero_goal/model-*.safetensors"
  log "ckpt done"
}

qwen() {
  hfenv
  log "Qwen3.6-35B-A3B-NVFP4 (NemoClaw's default model on Spark)"
  "$HF" download nvidia/Qwen3.6-35B-A3B-NVFP4
  log "qwen done"
}

cosmos() {
  hfenv
  log "Cosmos-Reason2-2B (gated: accept the terms on its Hugging Face page and run 'hf auth login' first)"
  "$HF" download nvidia/Cosmos-Reason2-2B
  log "cosmos done"
}

models() { ckpt; cosmos; qwen; }

vllm() {
  # Same arm64 manifest NemoClaw's Spark recipe pins (sha256:9204569b...). docker pull resumes and retries
  # layers on a flaky connection (crane restarts from zero), then docker save writes the arm64 image to the drive.
  local ref=nvcr.io/nvidia/vllm:26.05.post1-py3
  for i in 1 2 3 4 5 6; do
    log "docker pull $ref (attempt $i)"
    docker pull --platform linux/arm64 "$ref" && break
    [ "$i" = 6 ] && { echo "pull failed 6 times"; exit 1; }
    sleep 20
  done
  log "vLLM image -> $USB/images/vllm-26.05.post1-py3-arm64.tar"
  docker save --platform linux/arm64 -o "$USB/images/vllm-26.05.post1-py3-arm64.tar" "$ref"
  sync
  log "vllm done"
}

cell() {
  docker image inspect hack/cell >/dev/null 2>&1 || { echo "hack/cell not built yet"; exit 1; }
  [ "$(docker image inspect --format '{{.Architecture}}' hack/cell)" = arm64 ] || { echo "hack/cell is not arm64"; exit 1; }
  log "cell image -> $USB/images/cell-arm64.tar"
  docker save -o "$USB/images/cell-arm64.tar" hack/cell
  log "cell done"
}

notes() {
  cp ~/hack-build/Dockerfile.cell ~/hack-build/stage_usb.sh "$USB/src/"
  cp ~/hack-build/setup_on_box.sh "$USB/" && chmod +x "$USB/setup_on_box.sh"
  cp ~/Downloads/gb10-hackathon-handoff.md ~/Downloads/gb10-hackathon-integration.md "$USB/notes/"
  cp ~/Downloads/Travel_Ops_Agent_Channel_Assistant.docx "$USB/notes/" 2>/dev/null || true
  mkdir -p "$USB/src/app"
  ( cd "$USB" && ls -la images && du -sh images hf ckpt src notes ) > "$USB/notes/manifest.txt" 2>&1
  ( cd "$USB/images" && sha256sum *.tar > "$USB/notes/images.sha256" )
  # Readable on the box whatever its user id is (skip ext4's root-owned lost+found)
  find "$USB" -mindepth 1 -maxdepth 1 ! -name lost+found -exec chmod -R a+rX {} +
  chmod a+rx "$USB"
  log "notes done"; cat "$USB/notes/manifest.txt"
}

case "$STEP" in
  ckpt) ckpt ;; qwen) qwen ;; cosmos) cosmos ;; models) models ;;
  vllm) vllm ;; cell) cell ;; notes) notes ;;
  all) models; vllm; cell; notes ;;
  *) echo "unknown step: $STEP"; exit 1 ;;
esac
