# FleetOps on the GB10

Integration of the FleetOps warehouse demo: the fleet sim, the supervisor LLM, the dashboard and the
Discord scheduler side, all on this box. One command runs the stack:

    ./fleetops.sh start      # model, bridge, sim, supervisor, agent check, glue, dashboard, navbot
    ./fleetops.sh status
    ./fleetops.sh stop       # leaves the model server and the agent sandbox running
    ./fleetops.sh logs sim

| Part | Where | Port |
|---|---|---|
| Fleet sim (headless, pure Python) | `sim/fleet.py`, `sim/fleet_runner.py` | (pushes) |
| Sim bridge: telemetry, inventory, layout, event stream | `sim/sim_bridge.py` | 3001 |
| Supervisor tool service + skill | `~/hack/src/app` (git) | 8090 |
| Supervisor LLM agent | OpenClaw in NemoClaw sandbox `navfix` | 18789 |
| Glue: dashboard sources, Discord forwarding, live fleet log | `glue/fleetops_glue.py` | 7100 (localhost) |
| Dashboard | `~/navfix/dashboard`, `config.fleetops.json` | 8095 (LAN) |
| navbot (Discord) | `~/navfix/navbot`, `.env` (secret) | 8787 |
| Model | docker `vllm-qwen`, Qwen3.6-35B-A3B NVFP4 | 8000 |

Isaac Sim does not run on the GB10 (aarch64). `isaac/warehouse_live.py` runs on an x86 RTX laptop and renders
the same fleet logic; it can push to the bridge instead of `sim` (`--bridge http://<gb10>:3001`, same token).

Live fleet log for the scheduler: `curl localhost:7100/fleetlog?minutes=5` (same JSON as `samples/fleet_log_5min.json`).
Agent thinking is turned on by `enable_thinking.sh`; re-run it after any `nemoclaw navfix rebuild`.
