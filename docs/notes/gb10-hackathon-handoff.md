# GB10 Hackathon Handoff: Physical AI Cell Supervisor

Prepared Friday, October 2, 2026 for the Dell × NVIDIA hackathon in Boston on Saturday, October 3 (09:00–21:00). This file is meant to be opened on Thiago's Linux laptop and worked through tonight by whoever does the prep: Thiago, a teammate, or a coding agent. It is self-contained. Sections run in the order you should do them, commands are copy-pasteable apart from placeholders in angle brackets, and anything marked "Verify" has not been confirmed and should be checked before you rely on it.

## The short version

We are building an always-on "cell supervisor" agent for a robotic packing station. It lives in Slack (Telegram as backup), runs on NemoClaw/OpenClaw inside an OpenShell sandbox with a local LLM, and its main tool is a GR00T N1.7 robot policy running in simulation. It turns plain-language work orders into robot skills, dispatches them, checks the results, runs randomized validation sweeps on its own, and refuses to dispatch any skill whose validated success rate is below a threshold, escalating to a human with failure clips instead. Nobody collects teleop data or post-trains anything tomorrow; we use NVIDIA's published fine-tuned checkpoints.

Tonight's job is to make tomorrow's installation a non-event, because venue Wi-Fi will be slow and the box is ARM (aarch64). In priority order: request Hugging Face access to nvidia/Cosmos-Reason2-2B and set up an NGC login, stage every model on the external SSD, pull NemoClaw's vLLM image for arm64, build the GR00T Spark image and the "cell" image (GR00T plus the LIBERO simulator plus our tool service) for arm64, then package everything with a checksum and a manifest. Isaac Sim is a stretch goal with a strict time box, not part of the core plan.

## 1. Event constraints

The event runs Saturday, October 3, 2026 in Boston, with the venue sent by email. Doors open at 09:00, the brief is at 09:30, building runs 10:30–18:00, and the working demo must be submitted through the BuilderBase portal before the 18:00 code freeze. The top eight teams pitch live and winners are announced before 21:00. Teams have one to four people.

The requirements that shape every decision below: the agent runs 100% locally on the Dell Pro Max with GB10 with no cloud LLM calls in the runtime path, uses the NemoClaw + OpenClaw + OpenShell stack, is wired into a real channel (Slack, Discord, or Telegram) through the OpenClaw connector, reasons and uses tools without a human driving every step, and targets a real business workflow. The demo must run on the box. The organizers say to bring models, weights, containers, and datasets on a drive because the Wi-Fi will not keep up, plus a development laptop and a power strip.

The GB10 is a Grace Blackwell system: an aarch64 CPU and an NVIDIA GPU sharing 128 GB of unified memory. NVIDIA documents NemoClaw installs for DGX Spark and OEM GB10 systems like this one. We assume DGX OS but do not know the exact OS or driver version yet (Verify, see section 9).

## 2. What we are building

### The workflow

A packing cell has a robot arm and a team that sends it work in chat. Our agent is the cell's supervisor. When someone posts an order, it maps each item to one of the cell's skills, checks how reliable that skill currently is, dispatches the reliable ones one at a time, verifies each outcome, and replies with a clip and a status. When a skill is unreliable or has never been validated, it does not send it to the robot; it says why, shows the evidence, and tags a human. On its own schedule it runs randomized validation sweeps and keeps a live reliability table, which is what makes it an always-on agent rather than a chatbot.

### The demo, in three beats

First, someone posts an order such as "pack order 1042: alphabet soup and tomato sauce into the basket." The agent plans, dispatches, and posts the clip and the result. Second, someone asks how reliable a skill is, or the scheduled sweep fires; the agent runs randomized trials in parallel and posts a success rate with failure clips. Third, an order includes a skill that fails validation; the agent refuses to dispatch it and escalates with the clips. Close the pitch with the roadmap: every logged failure becomes post-training data, and the same box can run that loop.

For the gate in beat three, plan on one deliberately out-of-distribution skill: a LIBERO task from a suite the loaded checkpoint was not fine-tuned on, for example "open the middle drawer of the cabinet" while running the libero_10 checkpoint. It should validate poorly, which is exactly what the gate is for. Verify its actual score during the day's sweeps; if it scores well, pick another.

### Architecture

