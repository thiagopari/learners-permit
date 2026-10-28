#!/usr/bin/env bash
# Build cloud/job/Dockerfile.vm on the GPU VM and push it to Nebius Container Registry.
#   bash ~/learners-permit/cloud/job/build_on_vm.sh IMAGE
# IMAGE is cr.<region>.nebius.cloud/<registry>/learners-permit-eval:<commit>. Docker must already be logged in to the
# registry (cloud/job.sh build-vm pipes a short-lived Nebius access token into `docker login`; nothing is stored here
# beyond Docker's own credential file).
set -euo pipefail
image=${1:?usage: build_on_vm.sh IMAGE}
cd ~
# The build context is the home directory: send only what the image copies.
cat > ~/.dockerignore <<'EOF'
*
!.local
!.cache/huggingface/hub/models--nvidia--GR00T-N1.7-DROID
!Isaac-GR00T
!RoboLab
!learners-permit
!lp-versions.txt
RoboLab/output
learners-permit/permit/data
**/__pycache__
**/.git
EOF
df -h / | tail -1
timeout -k 60 90m sudo docker build -f ~/learners-permit/cloud/job/Dockerfile.vm -t "$image" ~
sudo docker image ls "$image" --format '{{.Repository}}:{{.Tag}} {{.Size}}'
timeout -k 60 90m sudo docker push "$image"
echo "pushed $image"
