# Submission kit: the video and the checklist

Track: **Physical AI.** City: **Boston** (a teammate attended Builders & Brews on Oct 2). Bonus: **Best Use of Tavily**.
Deadline: Oct 30, 2026, 10:00 AM PT (1:00 PM ET).

The Devpost text, final and paste-ready: [DEVPOST.md](DEVPOST.md).

## The video (2:30; the aha moment in the first 15 seconds)
Judges said (Oct 21): get to the aha moment fast. Every robot frame is labelled **"Simulation: NVIDIA Isaac Sim"**.
No music, and third-party brand names are hidden. Everything on screen is a real result; the source is in brackets.

| Time | Beat | On screen |
|---|---|---|
| 0:00–0:17 | **REFUSE** | The red-dishes sim frame, then its licence card: 14/40, P(rate ≥ 80%) = 2.4 × 10⁻¹⁰, refused [`docs/results/measurements.jsonl`] |
| 0:17–0:39 | The idea | Title, then the architecture: Nemotron's only path to the robot is `POST /run` |
| 0:39–1:08 | **EARN** | The bananas sim frame; its licence card, 37/40, P = 0.976, licensed [`e2e-revoke-2026-10-28/licences.json`]; the Serverless Job, 71/80 [`serverless-job-2026-10-28.log`] |
| 1:08–1:31 | **BLOCK** | Tavily finds a drill's spec sheet, 1.7 kg > 1 kg, denied [`tests/test_permit.py`, Oct 22 extraction]; then a recall notice for a grease gun, denied [`recall-2026-10-29/`] |
| 1:31–1:57 | **REVOKE** | The two real frames, tiles then wood; the console replaying the run's audit log: revoked by the vision check, then the next request denied with Nemotron's explanation [`e2e-revoke-2026-10-28/`] |
| 1:57–2:16 | Beyond robots | The crop licences: few-shot Nemotron-VL (pepper licensed, tomato not) vs a ResNet-18 trained on Nebius (both) [`crop-2026-10-29*/`] |
| 2:16–2:30 | Close | Built on Nebius Token Factory and AI Cloud, NVIDIA Nemotron, GR00T and Isaac Sim, and Tavily |

Don't show: the offline demo's coin-flip licence numbers as if they were robot runs (only its Nemotron and Tavily
parts are real), or Cosmos as the scene checker (it was measured and not used).

The rules ask projects without hardware to show the key modules working for at least a minute in total: here the
licence cards, the `POST /run` decisions, the console and the sim frames run from 0:00 to 0:17 and 0:39 to 2:16.

## Before submitting
- [ ] Team on Devpost: Gnana Shishir Kumar Chintapalli, Megha Manoj, Thiago Pari
- [x] Run numbers in the README, and the REVOKE beat matches what happened
- [x] Secret scan of the full history: `gitleaks detect --source . --log-opts="--all"` (config in `.gitleaks.toml`)
- [x] The repo is public, with the Apache-2.0 license at the top
- [ ] Video public on YouTube, under 3 minutes (captions: upload the `.srt` made with it)
- [ ] After submitting: `cloud/vm.sh delete` if a VM is up, so the disk stops billing; keep Token Factory testable until
  Dec 15