```
  Slack / Telegram
        |
+-------v----------------------------- GB10 box -------------------------------+
|                                                                              |
|  OpenShell sandbox: OpenClaw agent (installed by NemoClaw)                   |
|      | LLM calls  -------------------->  nemoclaw-vllm container :8000       |
|      | HTTP tool calls (allow-listed in the OpenShell network policy)        |
|      v                                                                       |
|  "cell" container (host networking)                                          |
|      tool service :8090  -->  LIBERO rollouts (MuJoCo, EGL rendering)        |
|                                  | observations and actions over ZMQ         |
|                                  v                                           |
|                          GR00T N1.7 policy server :5555                      |
|                                                                              |
+------------------------------------------------------------------------------+
```

The cell image holds three separate Python environments, mirroring how the GR00T repo keeps its policy server and each simulator client in separate environments: GR00T's policy-server environment, the LIBERO client environment that GR00T's setup script creates, and a small environment for our tool service. NemoClaw, OpenShell, and vLLM stay outside our images, because NemoClaw manages its own containers and sandbox.

### Out of scope tomorrow

Teleop collection and post-training do not fit the day: NVIDIA's own LIBERO fine-tunes ran on 8 GPUs for 20K steps at batch size 640, and XR teleoperation is not validated on DGX Spark. Sim-to-real does not apply because there is no physical robot. TensorRT acceleration for GR00T is skipped too, because engines are built on the target GPU and PyTorch mode is fast enough for simulation (roughly 8 Hz on Spark in eager mode, versus about 10 Hz with TensorRT). All of these belong on the roadmap slide.

## 3. Decision log

| Decision | Why | Revisit if |
|---|---|---|
| NemoClaw + OpenClaw + OpenShell, with the LLM served by NemoClaw's managed vLLM | Required stack; on DGX Spark the managed vLLM uses a known image and default model that we can pre-stage | Organizers preinstall the stack with a different model |
| Slack first, Telegram as backup | Slack fits a corporate-team story; Telegram is the fastest channel to wire | Slack setup is still fighting us at 12:00 |
| GR00T N1.7 with NVIDIA's fine-tuned checkpoints, no training | Post-training doesn't fit the day; GR00T inference is supported on DGX Spark | Not for tomorrow |
| LIBERO (MuJoCo) is the primary simulator | NVIDIA's LIBERO fine-tune scores 94–98%; it is lightweight and less sensitive to the driver than Isaac Sim's RTX renderer | The LIBERO environment won't install on arm64 tonight |
| Isaac Sim is a stretch goal only | RoboLab pins Isaac Sim 5.0, Isaac Lab 2.2 and Python 3.11, which we could not confirm on ARM; Isaac Sim on Spark is also picky about the driver | A stretch image builds tonight and renders a GR00T rollout by 12:30 |
| Prebuilt arm64 images on an ext4 SSD | Takes Wi-Fi off the critical path; ext4 keeps symlinks and large files intact | A Mac has to write to the drive (then use exFAT and store everything as tarballs) |
| The reliability gate lives in the tool service | A safety rule shouldn't depend on the LLM following its prompt | — |
| vLLM's memory is capped | The LLM, GR00T, and the simulator all share the same 128 GB | — |

## 4. Tonight on the Linux laptop

### 4.1 Preflight

The laptop's architecture decides how the arm64 images get built. On x86_64, Docker builds them under QEMU emulation, which is fine for downloads and installing prebuilt wheels and very slow for anything that compiles. On aarch64 the builds are native.

```bash
uname -m                        # x86_64 = emulated arm64 builds, aarch64 = native
docker version && docker buildx version
df -h /var/lib/docker ~         # rough budget: 150-200 GB free for images and build cache
nvidia-smi || true              # optional; only matters for section 4.12
```

On x86_64, register QEMU and confirm that emulation works:

```bash
docker run --privileged --rm tonistiigi/binfmt --install arm64
docker run --rm --platform linux/arm64 alpine uname -m     # expect: aarch64
```

If the GR00T build in 4.7 is still crawling after roughly 90 minutes, stop and rent a cheap ARM cloud VM (an AWS Graviton instance, for example), build there natively, and copy the `docker save` output back to the SSD.

### 4.2 Accounts, tokens, and one email

Request access to nvidia/Cosmos-Reason2-2B on Hugging Face first, because approval may not be instant and nothing in GR00T runs without it: it is the vision-language backbone that every GR00T N1.7 checkpoint loads. Then install the Hugging Face CLI in its own venv and log in.

```bash
python3 -m venv ~/.venvs/hf && source ~/.venvs/hf/bin/activate
pip install -U "huggingface_hub[cli]"
hf auth login                   # older CLI versions: huggingface-cli login
```

Create an NGC account and API key at ngc.nvidia.com and log Docker in, since NemoClaw's vLLM image comes from nvcr.io and pulls from there require a login.

```bash
docker login nvcr.io            # username: $oauthtoken   password: <NGC API key>
```

