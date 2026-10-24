"""The Cosmos Reason 2 scene check, with a fake vision model and fake frames: no GPU, no ffmpeg."""
import json
import random
import types

import pytest

from permit import authz, explainer, runners, scene
from permit.server import Permit
from tests.test_permit import FakeRoboLab

AI = authz.AGENT


@pytest.mark.parametrize("text,expect", [
    ('<think>the wall is now red</think><answer>{"same_conditions": false, "changes": ["red background"]}</answer>',
     {"verdict": "changed", "changes": ["red background"]}),
    ('<answer>{"same_conditions": true, "changes": []}</answer>', {"verdict": "same", "changes": []}),
    ('Looks the same. {"same_conditions": true}', {"verdict": "same", "changes": []}),  # no tags: the last JSON
])
def test_verdicts_are_parsed(text, expect):
    assert scene.verdict(text) == expect


@pytest.mark.parametrize("text", [
    "", "I can't tell.", "<answer>not json</answer>", '<answer>{"same_conditions": "maybe"}</answer>',
    '<answer>{"same_conditions": false, "changes": []}</answer>',  # "changed" but nothing named
])
def test_anything_unclear_is_unknown(text):
    assert scene.verdict(text)["verdict"] == "unknown"


def test_a_check_that_cannot_run_is_unknown():
    def down(reference, current):
        raise ConnectionError("cosmos server not running")
    v = scene.check("ref.jpg", "now.jpg", ask=down)
    assert v["verdict"] == "unknown" and "ConnectionError" in v["reason"]


def test_the_request_sends_both_frames_and_asks_for_tagged_json(tmp_path):
    for name in ("ref.jpg", "now.jpg"):
        (tmp_path / name).write_bytes(b"\xff\xd8 not really a jpeg")
    sent = []
    msg = types.SimpleNamespace(content='<answer>{"same_conditions": true}</answer>')
    client = types.SimpleNamespace(chat=types.SimpleNamespace(completions=types.SimpleNamespace(
        create=lambda **kw: sent.append(kw) or types.SimpleNamespace(choices=[types.SimpleNamespace(message=msg)]))))
    assert scene.verdict(scene.cosmos(str(tmp_path / "ref.jpg"), str(tmp_path / "now.jpg"), client=client))["verdict"] == "same"
    parts = sent[0]["messages"][-1]["content"]
    assert [p["type"] for p in parts] == ["image_url", "image_url", "text"]
    assert parts[0]["image_url"]["url"].startswith("data:image/jpeg;base64,") and "<answer>" in parts[2]["text"]
    assert sent[0]["model"] == scene.MODEL


def test_the_robolab_runner_reports_the_videos_it_recorded(tmp_path, monkeypatch):
    class WithVideos(FakeRoboLab):
        def __init__(self, cmd, cwd, env, **kw):
            super().__init__(cmd, cwd, env, **kw)
            out = FakeRoboLab.root / "output" / cmd[cmd.index("--output-folder-name") + 1]
            (out / "put_dishes.mp4").write_bytes(b"")
            (out / "put_dishes_viewport.mp4").write_bytes(b"")
    FakeRoboLab.root = tmp_path
    monkeypatch.setattr(runners.subprocess, "Popen", WithVideos)
    rb = runners.robolab("RedDishesInBinTask", {"ft": 5601}, root=str(tmp_path), video="viewport")
    rb({"ft": 2})
    assert [v.rsplit("/", 1)[-1].rsplit("\\", 1)[-1] for v in rb.videos["ft"]] == ["put_dishes_viewport.mp4",
                                                                                 "put_dishes.mp4"]


# --- in the control plane --------------------------------------------------------------------------------------

