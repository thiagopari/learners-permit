#!/usr/bin/env bash
# The evaluation sweep as a Nebius Serverless AI Job, driven from the laptop. A job bills only while it runs, and its
# VM is deleted when it ends, so there's nothing left idling.
#
#   cloud/job.sh build                 build the image (cloud/job/Dockerfile) and push it to Container Registry
#   cloud/job.sh run SKILL [KEY=VAL..] start a sweep; KEY=VAL are LP_* settings from cloud/job/sweep.py, e.g.
#                                      cloud/job.sh run red_dishes_in_bin LP_ARMS=n17_droid LP_TIER=supervised
#                                      LP_MODE=measure runs cloud/measure.py instead (SKILL is then ignored)
#   cloud/job.sh resume RUN_ID SKILL [KEY=VAL..]   rerun an interrupted run: it continues from its last batch
#   cloud/job.sh logs JOB_ID           follow a job's log
#   cloud/job.sh fetch RUN_ID          download a run's folder from the bucket to results/RUN_ID
#
# Needs: the nebius CLI with a profile, docker (build only), the aws CLI (fetch only), and in
# ~/.config/learners-permit.env:
#   NEBIUS_REGION        region of the registry and bucket (default uk-south2)
#   NEBIUS_REGISTRY      registry path from `nebius registry create` (the ID without "registry-")
#   LP_BUCKET            Object Storage bucket for results
#   LP_S3_PROFILE        how the job mounts the bucket: an AWS profile name, or PROFILE@SECRET for a MysteryBox secret
#   LP_HF_SECRET         MysteryBox secret holding the Hugging Face read token (passed to the job as HF_TOKEN)
# Options: LP_JOB_PLATFORM / LP_JOB_PRESET (default gpu-rtx6000-a / 1gpu-24vcpu-218gb; Isaac Sim needs RT cores, so
# the fallback is gpu-l40s-a / 1gpu-8vcpu-32gb in eu-north1), LP_SPOT=1, LP_JOB_HOURS (default 4),
# LP_USD_PER_HOUR (default 1.80, for the cost per 1,000 episodes).
set -euo pipefail
cd "$(dirname "$0")/.."
# shellcheck source=/dev/null
[ -f ~/.config/learners-permit.env ] && { set -a; . ~/.config/learners-permit.env; set +a; }
[ $# -gt 0 ] || { sed -n '2,24p' "$0"; exit 1; }
region=${NEBIUS_REGION:-uk-south2}
commit=$(git rev-parse --short HEAD)
image() { echo "cr.$region.nebius.cloud/${NEBIUS_REGISTRY:?set NEBIUS_REGISTRY}/learners-permit-eval:$commit"; }

submit() {  # submit RUN_ID SKILL [KEY=VAL..]
    local run_id=$1 skill=$2; shift 2
    : "${LP_BUCKET:?set LP_BUCKET}" "${LP_HF_SECRET:?set LP_HF_SECRET}"
    local hours=${LP_JOB_HOURS:-4}
    local envs=(--env "LP_RUN_ID=$run_id" --env "LP_SKILL=$skill" --env "LP_COMMIT=$commit"
                --env "LP_BUDGET_MIN=$(( hours * 60 - 15 ))" --env "LP_USD_PER_HOUR=${LP_USD_PER_HOUR:-1.80}")
    local kv
    for kv in "$@"; do
        [[ $kv == LP_*=* ]] || { echo "settings must look like LP_NAME=value, got: $kv"; exit 1; }
        envs+=(--env "$kv")
    done
    local pricing=(--on-demand)
    [ "${LP_SPOT:-0}" = 1 ] && pricing=(--preemptible --follows-spot-price)
    # on-failure: a preempted or crashed run restarts and resumes from the checkpoint in the bucket.
    nebius ai job create --name "lp-$run_id" --image "$(image)" "${envs[@]}" \
        --env-secret "HF_TOKEN=$LP_HF_SECRET" \
        --volume "s3://$LP_BUCKET:/results:rw:${LP_S3_PROFILE:-default}" \
        --platform "${LP_JOB_PLATFORM:-gpu-rtx6000-a}" --preset "${LP_JOB_PRESET:-1gpu-24vcpu-218gb}" \
        "${pricing[@]}" --timeout "${hours}h" --restart-policy on-failure --disk-size 250Gi --shm-size 32Gi \
        --format jsonpath='{.metadata.id}'
    echo
    echo "run $run_id: results in s3://$LP_BUCKET/$run_id. Follow with $0 logs <job ID>; fetch with $0 fetch $run_id"
}

case "${1:-}" in
build)
    [ -z "$(git status --porcelain)" ] || { echo "commit first: the image is tagged with HEAD ($commit)"; exit 1; }
    docker build -f cloud/job/Dockerfile --build-arg "LP_COMMIT=$commit" \
        ${GR00T_REF:+--build-arg "GR00T_REF=$GR00T_REF"} ${ROBOLAB_REF:+--build-arg "ROBOLAB_REF=$ROBOLAB_REF"} \
        -t "$(image)" .
    docker push "$(image)"
    ;;
run)
    [ $# -ge 2 ] || { echo "usage: $0 run SKILL [LP_KEY=value ...]"; exit 1; }
    skill=$2; shift 2
    submit "$(date -u +%Y%m%d-%H%M%S)-$skill" "$skill" "$@"
    ;;
resume)
    [ $# -ge 3 ] || { echo "usage: $0 resume RUN_ID SKILL [LP_KEY=value ...]"; exit 1; }
    run_id=$2 skill=$3; shift 3
    submit "$run_id" "$skill" "$@"
    ;;
logs) nebius ai job logs "${2:?usage: $0 logs JOB_ID}" --follow --timestamps ;;
fetch)
    run_id=${2:?usage: $0 fetch RUN_ID}
    aws s3 sync "s3://${LP_BUCKET:?set LP_BUCKET}/$run_id" "results/$run_id" \
        --endpoint-url "https://storage.$region.nebius.cloud"
    echo "results/$run_id/summary.json:"; cat "results/$run_id/summary.json" 2> /dev/null || echo "(none yet)"
    echo; echo "To use the licence in the console: python cloud/job/sweep.py import results/$run_id/licences.json"
    ;;
*) sed -n '2,24p' "$0"; exit 1 ;;
esac