Create the chat credentials tonight too. For Telegram, message @BotFather, run `/newbot`, and keep the token; NemoClaw can take it during onboarding or later with `nemoclaw <sandbox> channels add telegram`. For Slack, create the app by following OpenClaw's Slack channel documentation and collect the tokens it asks for (Verify the scopes there). Keep all tokens in a password manager, not in this file or a repo.

Finally, email hello@builderbase.com tonight and ask three things: whether NemoClaw and OpenShell come preinstalled on the boxes, which DGX OS and NVIDIA driver versions the boxes run, and whether teams may copy files and load containers before 10:30. The answers decide how much of section 7.1 you can do early.

### 4.3 Prepare the SSD

Use a USB 3.x SSD of 500 GB or more rather than a thumb drive. Since both the laptop and the box run Linux, format it ext4: it keeps symlinks, which Hugging Face caches depend on, and has no file-size limit. Use exFAT only if a Mac has to write to the drive, and in that case store everything as tarballs, because exFAT cannot hold symlinks.

```bash
lsblk                                       # find the SSD's partition, e.g. /dev/sdb1
sudo mkfs.ext4 -L HACK /dev/<partition>     # erases that partition
sudo mkdir -p /mnt/hack && sudo mount /dev/<partition> /mnt/hack
sudo chown -R "$USER": /mnt/hack
mkdir -p /mnt/hack/{hf,ckpt,src,images,notes}
```

`hf/` is a Hugging Face cache that becomes `~/.cache/huggingface` on the box, `ckpt/` holds checkpoints that use nested folders, `src/` holds the repos and our own code, `images/` holds the `docker save` archive, and `notes/` holds this handoff and the manifest.

### 4.4 Stage model weights

Start this before the builds and let it run in the background. The LLM alone is roughly 20 GB or more, and each GR00T checkpoint adds several more.

```bash
source ~/.venvs/hf/bin/activate
export HF_HOME=/mnt/hack/hf

hf download nvidia/Cosmos-Reason2-2B            # gated; GR00T's VLM backbone
hf download nvidia/Qwen3.6-35B-A3B-NVFP4        # NemoClaw's default LLM on DGX Spark

# The LIBERO checkpoint keeps one subfolder per suite; list them first (Verify which exist)
python - <<'EOF'
from huggingface_hub import list_repo_files
print(sorted({f.split("/")[0] for f in list_repo_files("nvidia/GR00T-N1.7-LIBERO")}))
EOF
hf download nvidia/GR00T-N1.7-LIBERO --include "libero_10/*" \
  --local-dir /mnt/hack/ckpt/GR00T-N1.7-LIBERO
# repeat with --include "<suite>/*" for any other suite folder the listing shows

# Isaac Sim stretch only (section 4.9)
hf download nvidia/GR00T-N1.7-DROID             # RoboLab path
hf download nvidia/SO_ARM_Starter_Gr00tN17      # Isaac for Healthcare SO-ARM path
```

If any download returns 401 or 403, request access on that model's page and retry.

### 4.5 Clone repositories

```bash
sudo apt install -y git-lfs && git lfs install
cd /mnt/hack/src
git clone --recurse-submodules https://github.com/NVIDIA/Isaac-GR00T
git clone https://github.com/NVIDIA/NemoClaw
git clone https://github.com/NVlabs/RoboLab                       # stretch
git clone https://github.com/isaac-for-healthcare/i4h-workflows   # stretch
mkdir -p /mnt/hack/src/app                                         # our tool service code
```

Use the NemoClaw clone to answer two questions tonight. First, which container images do its installer and sandbox pull? Pull any of those for arm64 as well. Second, what arguments does it pass to vLLM on DGX Spark, especially the memory setting and the tool-call parser? You will need those if you cap vLLM's memory tomorrow.

```bash
cd /mnt/hack/src/NemoClaw
grep -rnE "nvcr\.io|ghcr\.io|docker (pull|run)" . | head -50
grep -rnE "gpu-memory-utilization|tool-call-parser|max-model-len" . | head -50
```

Builds read many small files, so it is fine to build from a copy of these repos on the laptop's internal disk and sync the results back to the SSD afterwards.

### 4.6 Pull NemoClaw's vLLM image

NemoClaw's managed vLLM on DGX Spark uses this exact image, downloads weights into `~/.cache/huggingface`, and reuses both on later runs. Staging both means onboarding tomorrow should not need to download anything for inference.

```bash
docker pull --platform linux/arm64 nvcr.io/nvidia/vllm:26.05.post1-py3
```

### 4.7 Build the GR00T Spark image

