import json
import shutil
import subprocess
from unittest.mock import Mock

import httpx
import pytest

from vfx_engine.project_analyzer.ae_bridge import bridge_client as module


@pytest.fixture
def bridge(monkeypatch):
    requests = []
    original_client = httpx.Client

    def respond(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json={"ok": True})

    monkeypatch.setattr(module, "probe_live_ae_bridges", lambda _: {
        "any_live_bridge_online": True, "junkdoge_ae_mcp": {"reachable": True},
    })
    monkeypatch.setattr(module.httpx, "Client", lambda **kwargs: original_client(
        transport=httpx.MockTransport(respond), **kwargs))
    instance = module.AfterEffectsReadOnlyBridge()
    instance.validate_script_is_readonly = Mock(wraps=instance.validate_script_is_readonly)
    return instance, requests


def test_preview_transmits_hostile_name_as_data_and_checks_script(bridge, tmp_path):
    instance, requests = bridge
    name = 'quote\\"; globalThis.injected = true; //\n\u2028 tiếng Việt'
    target = tmp_path / "preview.png"
    instance.export_preview_frame(name, 0.5, target)
    script = requests[0]["params"]["arguments"]["code"]
    instance.validate_script_is_readonly.assert_called_once_with(script)
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is needed for the JSX sandbox regression check")
    harness = r'''
const vm = require('node:vm');
const input = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
let captured;
function CompItem() { this.name = input.name; this.duration = 2; }
const comp = new CompItem();
comp.saveFrameToPng = (time, file) => { captured = [comp.name, time, file.fsName]; };
function File(path) { this.fsName = path; this.name = path.split('/').pop(); this.exists = false; }
const context = {CompItem, File, app: {project: {numItems: 1, item: () => comp}}};
vm.runInNewContext(input.script, context, {timeout: 1000});
console.log(JSON.stringify({captured, injected: context.injected === true}));
'''
    result = subprocess.run([node, "-e", harness], input=json.dumps({"script": script, "name": name}),
                            capture_output=True, text=True, encoding="utf-8", timeout=5, check=True)
    output = json.loads(result.stdout)
    assert output == {"captured": [name, 0.5, target.resolve().as_posix()], "injected": False}


@pytest.mark.parametrize("time", [-1, float("nan"), float("inf")])
def test_preview_rejects_invalid_time_before_transport(bridge, tmp_path, time):
    instance, requests = bridge
    with pytest.raises(ValueError):
        instance.export_preview_frame("Scene", time, tmp_path / "preview.png")
    assert requests == []


@pytest.mark.parametrize("filename,existing", [("original.mp4", True), ("existing.png", True),
                                              ("not-png.txt", False)])
def test_preview_preserves_existing_files_and_requires_png(bridge, tmp_path, filename, existing):
    instance, requests = bridge
    target = tmp_path / filename
    if existing:
        target.write_bytes(b"original")
    with pytest.raises(ValueError):
        instance.export_preview_frame("Scene", 0, target)
    assert requests == []
    if existing:
        assert target.read_bytes() == b"original"


def test_preview_validates_trusted_script_before_dispatch(bridge, tmp_path):
    instance, requests = bridge
    script = tmp_path / "modified.jsx"
    script.write_text("app.project.save(new File('original.aep'));", encoding="utf-8")
    instance.jsx_script_path = script
    with pytest.raises(PermissionError):
        instance.export_preview_frame("Scene", 0, tmp_path / "preview.png")
    assert requests == []


def test_preview_rejects_linked_destination_without_touching_reference(bridge, tmp_path):
    instance, requests = bridge
    source = tmp_path / "reference.mp4"
    source.write_bytes(b"untouched reference")
    alias = tmp_path / "preview.png"
    alias.hardlink_to(source)
    with pytest.raises(ValueError):
        instance.export_preview_frame("Scene", 0, alias)
    assert source.read_bytes() == b"untouched reference"
    assert requests == []


def test_preview_rejects_missing_parent_before_transport(bridge, tmp_path):
    instance, requests = bridge
    with pytest.raises(ValueError):
        instance.export_preview_frame("Scene", 0, tmp_path / "missing/preview.png")
    assert requests == []
