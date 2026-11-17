"""2D long-form toolkit: silent draft voice -> timeline/manifest, run in an isolated fake repo."""
import json
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parents[1] / "studio/tools/longform-2d"
pytestmark = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="FFmpeg is required")


def run(script: str, cwd: Path, *args: str) -> None:
    subprocess.run([sys.executable, str(TOOL / script), *args], cwd=cwd, check=True, capture_output=True, text=True)


def test_silent_draft_builds_a_consistent_manifest(tmp_path: Path) -> None:
    (tmp_path / "studio").mkdir()
    (tmp_path / "studio/package.json").write_text("{}", encoding="utf-8")
    prod = tmp_path / "local/productions/test-ep"
    prod.mkdir(parents=True)
    script = json.loads((TOOL / "examples/demo-2d/script.json").read_text(encoding="utf-8"))
    script["music"] = {"src": "music.wav", "volume": 0.4, "duck": 0.5}
    (prod / "script.json").write_text(json.dumps(script), encoding="utf-8")
    with wave.open(str(prod / "music.wav"), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(48000)
        f.writeframes(b"\0\0" * 48000)
    (prod / "sfx.wav").write_bytes((prod / "music.wav").read_bytes())
    (prod / "sfx.json").write_text(json.dumps([
        {"src": "sfx.wav", "at": "l2#1", "note": "pop"},
        {"src": "sfx.wav", "at": "s2", "offset": 0.1, "note": "boom"},
    ]), encoding="utf-8")

    run("voice_lines.py", prod, "--silent")
    run("build.py", prod)

    m = json.loads((tmp_path / "studio/public/media/test-ep/longform.json").read_text(encoding="utf-8"))
    scenes, lines = m["scenes"], {line["id"]: line for line in m["lines"]}
    # scenes tile the whole timeline with no gap or overlap
    assert scenes[0]["from"] == 0
    for a, b in zip(scenes, scenes[1:]):
        assert a["from"] + a["durationInFrames"] == b["from"]
    assert scenes[-1]["from"] + scenes[-1]["durationInFrames"] == m["durationInFrames"]
    # every line sits inside its scene, with one mouth state per frame and words inside the line
    by_id = {s["id"]: s for s in scenes}
    for line in lines.values():
        s = by_id[line["scene"]]
        assert s["from"] <= line["from"] and line["from"] + line["durationInFrames"] <= s["from"] + s["durationInFrames"]
        assert len(line["mouth"]) == line["durationInFrames"]
        assert all(line["from"] <= w["from"] < w["to"] <= line["from"] + line["durationInFrames"] + 1 for w in line["words"])
    # SFX anchors: word 1 of l2, and 0.1 s after scene s2 starts
    assert m["sfx"][0]["from"] == lines["l2"]["words"][1]["from"]
    assert m["sfx"][1]["from"] == by_id["s2"]["from"] + 3
    # music is ducked under speech and silent inside the card scene
    vols = m["music"]["volumes"]
    card = by_id["s2"]
    assert max(vols[card["from"]:card["from"] + card["durationInFrames"]]) == 0
    assert vols[lines["l1"]["from"] + 20] < 0.4
