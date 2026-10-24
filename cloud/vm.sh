#!/usr/bin/env bash
# The Nebius GPU VM for Learner's Permit, driven from the laptop.
#
#   cloud/vm.sh create    create the VM (RTX PRO 6000, 96 GB) with the idle guard; it boots and starts billing
#   cloud/vm.sh setup     copy this repo's committed HEAD and run cloud/setup_vm.sh in tmux there, then follow its log
#   cloud/vm.sh status    state, public IP, and the idle guard's last check
#   cloud/vm.sh ssh       a shell on the VM          cloud/vm.sh tunnel   the permit console at http://localhost:8099
#   cloud/vm.sh record [TASK] [N]   N episodes (default 2) with viewport video; starts the GR00T server if needed
#   cloud/vm.sh dashboard RoboLab's dashboard (replays episode videos) at http://localhost:8080, plus the console
#   cloud/vm.sh clips     download every recorded episode video to results/clips/
#   cloud/vm.sh start | stop                         a stopped VM bills only its disk ($0.071 per GiB-month)
#   cloud/vm.sh delete    delete the VM and its boot disk (asks first)
#   cloud/vm.sh user-data print the cloud-init that create sends
#
# Needs: the nebius CLI with a profile (`nebius profile create`), and in the project's .env (git-ignored; or
# ~/.config/learners-permit.env): NEBIUS_PROJECT_ID (a project in uk-south2 or eu-south1) and, for setup, HF_TOKEN.
# Options: LP_SPOT=1 (preemptible: $0.79-1.79/h instead of $1.80/h, capped at LP_MAX_PRICE, default 1.20, by a
# pricing policy, see cloud/price_cap.sh; preemption or a price above the cap stops it, the disk survives),
# LP_DISK_GIB (default 150; grow later with `nebius compute disk update --size-gibibytes`), LP_SSH_KEY.
set -euo pipefail
cd "$(dirname "$0")/.."
# shellcheck source=cloud/price_cap.sh
. cloud/price_cap.sh
# Keys: the project's .env (git-ignored), else ~/.config/learners-permit.env. Strip Windows line endings (Notepad).
for f in .env ~/.config/learners-permit.env; do
    # shellcheck source=/dev/null
    [ -f "$f" ] && { set -a; . <(tr -d '\015' < "$f"); set +a; break; }  # \015: Notepad's CR
