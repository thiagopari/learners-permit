#!/usr/bin/env bash
# Idle guard for the GPU VM. Runs every 5 minutes from a systemd timer (cloud/vm.sh installs it through cloud-init)
# and powers the VM off after LP_IDLE_MIN minutes (default 30) with no GPU work, no CPU work, no typing in any
# terminal, and no /run/lp-keepalive file (cloud/setup_vm.sh holds one while it downloads).
#
# Only safe on a VM created with --recovery-policy fail, which cloud/vm.sh sets. Nebius treats a poweroff from
# inside the VM as a failure: under the default policy it restarts the VM and keeps billing it
# (docs.nebius.com/compute/virtual-machines/stopped-with-linux-commands).
set -u
idle_min=${LP_IDLE_MIN:-30}
r=${LP_GUARD_TEST_ROOT:-}  # tests point /run, /proc and /dev at a fake tree
state=$r/run/lp-idle-guard  # tmpfs: a boot starts the idle clock afresh
now=$(date +%s)
[ -f "$state" ] || echo "$now" > "$state"

busy=()
gpu=$(timeout 20 nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null | sort -n | tail -1)
[ "${gpu:-0}" -ge 10 ] && busy+=("gpu ${gpu}%")
load=$(cut -d' ' -f2 "$r/proc/loadavg")  # 5-minute average; Isaac Sim's boot and installs are CPU-bound
awk -v l="$load" 'BEGIN { exit !(l >= 1.0) }' && busy+=("load $load")
# A terminal's atime moves when someone types in it; that is what `w` reports as idle time.
[ -n "$(find "$r/dev/pts" -maxdepth 1 -name '[0-9]*' -amin -"$idle_min" 2>/dev/null)" ] && busy+=("typing")
[ -e "$r/run/lp-keepalive" ] && busy+=("keepalive")

if [ ${#busy[@]} -gt 0 ]; then
    echo "$now" > "$state"
    echo "busy: ${busy[*]}"
    exit 0
fi
idle=$(( (now - $(cat "$state")) / 60 ))
echo "idle for $idle of $idle_min minutes"
if [ "$idle" -ge "$idle_min" ]; then
    logger -t lp-idle-guard "idle for $idle minutes, powering off"
    systemctl poweroff
fi
