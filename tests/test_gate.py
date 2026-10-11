import json
import math
import random

import pytest

from permit.gate import Arm, Sweep, coin_flips, prob_rate_at_least


def beta_tail_by_integration(s, f, bar, steps=20000):
    """P(rate >= bar) for Beta(1+s, 1+f) by the midpoint rule: an independent check on the closed form."""
    log_norm = math.lgamma(s + f + 2) - math.lgamma(s + 1) - math.lgamma(f + 1)
    h = (1 - bar) / steps
    total = 0.0
    for i in range(steps):
        x = bar + (i + 0.5) * h
        total += math.exp(log_norm + s * math.log(x) + f * math.log1p(-x))
    return total * h


@pytest.mark.parametrize("s,f,bar", [(0, 0, 0.8), (13, 0, 0.8), (38, 2, 0.8), (15, 25, 0.8), (30, 3, 0.8),
                                     (50, 0, 0.99), (120, 1, 0.95), (7, 1, 0.7)])
def test_closed_form_matches_numerical_integration(s, f, bar):
    assert prob_rate_at_least(s, f, bar) == pytest.approx(beta_tail_by_integration(s, f, bar), abs=1e-6)


def test_thresholds_the_plan_relies_on():
    assert round(prob_rate_at_least(38, 2, 0.8), 3) == 0.993           # NVIDIA's bananas baseline
    assert prob_rate_at_least(15, 25, 0.8) < 1e-8                      # red dishes, 15/40
    assert prob_rate_at_least(12, 0, 0.8) < 0.95 <= prob_rate_at_least(16, 0, 0.8)  # batches of 4: first pass 16/16
    assert prob_rate_at_least(12, 0, 0.8) < 0.95 <= prob_rate_at_least(13, 0, 0.8)  # checked every trial: 13/13
    assert prob_rate_at_least(297, 0, 0.99) < 0.95 <= prob_rate_at_least(298, 0, 0.99)  # unattended: 298 straight
    assert prob_rate_at_least(20, 0, 0.8) == pytest.approx(0.991, abs=5e-4)  # one RoboLab launch of 20


def test_tail_is_well_behaved_at_the_edges_and_large_counts():
    assert prob_rate_at_least(0, 0, 0.0) == 1.0 and prob_rate_at_least(5, 5, 1.0) == 0.0
    assert prob_rate_at_least(0, 0, 0.8) == pytest.approx(0.2)  # uniform prior
    for s, f in [(400, 0), (0, 400), (396, 4), (200, 200)]:
        assert 0.0 <= prob_rate_at_least(s, f, 0.99) <= 1.0
    # more successes never lower confidence; more failures never raise it
    assert all(prob_rate_at_least(k, 3, 0.8) <= prob_rate_at_least(k + 1, 3, 0.8) for k in range(60))
    assert all(prob_rate_at_least(30, k, 0.8) >= prob_rate_at_least(30, k + 1, 0.8) for k in range(30))


def test_a_perfect_arm_passes_at_16_with_batches_of_4():
    sweep = Sweep.start(["a"], bar=0.8, cap=100)
    assert sweep.run(coin_flips({"a": 1.0}), batch=4) == "pass" and sweep.arms["a"].trials == 16
    assert len(sweep.log) == 4 and sweep.log[-1]["line"].endswith("= 0.98")


def test_a_broken_arm_is_refused_early_but_not_before_min_trials():
    sweep = Sweep.start(["a"], bar=0.8, cap=100)
    assert sweep.run(coin_flips({"a": 0.0}), batch=4) == "fail" and sweep.trials == 4
    high_bar = Sweep.start(["a"], bar=0.99, cap=400, min_trials=20)
    assert high_bar.run(coin_flips({"a": 0.0}), batch=4) == "fail" and high_bar.trials == 20


def test_the_cap_is_never_exceeded_even_when_the_batch_does_not_divide_it():
    sweep = Sweep.start(["a"], bar=0.8, cap=10)  # 10/10 gives only 0.91, so a perfect arm runs out of trials
    assert sweep.run(coin_flips({"a": 1.0}), batch=4) == "inconclusive" and sweep.trials == 10
    assert [sum(len(v) for v in e["ran"].values()) for e in sweep.log] == [4, 4, 2]


def test_thompson_sampling_sends_most_trials_to_the_better_arm():
    rng = random.Random(1)
    sweep = Sweep.start(["good", "bad"], bar=0.8, cap=100)
    sweep.run(coin_flips({"good": 0.97, "bad": 0.3}, rng=rng), batch=4, rng=rng)
    assert sweep.arms["good"].trials > 3 * sweep.arms["bad"].trials and sweep.leader() == "good"


def test_state_round_trips_through_json_and_a_resume_runs_no_extra_trials():
    first = Sweep.start(["a"], bar=0.8, cap=100)
    calls = []

    def dies_after_two(alloc):
        if len(calls) == 2:
            raise RuntimeError("preempted")
        calls.append(alloc)
        return {a: [1] * n for a, n in alloc.items()}
    with pytest.raises(RuntimeError):
        first.run(dies_after_two, batch=4)
    state = json.loads(json.dumps(first.state()))
    again = Sweep.start(["a"], bar=0.8, cap=100, state=state)
    assert again.arms["a"] == Arm(8, 0) and len(again.log) == 2
    calls.clear()
    assert again.run(dies_after_two, batch=4) == "pass" and again.arms["a"].trials == 16 and len(calls) == 2
    decided = Sweep.start(["a"], bar=0.8, cap=100, state=json.loads(json.dumps(again.state())))
    assert decided.run(lambda alloc: pytest.fail("a decided sweep must not run trials")) == "pass"


@pytest.mark.parametrize("rate,cap,low,high", [(0.90, 40, 0.45, 0.67), (0.90, 100, 0.86, 0.97),
                                               (0.80, 100, 0.08, 0.21), (0.95, 100, 0.97, 1.0)])
def test_licensing_odds_match_the_plan(rate, cap, low, high):
    """PLAN.md's table: cap 40 licenses a true-90% policy ~56% of the time, cap 100 ~92%; false licences at 80% ~14%."""
    rng = random.Random(rate * 1000 + cap)
    runs = 300
    passed = sum(Sweep.start(["a"], bar=0.8, cap=cap).run(coin_flips({"a": rate}, rng=rng), batch=4, rng=rng) == "pass"
                 for _ in range(runs))
    assert low <= passed / runs <= high
