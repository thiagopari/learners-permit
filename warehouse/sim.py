"""Warehouse fleet simulation core — 20 AMRs, grid world, A* routing, health, inventory.
Pure stdlib. Deterministic tick. Emits telemetry the Supervisor LLM reads."""
import math, random, heapq, time
from dataclasses import dataclass, field, asdict

# ---- world layout ----
W, H = 48, 28                     # grid cells
AISLE_X = list(range(6, W-5, 6))  # vertical aisles of racks
PICK_STATIONS = [(2, y) for y in range(4, H-3, 5)]
CHARGE_DOCKS = [(W-3, y) for y in range(4, H-3, 5)]

def build_blocked():
    """Racks occupy columns next to each aisle; robots travel the aisles and cross-lanes."""
    blocked = set()
    for ax in AISLE_X:
        for y in range(3, H-3):
            if y % 7 != 0:                 # leave cross-lanes every 7 rows
                blocked.add((ax-1, y)); blocked.add((ax+1, y))
    return blocked
BLOCKED = build_blocked()

RACK_BINS = {}   # (x,y) -> {sku, qty, expected}; expected is the system-of-record count
def seed_bins():
    i = 0
    for ax in AISLE_X:
        for y in range(3, H-3):
            for dx in (-1, 1):
                c = (ax+dx, y)
                if c in BLOCKED:
                    q = random.randint(0, 40)
                    RACK_BINS[c] = {"sku": f"SKU-{1000+i}", "qty": q, "expected": q}
                    i += 1
seed_bins()

def neighbors(c):
    x, y = c
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
        n = (x+dx, y+dy)
        if 0 <= n[0] < W and 0 <= n[1] < H and n not in BLOCKED:
            yield n

def astar(start, goal):
    if start == goal: return [start]
    openq = [(0, start)]; came = {}; g = {start: 0}
    while openq:
        _, cur = heapq.heappop(openq)
        if cur == goal:
            path = [cur]
            while cur in came: cur = came[cur]; path.append(cur)
            return path[::-1]
        for n in neighbors(cur):
            ng = g[cur] + 1
            if ng < g.get(n, 1e9):
                came[n] = cur; g[n] = ng
                h = abs(n[0]-goal[0]) + abs(n[1]-goal[1])
                heapq.heappush(openq, (ng+h, n))
    return [start]

TASKS = ("pick", "carry", "charge", "idle")

@dataclass
class Robot:
    id: int
    x: float; y: float
    zone: int
    task: str = "idle"
    goal: tuple = None
    path: list = field(default_factory=list)
    battery: float = 100.0
    temp: float = 38.0
    carrying: dict = None
    error: str = ""
    stuck_ticks: int = 0
    speed: float = 0.9
    ok: bool = True

    def pose(self): return (round(self.x,2), round(self.y,2))
    def pose_i(self): return (round(self.x), round(self.y))

