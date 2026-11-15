import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

import httpx
import pytest
from PIL import Image

from vfx_engine.core.config import EngineConfig
from vfx_engine.core.doctor import run_environment_doctor
from vfx_engine.vision import base


@pytest.fixture
def image(tmp_path):
    path = tmp_path / "contact.jpg"
    Image.new("RGB", (32, 32), "white").save(path)
    return path


def test_factory_preserves_explicit_endpoint():
    analyzer = base.create_vision_analyzer(EngineConfig(
        vision_provider="local", vision_model="test-model", vision_base_url="http://127.0.0.1:1234/v1"))
    assert analyzer.endpoint == "http://127.0.0.1:1234/v1"


@pytest.mark.parametrize("provider", ["none", "noop", "off", "disabled", ""])
def test_disabled_vision_never_connects(monkeypatch, image, provider):
    def client(**_):
        pytest.fail("Disabled vision attempted a connection")
    monkeypatch.setattr(httpx, "Client", client)
    analyzer = base.create_vision_analyzer(EngineConfig(vision_provider=provider, vision_model="model"))
    assert analyzer.analyze(image, [], []).analyzed is False


def test_local_vision_request_and_response_have_inferred_provenance(monkeypatch, image):
    calls = []
    original = httpx.Client

    def respond(request):
        calls.append(request)
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({
            "observations": [{"description": "Bright central area", "evidence": "contact sheet"}],
        })}}]})

    monkeypatch.setattr(httpx, "Client", lambda **kwargs: original(
        transport=httpx.MockTransport(respond), **kwargs))
    analyzer = base.create_vision_analyzer(EngineConfig(
        vision_provider="local", vision_model="cached-model", vision_base_url="http://127.0.0.1:1234/v1"))
    result = analyzer.analyze(image, [], [])
    assert result.analyzed is True
    assert result.status.value == "inferred"
    assert result.semantic_observations[0]["source"] == "inferred"
    assert result.semantic_observations[0]["verified"] is False
    assert str(calls[0].url) == "http://127.0.0.1:1234/v1/chat/completions"
    body = json.loads(calls[0].content)
    assert body["model"] == "cached-model"
    assert body["messages"][1]["content"][1]["image_url"]["url"].startswith("data:image/jpeg;base64,")


@pytest.mark.parametrize("endpoint", ["https://api.example.com/v1", "http://127.0.0.1.evil.test/v1",
                                      "http://user:secret@127.0.0.1/v1", "http://127.0.0.1/v1?key=secret"])
def test_remote_or_credential_urls_are_refused_without_network(monkeypatch, image, endpoint):
    monkeypatch.setattr(httpx, "Client", lambda **_: pytest.fail("Unsafe endpoint contacted"))
    analyzer = base.ConfiguredHTTPVisionAnalyzer("local", "model", endpoint)
    result = analyzer.analyze(image, [], [])
    assert not result.analyzed
    assert result.status.value == "unsupported"
    assert "secret" not in result.note


@pytest.mark.parametrize("failure", ["redirect", "bad-json", "timeout"])
def test_local_vision_failures_do_not_break_cv_or_leak_response(monkeypatch, image, failure):
    original = httpx.Client

    def respond(request):
        if failure == "timeout":
            raise httpx.ReadTimeout("sensitive response text", request=request)
        if failure == "redirect":
            return httpx.Response(302, headers={"Location": "https://outside.example/"})
        return httpx.Response(200, json={"choices": [{"message": {"content": "sensitive invalid JSON"}}]})

    monkeypatch.setattr(httpx, "Client", lambda **kwargs: original(
        transport=httpx.MockTransport(respond), **kwargs))
    result = base.ConfiguredHTTPVisionAnalyzer("local", "model", "http://127.0.0.1:1234/v1").analyze(image, [], [])
    assert not result.analyzed
    assert result.status.value == "error"
    assert "sensitive" not in result.note


