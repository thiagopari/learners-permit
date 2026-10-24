# Feedback: Nebius Token Factory, Nebius AI Cloud, NVIDIA models and tools

Draft for the submission form's required feedback section. Everything below happened while building Learner's
Permit (Oct 4–29, 2026); dates and versions are as we hit them. Team: fill in anything we missed before submitting.

## Nebius Token Factory

**What we used it for.** Nemotron-3-Super-120B-A12B (`nvidia/nemotron-3-super-120b-a12b`) as the planner (an order
becomes catalogue skill calls, through OpenAI-style tool calling) and as the explainer (plain-English reasons for
every refusal, block and revocation, written from audit facts).

**What worked well**
- Zero to first answer in minutes: the endpoint is OpenAI-compatible, so the `openai` client just worked with a new
  `base_url`. `/v1/models` listed 28 models, including five Nemotrons.
- Tool calling was right on every order we tried: correct skill, a speed (`30%`) and a part number pulled out of
  free text, and no call at all for an order with no matching skill.
- Cheap enough not to think about: the whole build cost cents.

**What needs work**
- **Reasoning is on by default, and that isn't obvious.** An explanation of three sentences spent ~250 of 318
  completion tokens on hidden reasoning, and with `max_tokens=600` some answers came back cut off mid-sentence.
  `extra_body={"chat_template_kwargs": {"enable_thinking": False}}` fixed it (1.3 s instead of 3–4 s), but we found
  that by trying options; we didn't find it on the model's Token Factory page. Please document per model whether
  reasoning is on by default, how to turn it off, and that reasoning tokens count against `max_tokens`.
- **Narrow no-break spaces (U+202F)** appeared before numbers in answers. Harmless, but worth knowing.
- **Cosmos Reason 2 isn't on Token Factory**, and its Hugging Face page says no inference provider serves it. For
  the Physical AI track, a hosted Cosmos Reason endpoint would remove the need to self-host a 2B VLM on the GPU VM.
- The FAQ says the hackathon promo codes are Token Factory credits only; we learned that late. Saying so on the
  overview page would save teams a billing surprise on AI Cloud.

**Would we build with it again?** Yes: OpenAI compatibility and Nemotron's tool calling made it the easiest part of
the stack.

## Nebius AI Cloud (Compute: RTX PRO 6000 VM in uk-south2; Serverless AI Jobs)

**What we used it for.** An RTX PRO 6000 Blackwell (96 GB) VM to run GR00T N1.7 and Isaac Sim 5.0 through NVIDIA's
RoboLab, plus a Serverless AI Job image for evaluation sweeps.

**What worked well**
- The GPU itself: RTX PRO 6000 Blackwell Server Edition, driver 580.173.02, Vulkan available, RT cores for Isaac Sim.
  The RTX PRO 6000 quota in uk-south2 was there when we needed it.
- The CLI covers everything (VMs, disks, subnets, pricing policies, jobs), and `--format jsonpath` made scripting
  easy. GitHub federation login worked from WSL.
- Renaming a project in the console was one click, and the project ID stays stable.
- `--recovery-policy fail` makes a poweroff from inside the VM really stop it, which made a 30-minute idle guard safe.

**What needs work**
- **Port 5555 is taken on the GPU images.** NVIDIA's DCGM host engine (`nv-hostengine`) listens on 127.0.0.1:5555,
  which is also GR00T's default policy-server port, so the GR00T server loaded its weights and then failed with
  `Address already in use`. Please list the ports the image's own services use.
- **The `ubuntu24.04-cuda13.0` image has no `libGLU.so.1`.** Isaac Sim's MDL material library (`libneuray.so`) needs
  it, and its absence shows up as a segfault in `librtx.mdltranslator.plugin.so` on the first launch, not as a missing
  library. Shipping `libglu1-mesa` (and `libxt6`) on GPU images meant for simulation would save hours.
- **An old CLI fails silently on new pricing.** Our CLI 0.12.242 (July) had no `billing pricing-policy` commands and
  no `--follows-spot-price`; nothing told us to update until a command didn't exist. `nebius update` to 0.12.294
  fixed it. A version warning when the API has moved on would help.
- **Which GPU platforms Serverless AI Jobs support isn't documented.** The jobs docs use `gpu-l40s-a` as the example
  and the VM-types page doesn't mention jobs, so we couldn't tell whether `gpu-rtx6000-a` (the platform with RT cores
  that Isaac Sim needs) can run a job before trying.
- **Spot pricing changed mid-hackathon** (a floating $0.79–1.79 per GPU hour from Oct 8; uncapped relative to on
  demand from Nov 2). Pricing policies handle it well, but the change landed on teams mid-project; the console banner
  was the only notice we saw.

**Would we build with it again?** Yes. The hardware and the CLI were solid; the two image issues (DCGM's port and the
missing libGLU) cost most of the time we lost, and both are cheap to fix or document.

## NVIDIA models and tools

**What we used.** GR00T N1.7-DROID (vision-language-action policy) through Isaac-GR00T's policy server; Isaac Sim 5.0
and RoboLab (`BananasInBinThreeTotalTask`, `RedDishesInBinTask`); Nemotron-3-Super (above); Cosmos-Reason2-2B (gated,
for scene verification).

**What worked well**
- RoboLab's GR00T runner and its `episode_results.jsonl` were exactly what an evaluation harness needs; every CLI flag
  we relied on (`--num-envs`, `--num-runs`, `--output-folder-name`, `--video-mode`, `--randomize-background`) existed
  and behaved as documented, and its dashboard replays episode videos.
- GR00T N1.7-DROID loaded in ~1.5 minutes on the RTX PRO 6000 and served over ZeroMQ, which made it easy to keep the
  policy (Python 3.12) and the simulator (Python 3.11) in separate environments.
- The Cosmos-Reason2-2B gate on Hugging Face approved us at once.

**What needs work**
- **Isaac Sim's failure mode for a missing system library is a segfault** (see AI Cloud above). Failing fast with
  "libGLU.so.1 not found; install libglu1-mesa" when `libneuray` doesn't load would turn hours into seconds.
- **GR00T's default port, 5555, collides with DCGM** on most data-center GPU images. A different default, or a note
  in the server's README, would help everyone running on cloud GPUs.
- The Isaac-GR00T example README for RoboLab was behind the RoboLab repo itself (we followed RoboLab's own README).

**Would we build with them again?** Yes. GR00T plus RoboLab gave us real, repeatable success rates to gate on, which is
the core of the project.

## Tavily (bonus sponsor)

**What we used it for.** `search` then `extract` to find a part's spec sheet and read its weight, which can only block
a robot pick.

- **Worked well:** fast (1–4 s per check), and `extract` returned spec tables in a parseable form.
- **Needs work:** for "Makita XFD131 datasheet weight", basic search returned only company-profile sites (LeadIQ,
  CB Insights, RocketReach); `specifications` at `search_depth: "advanced"` found the manufacturer and retailers.
  `extract` failed on the manufacturer's own product page. A made-up part number matched an unrelated real part
  (`48213-04030`), so we now require the page to name the part before trusting its weight.