GR00T ships an official Spark profile for its Docker build. Read `docker/build.sh` and `docker/README.md` first. You want to know how the script calls Docker and how the repo checkout is meant to be used inside the image; the main README recommends starting the image and working on a checkout that uses the image's prebuilt environment.

```bash
cd /mnt/hack/src/Isaac-GR00T
less docker/build.sh docker/README.md
export DOCKER_DEFAULT_PLATFORM=linux/arm64      # plain `docker build` now targets arm64
bash docker/build.sh --profile=spark
docker images | head                            # note the tag it produced
docker image inspect --format '{{.Architecture}}' <gr00t-spark-tag>    # must print arm64
```

If the script uses `docker buildx` with a non-default builder, add `--load` so the image lands in the local store. If a build step insists on seeing a GPU (by calling `nvidia-smi`, for example), move that step into a script you run on the box tomorrow. GR00T's Spark install uses a prebuilt aarch64 wheel for its video decoder (torchcodec) and compiles only if that wheel is missing, so this build should be mostly downloads.

### 4.8 Build the cell image (GR00T + LIBERO + tool service)

Write a short Dockerfile, `Dockerfile.cell`, based on the GR00T Spark image, and tag the result `hack/cell`. It needs to do the following.

Copy the Isaac-GR00T checkout into the image at `/opt/Isaac-GR00T` and make that the working directory. GR00T's LIBERO setup creates its virtual environment inside the repo tree, so bind-mounting a checkout over that path tomorrow would hide it. If GR00T's environment needs the package installed from the checkout, do that here too (docker/README.md will say).

Make GR00T's environment, including whatever `scripts/activate_spark.sh` exports, the default in the image, so that plain `python` works in the commands below. Do not set an ENTRYPOINT, and reset any inherited one with `ENTRYPOINT []`.

Install `libegl1-mesa-dev` and `libglu1-mesa`, which GR00T lists as the shared system libraries for its simulation benchmarks, then run `bash gr00t/eval/sim/LIBERO/setup_libero.sh` from the repo root. Create a separate small venv at `/opt/toolsvc` for the tool service (FastAPI and uvicorn are enough), so you don't disturb GR00T's pinned environment.

Set these environment variables:

| Variable | Value | Why |
|---|---|---|
| `NVIDIA_DRIVER_CAPABILITIES` | `all` | CUDA-based images usually expose only compute libraries, and EGL rendering then fails |
| `MUJOCO_GL` | `egl` | Headless MuJoCo rendering; GR00T's wrapper may already set it |
| `PYOPENGL_PLATFORM` | `egl` | Same reason as `MUJOCO_GL` |
| `HF_HOME` | `/hf` | Models load from the mounted cache |
| `HF_HUB_OFFLINE` | `1` | Hugging Face never touches the network |

```bash
docker build --platform linux/arm64 -f /path/to/Dockerfile.cell -t hack/cell /mnt/hack/src/Isaac-GR00T
```

Two GR00T rules apply inside this image because it is aarch64. First, run GR00T commands with plain `python` from its environment, not `uv run`, since `uv run` re-syncs against the x86 project file and breaks the platform environment. Second, on CUDA 13 platforms the README says to run `scripts/patch_triton_cuda13.sh`, or Triton fails at startup; check whether the Spark image already applies it (Verify).

### 4.9 Isaac Sim stretch (time-boxed)

Spend at most about 90 minutes on this tonight, and only after 4.6–4.8 are done. There are two candidates, and the first is more promising.

The Isaac for Healthcare SO-ARM Starter is maintained by NVIDIA. Its release notes say it added DGX Spark Isaac Sim container support and an upgrade to GR00T N1.7, and it ships a checkpoint (`nvidia/SO_ARM_Starter_Gr00tN17`) for scissor pick-and-place. Using it would reframe the cell as hospital instrument handling, which is still a strong business workflow. Read its README and DGX Dockerfile, try building that image for arm64, and run its asset download step tonight; its `i4h` CLI handles Docker builds and asset downloads (Verify the exact commands in the repo).

RoboLab has the best bin and crate tasks and writes detailed per-episode results, and NVIDIA ran `nvidia/GR00T-N1.7-DROID` on it zero-shot. But it pins Isaac Sim 5.0, Isaac Lab 2.2, and Python 3.11. Test whether that resolves on arm64:

```bash
docker run --rm -it --platform linux/arm64 -v /mnt/hack/src/RoboLab:/w -w /w ubuntu:22.04 bash -lc '
  apt-get update && apt-get install -y curl ca-certificates git ffmpeg &&
  curl -LsSf https://astral.sh/uv/install.sh | sh && . $HOME/.local/bin/env &&
  uv venv --python 3.11 && uv sync'
```

