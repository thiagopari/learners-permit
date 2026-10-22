# shellcheck shell=bash
# The spot price cap, shared by cloud/vm.sh and cloud/job.sh (sourced, not run).
#
# A preemptible VM or job runs under a Nebius pricing policy named lp-spot-cap-<platform> with a maximum price per
# GPU hour of LP_MAX_PRICE (default 1.20; RTX PRO 6000 is $1.80 on demand and $0.79-1.79 spot as of Oct 2026). If the
# spot price rises above the cap, Nebius stops the VM instead of charging more, and the policy shows as blocked until
# the price drops. From Nov 2, 2026 spot prices are no longer capped below on demand, so never run spot uncapped
# unattended. LP_MAX_PRICE=follow accepts any spot price; set it only on purpose.
#
# Needs the nebius CLI 0.12.294 or later (`nebius update`): older ones have no pricing-policy commands.

LP_MAX_PRICE=${LP_MAX_PRICE:-1.20}

same_price() { awk -v a="$1" -v b="$2" 'BEGIN { exit !(a + 0 == b + 0) }'; }

# spot_pricing PROJECT_ID PLATFORM: prints the pricing flags for a capped (or, with LP_MAX_PRICE=follow, uncapped)
# preemptible VM, one per line, creating or updating the policy as needed. Progress goes to stderr.
spot_pricing() {
    local project=$1 platform=$2 name="lp-spot-cap-$2" id current
    if [ "$LP_MAX_PRICE" = follow ]; then
        echo "spot: following the market price, with no cap (LP_MAX_PRICE=follow)" >&2
        echo --follows-spot-price
        return
    fi
    awk -v p="$LP_MAX_PRICE" 'BEGIN { exit !(p ~ /^[0-9]+(\.[0-9]{1,3})?$/ && p > 0) }' \
        || { echo "LP_MAX_PRICE must be a price in USD per GPU hour, like 1.20 (or 'follow')" >&2; return 1; }
    id=$(nebius billing pricing-policy get-by-name --parent-id "$project" --name "$name" \
             --format jsonpath='{.metadata.id}' 2> /dev/null || true)
    if [ -z "$id" ]; then
        echo "spot: creating pricing policy $name, max \$$LP_MAX_PRICE per GPU hour" >&2
        id=$(nebius billing pricing-policy create --parent-id "$project" --name "$name" \
                 --compute-instance-spec-v1-platform "$platform" --pricing-max-price-v1-max-price "$LP_MAX_PRICE" \
                 --format jsonpath='{.metadata.id}') || return 1
    else
        current=$(nebius billing pricing-policy get --id "$id" --format jsonpath='{.spec.pricing.max_price_v1.max_price}')
        if ! same_price "$current" "$LP_MAX_PRICE"; then
            echo "spot: changing $name from \$$current to \$$LP_MAX_PRICE per GPU hour" >&2
            nebius billing pricing-policy update --id "$id" --pricing-max-price-v1-max-price "$LP_MAX_PRICE" \
                > /dev/null || { echo "spot: can't change the cap while a VM runs under it; stop it first" >&2; return 1; }
        fi
    fi
    if nebius billing pricing-policy get --id "$id" --format json | grep -q BLOCKED; then
        echo "spot: the market price is above \$$LP_MAX_PRICE right now, so this won't start until it drops" >&2
        echo "      (raise LP_MAX_PRICE, or run on demand without LP_SPOT=1)" >&2
    fi
    echo "spot: capped at \$$LP_MAX_PRICE per GPU hour (policy $id)" >&2
    echo --spot-pricing-policy-id
    echo "$id"
}