class Warehouse:
    def __init__(self, n=20, seed=7):
        self.rng = random.Random(seed)
        self.t = 0
        self.robots = []
        lanes = [y for y in range(3, H-3) if y % 7 == 0]
        for i in range(n):
            y = self.rng.choice(lanes); x = self.rng.randint(1, W-2)
            while (x,y) in BLOCKED: x = self.rng.randint(1, W-2)
            r = Robot(id=i, x=x, y=y, zone=i % max(1,len(AISLE_X)))
            self.robots.append(r); self._assign(r)
        self.events = []          # code-detected issues feed the Supervisor
        self.picks = 0
        self.inject = {}          # demo hooks: forced faults

    def _free_cell(self):
        while True:
            c = (self.rng.randint(1, W-2), self.rng.randint(1, H-2))
            if c not in BLOCKED: return c

    def _assign(self, r):
        if r.battery < 20 and r.task != "charge":
            r.task = "charge"; r.goal = min(CHARGE_DOCKS, key=lambda d: abs(d[0]-r.x)+abs(d[1]-r.y))
        elif r.task in ("idle", None):
            r.task = "pick"
            # go to a bin that has stock
            stocked = [c for c,b in RACK_BINS.items() if b["qty"] > 0]
            r.goal = self.rng.choice(stocked) if stocked else self._free_cell()
        r.path = astar((round(r.x), round(r.y)), r.goal)

    def tick(self):
        self.t += 1
        for r in self.robots:
            self._step(r)
        self._detect()
        return self.t

    def _step(self, r):
        # injected faults for the demo
        if self.inject.get(r.id) == "stuck": r.stuck_ticks += 1; return
        if self.inject.get(r.id) == "overheat": r.temp = min(95, r.temp+2)

        r.battery = max(0, r.battery - (0.08 if r.task!="idle" else 0.02))
        r.temp += (0.15 if r.task in ("pick","carry") else -0.1)
        r.temp = max(36, min(92, r.temp))

        if not r.path or len(r.path) < 2:
            # arrived
            if r.task == "pick" and r.goal in RACK_BINS and RACK_BINS[r.goal]["qty"] > 0:
                RACK_BINS[r.goal]["qty"] -= 1; RACK_BINS[r.goal]["expected"] -= 1
                r.carrying = {"sku": RACK_BINS[r.goal]["sku"], "qty": 1}
                r.task = "carry"; r.goal = self.rng.choice(PICK_STATIONS); r.path = astar(r.pose_i(), r.goal)
            elif r.task == "carry":
                self.picks += 1; r.carrying = None; r.task = "idle"; self._assign(r)
            elif r.task == "charge":
                r.battery = min(100, r.battery + 6)
                if r.battery > 95: r.task = "idle"; self._assign(r)
            else:
                self._assign(r)
            r.stuck_ticks = 0
            return

        # move toward next path cell
        nx, ny = r.path[1]
        dx, dy = nx - r.x, ny - r.y
        d = math.hypot(dx, dy)
        if d < 0.1:
            r.path.pop(0); r.stuck_ticks = 0
        else:
            r.x += r.speed * dx/d; r.y += r.speed * dy/d
            if abs(r.x-nx) < 0.12 and abs(r.y-ny) < 0.12:
                r.x, r.y = nx, ny; r.path.pop(0)

    def _detect(self):
        """CODE flags problems; the LLM narrates/routes them. (the design rule)"""
        self.events = []
        for r in self.robots:
            r.ok = True; r.error = ""
            if r.battery < 15:
                r.ok=False; r.error="LOW_BATTERY"; self.events.append(self._ev(r,"health","battery %.0f%%"%r.battery,"critical"))
            if r.temp > 80:
                r.ok=False; r.error="OVERHEAT"; self.events.append(self._ev(r,"health","motor %.0fC"%r.temp,"warning"))
            if r.stuck_ticks > 3:
                r.ok=False; r.error="STUCK"; self.events.append(self._ev(r,"stuck","no progress %dt"%r.stuck_ticks,"warning"))
        # inventory shortfall per zone (the "inventory misses something" beat)
        for zi, ax in enumerate(AISLE_X):
            bins = [b for c,b in RACK_BINS.items() if abs(c[0]-ax)<=1]
            total = sum(b["qty"] for b in bins)
            if total < 30:
                self.events.append({"type":"inventory","zone":zi,"detail":f"zone {zi} stock {total}","sev":"warning","t":self.t})
        return self.events

    def _ev(self, r, typ, detail, sev):
        return {"type":typ,"robot":r.id,"zone":r.zone,"detail":detail,"sev":sev,"t":self.t}

    def telemetry(self):
        return {
            "t": self.t,
            "picks": self.picks,
            "robots": [{
                "id": r.id, "x": round(r.x,2), "y": round(r.y,2),
                "task": r.task, "battery": round(r.battery), "temp": round(r.temp),
                "zone": r.zone, "carrying": r.carrying, "error": r.error, "ok": r.ok,
                "goal": r.goal,
            } for r in self.robots],
            "events": self.events,
        }

    def layout(self):
        return {"w":W,"h":H,"blocked":list(BLOCKED),
                "stations":PICK_STATIONS,"docks":CHARGE_DOCKS,"aisles":AISLE_X}

    def inventory(self):
        """Per-zone bins: qty is what is physically there, expected is what the system thinks."""
        zones = []
        for zi, ax in enumerate(AISLE_X):
            bins = [{"bin": list(c), **b} for c, b in RACK_BINS.items() if abs(c[0]-ax) <= 1]
            zones.append({"zone": zi, "aisle_x": ax, "total": sum(b["qty"] for b in bins),
                          "expected_total": sum(b["expected"] for b in bins), "bins": bins})
        return {"zones": zones}

    def shrink(self, zone, units=6):
        """Demo fault: stock disappears without a recorded pick (the 'inventory misses something' beat)."""
        ax = AISLE_X[zone]
        bins = [b for c, b in RACK_BINS.items() if abs(c[0]-ax) <= 1 and b["qty"] > 0]
        taken = 0
        for b in self.rng.sample(bins, min(3, len(bins))):
            k = min(b["qty"], units - taken)
            b["qty"] -= k; taken += k
            if taken >= units: break
        return taken