If uv reports that it can't find aarch64 wheels for Isaac Sim, RoboLab is out for tomorrow, because porting it to a newer Isaac Sim is not a hackathon-day job. If it starts downloading Isaac Sim wheels instead, RoboLab may be viable; let it finish only if time allows.

Whichever candidate you pursue, three things will matter tomorrow:

| Issue | What to do |
|---|---|
| Isaac Sim on Spark is sensitive to the host driver | One NVIDIA forum thread has Isaac Sim 6.0.1 crashing at RTX startup on a Spark, with an answer that 6.0.1 needs driver 580.159.03 there. Write down the validated driver for your version from the Isaac Sim requirements page. |
| Isaac Sim expects internet access for assets and some extensions | Anything a stretch scene fetches at runtime has to be on the SSD. |
| The first launch builds shader caches on the real GPU and is slow | Mount persistent cache volumes (NVIDIA's container docs show which folders) and launch once early in the day, not during the demo. |

### 4.10 Checks that work without a GPU

Emulation lets you check architecture, file layout, and pure-Python imports. It cannot test CUDA, EGL rendering, Isaac Sim startup, or TensorRT; those have to wait for the box.

```bash
docker image inspect --format '{{.Architecture}}' hack/cell nvcr.io/nvidia/vllm:26.05.post1-py3
docker run --rm --platform linux/arm64 hack/cell \
  gr00t/eval/sim/LIBERO/libero_uv/.venv/bin/python -c 'import mujoco; print("mujoco", mujoco.__version__)'
docker run --rm --platform linux/arm64 hack/cell python -c 'import gr00t; print("gr00t imports")'
docker run --rm --platform linux/arm64 hack/cell /opt/toolsvc/bin/python -c 'import fastapi; print("toolsvc ok")'
```

A failure mentioning libcuda or the CUDA driver is expected without a GPU. Anything else, such as a missing module or the wrong Python version, is a real problem to fix tonight.

### 4.11 Package and verify

Save all images in a single `docker save` so that shared layers are stored once, then record a checksum and a manifest.

```bash
docker save -o /mnt/hack/images/images.tar \
  nvcr.io/nvidia/vllm:26.05.post1-py3 <gr00t-spark-tag> hack/cell <any stretch or NemoClaw images>
cd /mnt/hack
sha256sum images/images.tar > notes/images.sha256
docker images --digests > notes/manifest.txt
du -sh hf ckpt src images >> notes/manifest.txt
cp <path-to-this-handoff>.md notes/
sync && sudo umount /mnt/hack
```

### 4.12 Optional: write the tool service tonight

Build the tool service in mock mode first (section 5) so it can be finished without a GPU. Keep its code in `/mnt/hack/src/app`, and make sure it runs with `/opt/toolsvc/bin/python`. If the laptop happens to have an NVIDIA GPU with at least 16 GB of VRAM, which is GR00T's stated minimum for inference, you can also do GR00T's standard x86 install with the LIBERO setup and test the service against a real policy tonight. Otherwise mock mode is the plan, and you swap in real rollouts tomorrow.

## 5. Tool service spec

The tool service is a small HTTP service that runs inside the cell container on host networking, port 8090. It owns everything robot-related, so the agent only sees a narrow API.

| Endpoint | Does | Returns |
|---|---|---|
| `GET /health` | Checks the GR00T server and the simulator | Status of each |
| `GET /skills` | Lists the cell's skills, each mapped to a sim task | Name, task id, validated rate, trials, last validated |
| `POST /run` `{skill, seed}` | Runs one episode with video, if the gate allows it | Success, duration, video path, or a refusal with the reason |
| `POST /validate` `{skill, n}` | Starts n randomized episodes as a background job | Job id |
| `GET /jobs/{id}` | Reports job progress | Progress, successes, rate, failure video paths |
| `GET /reliability` | Returns the reliability table | Per-skill rate, trials, last validated |

`/run` must refuse a skill that has never been validated or whose rate is below the threshold (start at 0.8), so the gate holds even if the LLM ignores its instructions. Validation must be asynchronous, because sweeps take minutes and agent tool calls time out. A `MOCK=1` setting returns canned results with realistic delays, so the agent can be built before the simulator works. Persist the reliability table to a JSON file so restarts don't wipe it, and keep the last few videos per skill for reports.

To run episodes, shell out to `rollout_policy.py` with the LIBERO venv's Python (the full command is in section 7.2) and parse its output. Read `gr00t/eval/rollout_policy.py` tonight for the flags that save videos and per-episode results (Verify).

Example skill mapping, using task names from GR00T's LIBERO list:

| Skill | LIBERO task | Purpose |
|---|---|---|
| `soup_and_sauce_to_basket` | `libero_sim/LIVING_ROOM_SCENE2_put_both_the_alphabet_soup_and_the_tomato_sauce_in_the_basket` | Normal order |
| `cheese_and_butter_to_basket` | `libero_sim/LIVING_ROOM_SCENE2_put_both_the_cream_cheese_box_and_the_butter_in_the_basket` | Normal order |
| `open_middle_drawer` | `libero_sim/open_the_middle_drawer_of_the_cabinet` | Out-of-distribution gate demo |

## 6. Agent spec

The agent is the supervisor for one packing cell. On a work order, it maps each item to a skill from `GET /skills` and nothing else, checks each skill's validated rate, dispatches passing skills one at a time with `/run`, and reports each result with its clip. For a refused skill, it explains that it will not send that skill to the robot, shows the validation evidence, and tags a human. It never reports a result the tool didn't return, and it says so plainly when a tool errors. On a schedule, or when asked, it runs `/validate` for each skill and posts a short reliability report; at the end of the demo it posts a shift summary.

For wiring, expose the API to OpenClaw in the simplest way its documentation supports, whether that is a skill that calls the HTTP endpoints or an MCP server (Verify at docs.openclaw.ai). For scheduling, use OpenClaw's own scheduler if it has one, or a host cron job that posts a trigger message (Verify). Check how OpenClaw sends images or video on the chosen channel; if clips are awkward, post a still frame or a GIF instead.

OpenShell locks the sandbox's filesystem policy when the sandbox is created and lets you change the network policy at runtime, so decide before onboarding which host folders the agent may read (a reports folder, say). `localhost` inside the sandbox may not be the box's localhost. Look at how NemoClaw routes the agent's inference to vLLM and reach the tool service the same way, then allow-list exactly that address on port 8090, plus the chat channel's network preset.

## 7. Tomorrow on the GB10

### 7.1 Before 10:30, if allowed (no Wi-Fi needed)

Copy everything to the box's internal NVMe first. It is much faster than USB and frees the drive.

```bash
lsblk && sudo mkdir -p /mnt/hack && sudo mount /dev/<partition> /mnt/hack
mkdir -p ~/hack ~/.cache/huggingface
rsync -a --info=progress2 /mnt/hack/{images,ckpt,src,notes} ~/hack/
rsync -a --info=progress2 /mnt/hack/hf/ ~/.cache/huggingface/
cd ~/hack && sha256sum -c notes/images.sha256
docker load -i ~/hack/images/images.tar
```

### 7.2 First 30 minutes of build time

Check the driver and GPU access first, then bring up the policy and run a two-episode smoke rollout.

```bash
nvidia-smi                                            # note the driver version
docker run --rm --gpus all hack/cell nvidia-smi       # the GPU must be visible inside containers

docker run -d --name cell --gpus all --network host --ipc host \
  -e NVIDIA_DRIVER_CAPABILITIES=all \
  -v ~/.cache/huggingface:/hf -v ~/hack/ckpt:/ckpt -v ~/hack/src/app:/app \
  hack/cell sleep infinity

docker exec -d cell bash -lc 'cd /opt/Isaac-GR00T && python gr00t/eval/run_gr00t_server.py \
  --model-path /ckpt/GR00T-N1.7-LIBERO/libero_10 --embodiment-tag LIBERO_PANDA \
  --use-sim-policy-wrapper --host 127.0.0.1 --port 5555 > /tmp/gr00t.log 2>&1'
docker exec cell tail -f /tmp/gr00t.log               # wait for "Server is ready and listening"

docker exec -it cell bash -lc 'cd /opt/Isaac-GR00T && \
  gr00t/eval/sim/LIBERO/libero_uv/.venv/bin/python gr00t/eval/rollout_policy.py \
  --n-episodes 2 --n-envs 1 --policy-client-host 127.0.0.1 --policy-client-port 5555 \
  --max-episode-steps 720 --n-action-steps 8 \
  --env-name libero_sim/LIVING_ROOM_SCENE2_put_both_the_alphabet_soup_and_the_tomato_sauce_in_the_basket'
```

Time this two-episode run, because it tells you how big the live validation sweep in the demo can be.

Then set up NemoClaw. If it is not preinstalled, follow the instructions at build.nvidia.com/spark/nemoclaw; its installer needs the network, so do this early. Export `HF_TOKEN` before onboarding so NemoClaw can pass it to the vLLM container, then run `nemoclaw onboard` and choose the managed vLLM. With the image loaded and the weights in `~/.cache/huggingface`, it should reuse both. (Verify that NemoClaw treats the Dell GB10 as a DGX Spark; if it picks a different profile, the image or model may differ.) Afterwards, check what memory vLLM claimed:

```bash
docker inspect nemoclaw-vllm --format '{{json .Config.Cmd}}'
nvidia-smi
```

If vLLM reserved so much of the 128 GB that GR00T or the simulator can't fit, run vLLM yourself from the same image with the same arguments (from tonight's grep) plus a lower `--gpu-memory-utilization` (try about 0.45). Then point NemoClaw at that existing server, which its documentation supports; on DGX Spark, an existing server is yours to manage. Last, add the chat channel (for Telegram, `nemoclaw <sandbox> channels add telegram`) and start the tool service in the cell container.

