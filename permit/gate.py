"""The trust gate: decides, from trial outcomes alone, whether a skill has earned a licence.

Each candidate policy ("arm") carries a Beta(1 + successes, 1 + failures) posterior over its true success rate,
starting from a uniform prior. A sweep spends its trials by Thompson sampling: every slot in a batch goes to the arm
whose posterior draw is highest, so trials drift toward the arm most likely to be good while weak arms still get
sampled now and then. After each batch the sweep stops as soon as one of three things is true:

- licence:   some arm has P(rate >= bar) >= confidence
- refuse:    every arm has P(rate >= bar) <= 1 - confidence, and at least `min_trials` trials have run
- undecided: the trial cap is spent

`min_trials` exists for high bars. Under the uniform prior P(rate >= 0.99) starts at 0.01, already below 0.05, so
without a floor a perfect policy would be refused after its first batch.

Standard library only, so the gate runs anywhere the control plane does.
"""
import math
import random
import time
from dataclasses import dataclass, field

CONFIDENCE = 0.95


def prob_rate_at_least(successes, failures, bar):
    """P(rate >= bar) when rate ~ Beta(1 + successes, 1 + failures).

    With integer parameters the Beta tail is a binomial CDF: P(rate >= x) = P(Binomial(n, x) <= successes) with
    n = successes + failures + 1. Terms are built in log space, because at a 0.99 bar and 400 trials individual
    probabilities underflow a float, and we sum whichever side of the CDF is shorter, then complement if needed.
    """
    if bar <= 0:
        return 1.0
    if bar >= 1:
        return 0.0
    n = successes + failures + 1
    log_x, log_1mx = math.log(bar), math.log1p(-bar)
    lg_n = math.lgamma(n + 1)

    def log_term(k):
        return lg_n - math.lgamma(k + 1) - math.lgamma(n - k + 1) + k * log_x + (n - k) * log_1mx

    def log_sum(ks):
        logs = [log_term(k) for k in ks]
        top = max(logs)
        return top + math.log(sum(math.exp(v - top) for v in logs))

    lower = range(0, successes + 1)  # P(X <= successes)
    upper = range(successes + 1, n + 1)  # P(X > successes)
    if len(lower) <= len(upper):
        p = math.exp(log_sum(lower))
    else:
        p = 1.0 - math.exp(log_sum(upper))
    return min(1.0, max(0.0, p))


@dataclass
class Arm:
    successes: int = 0
    failures: int = 0

    @property
    def trials(self):
        return self.successes + self.failures

    def add(self, outcomes):
        wins = sum(1 for o in outcomes if o)
        self.successes += wins
        self.failures += len(outcomes) - wins

    def draw(self, rng):
        return rng.betavariate(1 + self.successes, 1 + self.failures)

    def confidence_at(self, bar):
        return prob_rate_at_least(self.successes, self.failures, bar)


@dataclass
class Sweep:
    """One commissioning sweep over candidate arms. `state()` / `restore()` round-trip through JSON, so a caller
    can checkpoint after every batch and continue after a crash without losing finished batches."""
    arms: dict
    bar: float
    cap: int
    min_trials: int = 0
    confidence: float = CONFIDENCE
    log: list = field(default_factory=list)

    @classmethod
    def start(cls, arm_ids, bar, cap, min_trials=0, confidence=CONFIDENCE, state=None):
        arms = {a: Arm() for a in arm_ids}
        log = []
        if state:
            for a in arms:
                arms[a] = Arm(state["successes"].get(a, 0), state["failures"].get(a, 0))
            log = list(state["log"])
        return cls(arms, bar, cap, min_trials, confidence, log)

    def state(self):
        return {"successes": {a: arm.successes for a, arm in self.arms.items()},
                "failures": {a: arm.failures for a, arm in self.arms.items()},
                "log": list(self.log)}

    @property
    def trials(self):
        return sum(arm.trials for arm in self.arms.values())

    def scores(self):
        return {a: arm.confidence_at(self.bar) for a, arm in self.arms.items()}

    def leader(self):
        scores = self.scores()
        return max(scores, key=scores.get)

    def verdict(self):
        """'pass', 'fail' or 'inconclusive' once decided, else None."""
        scores = self.scores()
        if max(scores.values()) >= self.confidence:
            return "pass"
        if self.trials >= self.min_trials and all(v <= 1 - self.confidence for v in scores.values()):
            return "fail"
        if self.trials >= self.cap:
            return "inconclusive"
        return None

    def allocate(self, slots, rng=random):
        """Thompson sampling: each slot goes to the arm with the highest posterior draw. Never past the cap."""
        slots = min(slots, self.cap - self.trials)
        plan = {}
        for _ in range(slots):
            pick = max(self.arms, key=lambda a: self.arms[a].draw(rng))
            plan[pick] = plan.get(pick, 0) + 1
        return plan

    def record(self, results, seconds=0.0):
        for a, outcomes in results.items():
            self.arms[a].add(outcomes)
        scores = self.scores()
        lead = max(scores, key=scores.get)
        counts = {a: f"{arm.successes}/{arm.trials}" for a, arm in self.arms.items()}
        entry = {"batch": len(self.log) + 1, "ran": results, "counts": counts,
                 "p_at_least": {a: round(v, 3) for a, v in scores.items()}, "best": lead,
                 "seconds": round(seconds, 1),
                 "line": f"batch {len(self.log) + 1}: " + ", ".join(f"{a} {c}" for a, c in counts.items())
                         + f" | P(rate >= {self.bar:.0%}) for {lead} = {scores[lead]:.2f}"}
        self.log.append(entry)
        return entry

    def run(self, run_batch, batch=4, rng=random, on_batch=None):
        """Drive the sweep to a verdict. run_batch({arm: n}) -> {arm: [1, 0, ...]}. on_batch(entry) runs after every
        batch is recorded (checkpoint there). A resumed sweep that is already decided returns without new trials."""
        decided = self.verdict() if self.log else None
        while decided is None:
            t0 = time.time()
            results = run_batch(self.allocate(batch, rng))
            entry = self.record(results, time.time() - t0)
            if on_batch:
                on_batch(entry)
            decided = self.verdict()
        return decided


def coin_flips(rates, seconds_per_batch=0.0, rng=random):
    """An offline stand-in runner: each trial succeeds with probability rates[arm]. Not robot results; for tests and
    the offline demo. `rates` is read on every call, so a caller can change one between batches."""
    def run_batch(alloc):
        if seconds_per_batch:
            time.sleep(seconds_per_batch)
        outcomes = {}
        for arm, trials in alloc.items():
            chance = rates[arm]
            outcomes[arm] = [int(rng.random() < chance) for _ in range(trials)]
        return outcomes
    return run_batch
