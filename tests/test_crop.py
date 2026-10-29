"""The leaf-diagnosis skill under the trust gate, with a fake vision model and a tiny fake dataset."""
import json
import types

import pytest

from crop import leaf, run


def dataset(tmp_path, per_class=30):
    for crop, labels in leaf.CROPS.items():
        for label, folder in labels.items():
            d = tmp_path / folder
            d.mkdir(parents=True)
            (d / f"ref_{label}.jpg").write_bytes(b"\xff\xd8" + label.encode())
            for i in range(per_class):
                (d / f"{label}_{i:03}.JPG").write_bytes(b"\xff\xd8" + f"{label}:{i}".encode())
    return tmp_path


class FakeVLM:
    """Answers from the query image's bytes (which carry its label here), right `accuracy` of the time."""

    def __init__(self, accuracy=1.0, answer=None):
        self.accuracy, self.answer, self.sent, self.n = accuracy, answer, [], 0
        self.chat = types.SimpleNamespace(completions=types.SimpleNamespace(create=self.create))

    def create(self, **kw):
        self.sent.append(kw)
        import base64
        query = base64.b64decode(kw["messages"][-1]["content"][-1]["image_url"]["url"].split(",", 1)[1])
        truth = query[2:].decode().split(":")[0]
        self.n += 1
        right = (self.n * 61 % 100) < self.accuracy * 100  # spread evenly, not "the first 40 of every 100"
        text = self.answer if self.answer is not None else json.dumps(
            {"diagnosis": truth if right else ("healthy" if truth != "healthy" else "early_blight")})
        return types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=text))])


@pytest.mark.parametrize("text,expect", [
    ('{"diagnosis": "late_blight"}', "late_blight"), ('{"diagnosis": "Late blight"}', "late_blight"),
    ("It looks like early blight.", "early_blight"), ("healthy or late blight?", None),
    ('{"diagnosis": "septoria"}', None), ("", None),
])
def test_answers_are_parsed_strictly(text, expect):
    assert leaf.parse(text, ["healthy", "early_blight", "late_blight"]) == expect


def test_a_perfect_model_is_licensed_for_its_crop_only(tmp_path):
    data = dataset(tmp_path / "data")
    s = run.main(out=tmp_path / "out", client=FakeVLM(1.0), data=data)
    assert s["crops"]["tomato"]["status"] == "licensed" and s["crops"]["pepper"]["status"] == "licensed"
    assert s["scope_checks"]["tomato licence covers tomato"] and not s["scope_checks"]["tomato licence covers pepper"]
    rows = [json.loads(line) for line in open(tmp_path / "out" / "predictions.jsonl")]
    assert rows and all(r["correct"] for r in rows) and {r["crop"] for r in rows} == {"tomato", "pepper"}


def test_a_poor_model_is_refused(tmp_path):
    s = run.main(out=tmp_path / "out", client=FakeVLM(0.4), data=dataset(tmp_path / "data"))
    assert s["crops"]["tomato"]["status"] == "refused" and s["crops"]["pepper"]["status"] == "refused"


def test_running_out_of_photos_is_reported_as_undecided_never_invented(tmp_path):
    s = run.main(out=tmp_path / "out", client=FakeVLM(0.85), data=dataset(tmp_path / "data", per_class=8))
    pepper = s["crops"]["pepper"]
    assert pepper["status"].startswith("undecided") and pepper["trials"] == 16  # every photo, no more


def test_an_unclear_answer_counts_as_wrong(tmp_path):
    s = run.main(out=tmp_path / "out", client=FakeVLM(answer="I can't tell from this photo."),
                 data=dataset(tmp_path / "data"))
    assert s["crops"]["tomato"]["status"] == "refused" and s["crops"]["tomato"]["successes"] == 0


def test_file_names_never_reach_the_model(tmp_path):
    client = FakeVLM(1.0)
    run.main(out=tmp_path / "out", client=client, data=dataset(tmp_path / "data"))
    sent = json.dumps([kw["messages"] for kw in client.sent])
    assert "ref_" not in sent and "_000" not in sent and ".JPG" not in sent and ".jpg" not in sent
    first = client.sent[0]["messages"][0]["content"]
    assert [p["type"] for p in first].count("image_url") == 4  # 3 tomato references + the query