### 7.3 Smoke tests and go/no-go

| Check | Pass | If it fails |
|---|---|---|
| `nvidia-smi` on the host | GB10 listed, driver noted | Ask a mentor; don't attempt a driver update on venue Wi-Fi |
| GPU inside a container | Same output inside `hack/cell` | Check the NVIDIA Container Toolkit and `--gpus all` |
| GR00T server | Log says "Server is ready and listening" | Cosmos access and HF cache, `HF_HUB_OFFLINE`, Triton CUDA 13 patch |
| LIBERO smoke rollout | Two episodes finish and report success | `NVIDIA_DRIVER_CAPABILITIES`, `MUJOCO_GL=egl`, EGL libraries |
| NemoClaw | Web UI answers from local vLLM | vLLM container logs |
| Chat channel | The bot replies | Token, network preset |
| Tool service | `/health` and `/run` return JSON, then the agent calls them | Sandbox route and allow-list |
| Isaac Sim stretch | A GR00T rollout renders by 12:30 | Drop it; no extensions |

### 7.4 Roles and schedule

There are four roles; with fewer people, merge C into A and D into B.

| Role | Owns |
|---|---|
| A | NemoClaw, the channel, and the agent's prompt and behaviors, wired to the tool service in mock mode first |
| B | The GR00T server, the LIBERO client, and the validation sweeps |
| C | The tool service and the report formats |
| D | The Isaac Sim stretch until 12:30, then the demo script, the pitch, and the backup recording |