done
[ $# -gt 0 ] || { sed -n '2,19p' "$0"; exit 1; }
: "${NEBIUS_PROJECT_ID:?set NEBIUS_PROJECT_ID in .env}"
# Not "lp": Ubuntu already has an lp system user (the printer daemon) with a nologin shell, and cloud-init only adds
# the key to an existing user, so every SSH session ended "This account is currently not available" (Oct 23).
name=lp-rtx6000 user=permit key=${LP_SSH_KEY:-$HOME/.ssh/id_ed25519}
ssh_opts=(-i "$key" -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30)

vm_id() { nebius compute instance get-by-name --parent-id "$NEBIUS_PROJECT_ID" --name "$name" --format jsonpath='{.metadata.id}'; }
vm_json() { nebius compute instance get --id "$(vm_id)" --format json; }
vm_ip() {  # dynamic: a stopped VM gives its public IP back, so look it up every time
    local ip
    ip=$(vm_json | jq -r '.status.network_interfaces[0].public_ip_address.address // empty | split("/")[0]')
    [ -n "$ip" ] || { echo "no public IP: is the VM running? ($0 status)" >&2; exit 1; }
    echo "$ip"
}
on_vm() { local ip; ip=$(vm_ip); ssh "${ssh_opts[@]}" "$user@$ip" "$@"; }

gr00t_up() {  # the GR00T policy server on the VM's 127.0.0.1:5600, in tmux, unless it's already listening
    # Not 5555, GR00T's default: on Nebius images NVIDIA's DCGM monitor (nv-hostengine) listens there. And the port
    # being open isn't enough: it has to be GR00T that holds it.
    on_vm 'gr00t_listening() { ss -ltn | grep -q "127.0.0.1:5600 " && pgrep -f run_gr00t_server > /dev/null; }
        gr00t_listening && exit 0
        if ss -ltn | grep -q ":5600 "; then echo "port 5600 is held by something other than GR00T:"; sudo ss -ltnp | grep ":5600 "; exit 1; fi
        tmux has-session -t gr00t 2> /dev/null || tmux new-session -d -s gr00t "cd ~/Isaac-GR00T &&
            CUDA_VISIBLE_DEVICES=0 ~/.local/bin/uv run python gr00t/eval/run_gr00t_server.py \
            --model-path nvidia/GR00T-N1.7-DROID --embodiment-tag OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT --device cuda \
            --host 127.0.0.1 --port 5600 --use-sim-policy-wrapper 2>&1 | tee ~/gr00t-server.log"
        echo "starting the GR00T policy server (a few minutes the first time)"
        for _ in $(seq 180); do gr00t_listening && exit 0; sleep 5; done
        tail -20 ~/gr00t-server.log; echo "the GR00T server is not up after 15 minutes"; exit 1'
}

user_data() {  # cloud-init: our user and key, plus the idle guard on a 5-minute timer from the first boot
    local guard
    guard=$(sed 's/^/      /' cloud/idle_guard.sh)
    cat <<EOF
#cloud-config
users:
  - name: $user
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/bash
    ssh_authorized_keys:
      - $(cat "$key.pub")
write_files:
  - path: /usr/local/bin/lp-idle-guard
    permissions: "0755"
    content: |
$guard
  - path: /etc/systemd/system/lp-idle-guard.service
    content: |
      [Unit]
      Description=Power the VM off when idle (Learner's Permit)
      [Service]
      Type=oneshot
      ExecStart=/usr/local/bin/lp-idle-guard
  - path: /etc/systemd/system/lp-idle-guard.timer
    content: |
      [Unit]
      Description=Check for idleness every 5 minutes
      [Timer]
      OnBootSec=5min
      OnUnitActiveSec=5min
      [Install]
      WantedBy=timers.target
runcmd:
  - [systemctl, daemon-reload]
  - [systemctl, enable, --now, lp-idle-guard.timer]
EOF
}

case "${1:-}" in
create)
    [ -f "$key.pub" ] || { echo "no SSH key at $key.pub (set LP_SSH_KEY)"; exit 1; }
    subnet=$(nebius vpc subnet list --parent-id "$NEBIUS_PROJECT_ID" --format jsonpath='{.items[0].metadata.id}')
    pricing=()  # regular VM by default
    if [ "${LP_SPOT:-0}" = 1 ]; then
        mapfile -t pricing < <(spot_pricing "$NEBIUS_PROJECT_ID" gpu-rtx6000-a)
        [ "${#pricing[@]}" -gt 0 ] || exit 1
        pricing+=(--preemptible-on-preemption stop)
    fi
    # --recovery-policy fail is what makes the idle guard safe: a poweroff from inside the VM then stops it, where
    # the default policy restarts it and keeps billing. It can only be set at creation.
    nebius compute instance create --parent-id "$NEBIUS_PROJECT_ID" --name "$name" \
        --resources-platform gpu-rtx6000-a --resources-preset 1gpu-24vcpu-218gb "${pricing[@]}" \
        --recovery-policy fail \
        --boot-disk-managed-disk-name "$name-boot" --boot-disk-managed-disk-type network_ssd \
        --boot-disk-managed-disk-size-gibibytes "${LP_DISK_GIB:-150}" \
        --boot-disk-managed-disk-block-size-bytes 4096 \
        --boot-disk-managed-disk-source-image-family-image-family ubuntu24.04-cuda13.0 \
        --boot-disk-attach-mode READ_WRITE \
        --cloud-init-user-data "$(user_data)" \
        --network-interfaces "[{\"name\": \"eth0\", \"subnet_id\": \"$subnet\", \"ip_address\": {}, \"public_ip_address\": {}}]" \
        --format jsonpath='{.metadata.id}'
    echo; echo "Created $name; it is billing from now. Next: $0 setup"
    ;;
setup)
    : "${HF_TOKEN:?set HF_TOKEN in .env (a Read token, after accepting Cosmos-Reason2-2B)}"
    for _ in $(seq 30); do on_vm true 2> /dev/null && break; sleep 10; done  # a fresh VM takes a few minutes
    on_vm 'cloud-init status --wait > /dev/null'  # until our user, key and idle guard are in place
    if on_vm 'tmux has-session -t setup 2> /dev/null'; then
        echo "setup is already running on the VM; following it"
    else
        [ -z "$(git status --porcelain)" ] || echo "note: uncommitted changes are not copied, only HEAD"
        # Swap in the new code, but carry over permit/data (licences, sweep checkpoints, audit log) and the venv.
        git archive --format=tar HEAD | on_vm 'set -e; cd ~; rm -rf lp.new; mkdir lp.new; tar -x -C lp.new
            for d in permit/data .venv; do [ ! -e "learners-permit/$d" ] || mv "learners-permit/$d" "lp.new/$d"; done
            rm -rf learners-permit; mv lp.new learners-permit'
        git rev-parse --short HEAD | on_vm 'cat > ~/learners-permit/.commit'
        printf '%s' "$HF_TOKEN" | on_vm 'umask 077 && mkdir -p ~/.cache/huggingface && cat > ~/.cache/huggingface/token'
        on_vm 'rm -f ~/lp-setup.status && tmux new-session -d -s setup "bash ~/learners-permit/cloud/setup_vm.sh"'
    fi
    echo "Setup runs in tmux on the VM, so closing the laptop is fine. Ctrl-C here stops following, not the setup."
    on_vm 'touch ~/lp-setup.log; tail -n +1 -f ~/lp-setup.log & t=$!
           while tmux has-session -t setup 2> /dev/null; do sleep 5; done; sleep 1; kill $t
           echo; echo "setup exit status: $(cat ~/lp-setup.status 2> /dev/null || echo unknown) (0 = all checks passed)"'
    ;;
