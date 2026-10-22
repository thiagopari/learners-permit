# The evaluation sweep as a Nebius Serverless AI Job: the GR00T N1.7 policy server, RoboLab on Isaac Sim 5.0 and this
# repo's control plane in one image. It installs the same stack as cloud/setup_vm.sh, which is the tested reference:
# get a sweep working on the VM first, then pin GR00T_REF and ROBOLAB_REF to the commits in ~/lp-versions.txt.
#
# Build and push with cloud/job.sh build (from the repo root, on a Linux machine with Docker; the image is large).
FROM ubuntu:24.04

ARG GR00T_REF=main
ARG ROBOLAB_REF=main
ARG LP_COMMIT=unknown

# NVIDIA_DRIVER_CAPABILITIES=all asks the container runtime for the graphics (Vulkan) driver too: Isaac Sim renders.
ENV DEBIAN_FRONTEND=noninteractive OMNI_KIT_ACCEPT_EULA=Y ACCEPT_EULA=Y PRIVACY_CONSENT=Y \
    NVIDIA_VISIBLE_DEVICES=all NVIDIA_DRIVER_CAPABILITIES=all \
    PATH=/root/.local/bin:$PATH UV_LINK_MODE=copy LP_COMMIT=$LP_COMMIT

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl git git-lfs ffmpeg jq python3 python3-venv vulkan-tools libvulkan1 \
        libglu1-mesa libegl1 libgl1 libxt6 libxrender1 libxi6 libsm6 libxrandr2 libxkbcommon0 \
    && rm -rf /var/lib/apt/lists/* \
    && git lfs install \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /opt

# GR00T N1.7 (Python 3.12). Weights are not baked in: the job downloads them with its own HF token at start.
RUN git clone --recurse-submodules https://github.com/NVIDIA/Isaac-GR00T \
    && cd Isaac-GR00T && git checkout "$GR00T_REF" && git submodule update --init --recursive \
    && uv sync --python 3.12 \
    && uv run python -c "import torch; a = torch.cuda.get_arch_list(); print(torch.__version__, a); \
assert 'sm_120' in a, 'this torch has no Blackwell kernels: docs/RUNBOOK.md section 1.4'"

# RoboLab on Isaac Sim 5.0 (Python 3.11), with its git-lfs scene assets.
RUN git clone https://github.com/NVlabs/RoboLab \
    && cd RoboLab && git checkout "$ROBOLAB_REF" && git lfs pull \
    && uv venv --python 3.11 && uv sync --extra isaac50

COPY . /opt/learners-permit
RUN cd /opt/learners-permit && python3 -m venv .venv && .venv/bin/pip install --no-cache-dir -r requirements.txt \
    && { echo "Isaac-GR00T $(git -C /opt/Isaac-GR00T rev-parse --short HEAD)"; \
         echo "RoboLab $(git -C /opt/RoboLab rev-parse --short HEAD), isaac50"; \
         echo "learners-permit $LP_COMMIT"; } > /opt/versions.txt

ENTRYPOINT ["bash", "/opt/learners-permit/cloud/job/entrypoint.sh"]