| Time | Milestone |
|---|---|
| 09:00–10:30 | Arrive and attend the brief; if allowed, copy and load from the SSD (7.1) |
| 10:30–11:00 | Driver and GPU checks, GR00T server up, LIBERO smoke rollout, NemoClaw onboarding |
| 11:00–12:30 | Agent talking to the mock tool service end to end in the channel; real tool service on LIBERO; Isaac Sim stretch attempt |
| 12:30 | Go/no-go: the stretch continues only if a GR00T rollout rendered in Isaac Sim |
| 12:30–15:00 | Mock swapped for real rollouts; validation jobs, the gate, and reports with clips |
| 15:00–16:30 | Demo flow polished; full sweeps run so the reliability table is populated before judging |
| 16:30–17:15 | Two full dress rehearsals; record a backup video |
| 17:15–17:45 | Freeze, write the submission, submit |
| 18:00 | Code freeze |

### 7.5 Submission, pitch, and cleanup

Submit through the BuilderBase portal before 18:00, aiming for 17:45. Include a short README covering what the agent does, how it runs entirely on the box, and the stack used, plus the repo link and the backup video.

The pitch should cover four things:

| Part | What to say |
|---|---|
| Problem | Robot cells need supervision, and policies fail quietly |
| Demo | The three beats from section 2 |
| Why local | Factory video and data never leave the site, and everything runs on one box under a desk |
| Roadmap | Logged failures become post-training data |

Before leaving, run `docker logout nvcr.io` and `hf auth logout` on the box, and rotate the bot tokens and the NGC key. The boxes are loaners; prizes ship separately after the event.

