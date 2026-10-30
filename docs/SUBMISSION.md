# Submission kit: the video and the checklist

Track: **Physical AI.** City: **Boston** (a teammate attended Builders & Brews on Oct 2). Bonus: **Best Use of Tavily**.
Deadline: Oct 30, 2026, 10:00 AM PT (1:00 PM ET).

The Devpost text, final and paste-ready: [DEVPOST.md](DEVPOST.md).

## The video (2:57; the aha moment in the first 15 seconds)
Judges said (Oct 21): get to the aha moment fast. Every robot frame is labelled **"Simulation · rendered in NVIDIA
Isaac Sim"**. Music: “Impact Prelude” by Kevin MacLeod (incompetech.com), CC BY 4.0, credited on the end card and in
the YouTube description. Captions are burned in. Third-party brand names are hidden. Everything on screen is a real
result; the source is in brackets.

| Time | Beat | On screen |
|---|---|---|
| 0:00–0:18 | **REFUSE** | The red-dishes sim frame, then its licence card: 14/40, P(rate ≥ 80%) = 2.4 × 10⁻¹⁰, refused [`docs/results/measurements.jsonl`] |
| 0:18–0:40 | The idea | Title, then the architecture: Nemotron's only path to the robot is `POST /run` |
| 0:40–1:09 | **EARN** | The bananas sim frame; its licence card, 37/40, P = 0.976, licensed [`e2e-revoke-2026-10-28/licences.json`]; the Serverless Job, 71/80 [`serverless-job-2026-10-28.log`] |
| 1:09–1:32 | **BLOCK** | Tavily finds a drill's spec sheet, 1.7 kg > 1 kg, denied [`tests/test_permit.py`, Oct 22 extraction]; then a recall notice for a grease gun, denied [`recall-2026-10-29/`] |
| 1:32–1:58 | **REVOKE** | The wood-floor frame where GR00T still succeeded, then both real frames side by side (tiles, wood); the vision check's verdict from the run's audit log ("changed", 13:07), revoked, then the next request denied with Nemotron's explanation [`e2e-revoke-2026-10-28/`] |
| 1:58–2:30 | Beyond robots | One application of Learner's Permit: crop health. What crop disease costs: in the US in 2024, corn lost 6.0% of yield and soybeans 5.4%, ≈$6.7B at 2024 prices (our arithmetic, below). Then the crop licences: few-shot Nemotron-VL (pepper licensed, tomato not) vs a ResNet-18 trained on Nebius (both) [`crop-2026-10-29*/`] |
| 2:30–2:44 | Field system | The team's field design (Oct 28): drones and ground robots feed crop models, every action goes through the permit. The built parts are lit, the rest is marked "next" |
| 2:44–2:57 | Close | "Other robot agents ask when they're unsure. Ours asks when it's unproven." Then the catchphrase, "Cultivating trust, one robot skill at a time", and the end card: built on Nebius Token Factory and AI Cloud, NVIDIA Nemotron, GR00T and Isaac Sim, and Tavily |

The disease-cost card shows extension experts' estimates, not our measurements. Crop Protection Network CPN-2007-24
(corn, 2024: 6.0% of US yield, 948.9M bu) and CPN-1018-24 (soybeans: 5.4%, 250.9M bu), priced with USDA NASS Crop
Values 2024 (preliminary, $4.35 and $10.10 per bu): $4.13B + $2.53B ≈ $6.7B. Corn and soybeans were worth $108.8B, so
each 1% of yield saved is ≈ $1.1B a year. The biggest corn losses were tar spot, southern rust and northern corn leaf
blight.

Don't show: the offline demo's coin-flip licence numbers as if they were robot runs (only its Nemotron and Tavily
parts are real), or Cosmos as the scene checker (it was measured and not used).

The rules ask projects without hardware to show the key modules working for at least a minute in total: here the
licence cards, the `POST /run` decisions and the sim frames run from 0:00 to 0:18 and 0:40 to 1:58.

## Before submitting
- [ ] Team on Devpost: Gnana Shishir Kumar Chintapalli, Megha Manoj, Thiago Pari
- [x] Run numbers in the README, and the REVOKE beat matches what happened
- [x] Secret scan of the full history: `gitleaks detect --source . --log-opts="--all"` (config in `.gitleaks.toml`)
- [x] The repo is public, with the Apache-2.0 license at the top
- [ ] Video public on YouTube, under 3 minutes, music credit in the description (captions are burned in; the `.srt` is
  optional)
- [ ] After submitting: `cloud/vm.sh delete` if a VM is up, so the disk stops billing; keep Token Factory testable until
  Dec 15