status)
    vm_json | jq -r '"\(.metadata.name): \(.status.state)  ip \(.status.network_interfaces[0].public_ip_address.address // "none")"'
    on_vm 'sudo journalctl -u lp-idle-guard -n 1 -o cat' 2> /dev/null || true
    ;;
user-data) user_data ;;  # what create sends, for inspection
ssh) on_vm ;;
tunnel)
    echo "permit console: http://localhost:8099 (start it on the VM: .venv/bin/python -m permit.server --runner robolab)"
    ip=$(vm_ip)
    ssh "${ssh_opts[@]}" -N -L 8099:127.0.0.1:8099 "$user@$ip"
    ;;
record)  # record TASK [N]: N episodes (default 2) with third-person viewport video, through permit's RoboLab runner
    task=${2:-BananasInBinThreeTotalTask} n=${3:-2}
    [[ $task =~ ^[A-Za-z0-9_]+$ && $n =~ ^[0-9]+$ ]] || { echo "usage: $0 record [TASK] [N]"; exit 1; }
    gr00t_up
    on_vm "cd ~/learners-permit && ROBOLAB_DIR=~/RoboLab timeout -k 60 60m .venv/bin/python -c \"
from permit import runners
print('successes:', runners.robolab('$task', {'a': 5600}, video='viewport', retries=0)({'a': $n})['a'])\" &&
           echo 'clips:' && find ~/RoboLab/output -name '*_viewport.mp4' -mmin -60 | tail -$n"
    echo "Watch them: $0 dashboard (in the browser), or $0 clips (download to results/clips)"
    ;;
dashboard)  # RoboLab's results dashboard (episode videos) and the permit console, through an SSH tunnel
    # Bound to 127.0.0.1 on the VM: RoboLab's default 0.0.0.0 would put it on the VM's public IP.
    on_vm 'tmux has-session -t dashboard 2> /dev/null || tmux new-session -d -s dashboard \
        "cd ~/RoboLab && ~/.local/bin/uv run robolab-dashboard --output-dir ~/RoboLab/output --host 127.0.0.1 --port 8080"'
    echo "RoboLab dashboard (episode videos): http://localhost:8080"
    echo "permit console (if running on the VM): http://localhost:8099. Ctrl-C closes the tunnel."
    ip=$(vm_ip)
    ssh "${ssh_opts[@]}" -N -L 8080:127.0.0.1:8080 -L 8099:127.0.0.1:8099 "$user@$ip"
    ;;
clips)  # download every recorded episode video to results/clips/ (git-ignored)
    mkdir -p results/clips
    on_vm 'cd ~/RoboLab/output 2> /dev/null && find . -name "*.mp4" -print0 | tar -c --null -T -' | tar -x -C results/clips
    find results/clips -name '*.mp4' | sort
    ;;
start | stop) nebius compute instance "$1" --id "$(vm_id)" ;;
delete)
    read -r -p "Delete $name and its boot disk? Everything on it is lost. Type the name to confirm: " answer
    [ "$answer" = "$name" ] || { echo "not deleted"; exit 1; }
    nebius compute instance delete --id "$(vm_id)"  # also deletes the managed boot disk
    ;;
*) sed -n '2,19p' "$0"; exit 1 ;;
esac