def test_doctor_does_not_claim_configuration_is_tested_inference(monkeypatch):
    from vfx_engine.core import doctor
    from vfx_engine.project_analyzer.ae_bridge import bridge_client

    monkeypatch.setattr(doctor, "_run_cmd_probe", lambda *_: (True, "stub"))
    monkeypatch.setattr(bridge_client, "probe_live_ae_bridges", lambda _: {})
    result = run_environment_doctor(EngineConfig(
        vision_provider="local", vision_model="model", vision_base_url="http://127.0.0.1:1234/v1"))["vision"]
    assert result["configured"] is True
    assert result["implementation"] == "local-openai-compatible"
    assert result["connection_tested"] is False


def test_loopback_http_fixture_receives_images_and_ignores_proxy(monkeypatch, image):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            requests.append((self.path, json.loads(self.rfile.read(int(self.headers["Content-Length"])))))
            body = json.dumps({"choices": [{"message": {"content": '{"observations":[]}'}}]}).encode()
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:1")
    monkeypatch.setenv("NO_PROXY", "")
    try:
        endpoint = f"http://127.0.0.1:{server.server_port}/v1"
        result = base.ConfiguredHTTPVisionAnalyzer("local", "fixture-only", endpoint).analyze(image, [], [])
        assert result.analyzed and result.semantic_observations == []
        assert requests[0][0] == "/v1/chat/completions"
        assert requests[0][1]["model"] == "fixture-only"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


@pytest.mark.parametrize("kind", ["oversized", "malformed", "missing"])
def test_invalid_evidence_is_nonfatal_and_never_sent(monkeypatch, tmp_path, kind):
    path = tmp_path / "bad.jpg"
    if kind == "oversized":
        path.write_bytes(b"x" * (4 * 1024 * 1024 + 1))
    elif kind == "malformed":
        path.write_bytes(b"not an image")
    monkeypatch.setattr(httpx, "Client", lambda **_: pytest.fail("Invalid evidence was sent"))
    result = base.ConfiguredHTTPVisionAnalyzer("local", "model", "http://127.0.0.1:1234/v1").analyze(path, [], [])
    assert result.status.value == "error" and not result.analyzed


def test_response_budget_is_enforced(monkeypatch, image):
    original = httpx.Client
    monkeypatch.setattr(httpx, "Client", lambda **kwargs: original(
        transport=httpx.MockTransport(lambda _: httpx.Response(200, content=b"x" * (2 * 1024 * 1024 + 1))),
        **kwargs))
    result = base.ConfiguredHTTPVisionAnalyzer("local", "model", "http://127.0.0.1:1234/v1").analyze(image, [], [])
    assert result.status.value == "error" and not result.analyzed


@pytest.mark.parametrize("endpoint", ["http://localhost:1234/v1/", "http://[::1]:1234"])
def test_local_endpoint_normalization(endpoint):
    expected = "http://[::1]:1234/v1/chat/completions" if "::1" in endpoint else "http://127.0.0.1:1234/v1/chat/completions"
    assert base.local_vision_url(endpoint) == expected


def test_semantic_observations_reach_markdown_as_unverified_data():
    from vfx_engine.reports.video_reporter import render_video_markdown
    from vfx_engine.schemas.video_schema import (
        SamplingSummarySchema,
        VideoAnalysisResult,
        VideoMetadataSchema,
        VisionAnalysisSummarySchema,
    )

    result = VideoAnalysisResult(
        analysis_id="test", analyzed_at="2026-11-15", rerun_command="test",
        metadata=VideoMetadataSchema(file_path="fixture.mp4", file_name="fixture.mp4", file_size_bytes=1,
            sha256="fixture", container_format="mp4", video_codec="h264", width=32, height=32,
            nominal_fps=30, average_fps=30, duration_seconds=1, frame_count=30),
        sampling=SamplingSummarySchema(strategy="fixture", total_video_frames=30, analyzed_frames_count=30,
            coverage_ratio=1, contact_sheet_path="contact.jpg", evidence_frames_dir="evidence"),
        vision_analysis=VisionAnalysisSummarySchema(provider="local", model="fixture", status="inferred",
            analyzed=True, semantic_observations=[{"description": "Bright region\n```", "evidence": "frame 1",
                                                  "source": "inferred", "verified": False}]))
    report = render_video_markdown(result)
    assert "Model observations (inferred, unverified)" in report
    assert "Bright region" in report and '"verified": false' in report
    assert report.count("```") == 2