## 8. Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Driver not validated for your Isaac Sim version | Isaac Sim crashes at RTX startup | Match the driver to the requirements page, or skip Isaac Sim |
| vLLM claims most of the memory | GR00T or the simulator runs out of memory | Cap `--gpu-memory-utilization` and point NemoClaw at that server |
| Rendering libraries missing in the container | EGL or Vulkan errors | `NVIDIA_DRIVER_CAPABILITIES=all` |
| `uv run` on aarch64 | GR00T's environment re-syncs and breaks | Plain `python` in GR00T's environment |
| Triton on CUDA 13 | RuntimeError in `ptx_get_version` | `scripts/patch_triton_cuda13.sh` |
| Bind mount over `/opt/Isaac-GR00T` | LIBERO venv missing | Mount only our own code |
| Hugging Face reaching for the network | Timeouts or 401 errors | `HF_HUB_OFFLINE=1`, `HF_HOME` on the cache, Cosmos access granted |
| Port 5555 busy | `ZMQError: Address already in use` | Use another `--port` on both server and client |
| Sandbox can't reach the tool service | Connection refused or blocked | Use the route NemoClaw uses for vLLM and allow-list it |
| Isaac Sim assets fetched online | Scenes hang while loading | Pre-download assets (stretch only) |
| First Isaac Sim launch | Several minutes of shader compilation | Persistent cache volumes; launch once early |
| Emulated builds too slow | A build crawls for hours | Build natively on a cloud ARM VM |

## 9. Open questions

| Question | How to resolve | Why it matters |
|---|---|---|
| Are NemoClaw and OpenShell preinstalled? | Email the organizers tonight | Whether the installer needs venue Wi-Fi |
| Which DGX OS and driver do the boxes run? | Email; `nvidia-smi` on arrival | Whether the Isaac Sim stretch is viable |
| May we load containers before 10:30? | Email, or ask at the door | Saves the first half hour |
| Which LIBERO suite folders exist? | The listing in 4.4 | Which skills the cell offers |
| Does the GR00T Spark build need a GPU? | Tonight's build | What moves to tomorrow |
| Do the SO-ARM Starter or RoboLab images build for arm64? | Section 4.9 | Whether the stretch exists at all |
| How does OpenClaw add tools, schedule tasks, and send media? | docs.openclaw.ai | Agent wiring |
| Slack or Telegram? | Team decision tonight | Setup time |
| Is the team aligned on this plan and the roles? | Quick team chat tonight | Avoids a debate at 10:30 |

## 10. Numbers for the pitch

| Item | Number | Source |
|---|---|---|
| GR00T N1.7 LIBERO fine-tune success | 94.35% on LIBERO-10, up to 98.45% on LIBERO-Object | GR00T LIBERO README |
| GR00T N1.7 DROID on RoboLab, zero-shot | 8.58% across 120 tasks; 38/40 on bananas into a bin; 15/40 on red dishes into a bin | GR00T RoboLab README |
| NVIDIA's LIBERO post-training run | 8 GPUs, 20K steps, batch size 640 | GR00T LIBERO README |
| GR00T inference on DGX Spark | About 8 Hz in PyTorch eager mode, about 10 Hz with TensorRT | GR00T N1.7 model card and repo docs |

The RoboLab row is the argument for the gate: the same policy that is near-perfect on some tasks succeeds on fewer than half the attempts at others, and nobody can tell which without validation.

## 11. Sources

| Topic | Link |
|---|---|
| Event page | https://builderbase.com/event/dell-x-nvidia-ai-hackathon-boston |
| NemoClaw on DGX Spark (playbook) | https://build.nvidia.com/spark/nemoclaw |
| NemoClaw managed vLLM (image and default model) | https://docs.nvidia.com/nemoclaw/user-guide/openclaw/inference/local-inference/set-up-vllm |
| NemoClaw repo | https://github.com/NVIDIA/NemoClaw |
| OpenClaw docs | https://docs.openclaw.ai |
| GR00T N1.7 repo | https://github.com/NVIDIA/Isaac-GR00T |
| GR00T LIBERO example | https://github.com/NVIDIA/Isaac-GR00T/blob/main/examples/LIBERO/README.md |
| GR00T on RoboLab | https://github.com/NVIDIA/Isaac-GR00T/blob/main/examples/RoboLab/README.md |
| RoboLab | https://github.com/NVlabs/RoboLab |
| Isaac for Healthcare workflows (SO-ARM Starter) | https://github.com/isaac-for-healthcare/i4h-workflows |
| Isaac Sim requirements | https://docs.isaacsim.omniverse.nvidia.com/latest/installation/requirements.html |
| Isaac Sim container on NGC | https://catalog.ngc.nvidia.com/orgs/nvidia/-/containers/isaac-sim/6.1.0 |
| Isaac Lab installation notes for DGX Spark | https://isaac-sim.github.io/IsaacLab/release/3.0.0/source/setup/installation/index.html |
| Isaac Sim driver thread for DGX Spark | https://forums.developer.nvidia.com/t/isaac-sim-6-0-1-gpu-crash-on-dgx-spark-gb10-arm64-driver-595-71-05/376418 |
| vLLM recipes for DGX Spark | https://recipes.vllm.ai/browse?panel=open&hw=dgx_spark_gb10 |