class Cell:
    """A fake cell: every run "records" a video, and the fake Cosmos answers with whatever `seen` holds."""

    def __init__(self, tmp_path, seen="same", rate=1.0):
        random.seed(0)
        self.seen, self.calls = seen, []
        self.p = Permit(data_dir=str(tmp_path), clock=lambda: types.SimpleNamespace(tm_hour=14), lock_timeout=0.2,
                        check_scene=self.cosmos, frame=lambda video, out: out)
        self.p.rates["bananas_in_bin"]["n17_droid"] = rate
        real = self.p.run_batch

        def run_batch(skill):
            rb = real(skill)

            def recorded(alloc):
                out = rb(alloc)
                recorded.videos = {arm: [f"{arm}.mp4"] for arm in alloc}
                return out
            recorded.videos = {}
            return recorded
        self.p.run_batch = run_batch

    def cosmos(self, reference, current):
        self.calls.append((reference, current))
        if self.seen == "changed":
            return {"verdict": "changed", "changes": ["the background is now a brick wall"], "model": scene.MODEL}
        return {"verdict": self.seen, "changes": [], "model": scene.MODEL}


def test_commissioning_keeps_a_reference_frame_and_a_same_scene_changes_nothing(tmp_path):
    c = Cell(tmp_path, seen="same")
    lic = c.p.commission("sue", "bananas_in_bin")
    assert lic["status"] == "licensed" and lic["scene_reference"].endswith("bananas_in_bin-reference.jpg")
    e = c.p.execute(AI, "bananas_in_bin", {}, requester="olga")
    assert e["decision"] == "allow" and e["scene_check"]["verdict"] == "same"
    assert c.p.licences.data["bananas_in_bin"]["status"] == "licensed"
    assert c.calls[-1][0] == lic["scene_reference"]


def test_a_changed_scene_suspends_the_licence_after_one_run_and_is_explained(tmp_path):
    c = Cell(tmp_path, seen="same")
    c.p.commission("sue", "bananas_in_bin")
    c.seen = "changed"
    e = c.p.execute(AI, "bananas_in_bin", {}, requester="olga")
    lic = c.p.licences.data["bananas_in_bin"]
    assert lic["status"] == "revoked" and lic["revoked_by"] == "scene" and "brick wall" in lic["reason"]
    assert e["revocation"]["action"] == "revoke" and "Cosmos Reason 2" in e["revocation"]["explanation"]
    assert "live runs succeeded" not in e["revocation"]["explanation"]  # it wasn't the success rate
    assert c.p.execute(AI, "bananas_in_bin", {}, requester="olga")["decision"] == "deny"
    checks = [x for x in map(json.loads, open(c.p.audit_path)) if x.get("action") == "scene_check"]
    assert checks and checks[-1]["verdict"] == "changed"


@pytest.mark.parametrize("seen", ["unknown", "same"])
def test_an_unclear_or_same_answer_never_suspends(tmp_path, seen):
    c = Cell(tmp_path, seen="same")
    c.p.commission("sue", "bananas_in_bin")
    c.seen = seen
    for _ in range(3):
        assert c.p.execute(AI, "bananas_in_bin", {}, requester="olga")["decision"] == "allow"
    assert c.p.licences.data["bananas_in_bin"]["status"] == "licensed"


def test_no_reference_or_no_video_means_no_check(tmp_path):
    p = Permit(data_dir=str(tmp_path), clock=lambda: types.SimpleNamespace(tm_hour=14),
               check_scene=lambda r, c: pytest.fail("must not be called"))
    p.rates["bananas_in_bin"]["n17_droid"] = 1.0
    p.commission("sue", "bananas_in_bin")  # the mock runner records no video, so no reference either
    assert "scene_reference" not in p.licences.data["bananas_in_bin"]
    assert p.execute(AI, "bananas_in_bin", {}, requester="olga")["decision"] == "allow"


def test_a_scene_suspension_template_names_cosmos_not_the_success_rate():
    lic = {"status": "revoked", "tier": "supervised", "thr": 0.8, "p": 0.98, "trials": 16, "successes": 16,
           "revoke_below": 0.7, "live": [1], "revoked_by": "scene",
           "reason": "the scene changed since the skill was commissioned (nvidia/Cosmos-Reason2-2B): red background"}
    f = explainer.facts({"action": "revoke", "skill": "bananas_in_bin", "reasons": [lic["reason"]]}, lic)
    text = explainer.offline(f)
    assert "Cosmos Reason 2 compared" in text and "red background" in text and "live runs" not in text
