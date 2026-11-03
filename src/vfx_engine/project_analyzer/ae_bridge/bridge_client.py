"""Read-only After Effects Bridge client (Method B).

Supports querying a running After Effects instance via:
1. JUNKDOGE `after-effects-mcp` Streamable HTTP endpoint (`http://127.0.0.1:11488/mcp`)
2. Solomon `aftereffects-mcp` AE MCP Bridge (`http://127.0.0.1:7788/call` with `~/.ae-mcp-bridge.json` token)

Guarantees read-only behavior: never dispatches write operations, never modifies
the user's original `.aep` file, and transparently reports when live AE is not active.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import httpx

from ...core.config import EngineConfig, discover_after_effects_installations
from ...core.logging import get_logger
from ...core.safety import compute_sha256

logger = get_logger("project_analyzer.ae_bridge")


def verify_live_project_identity(
    target_path: Path,
    target_sha256: str,
    live_payload: Any,
) -> tuple[bool, str, str]:
    """Verify that a live AE bridge payload is structurally valid and matches the target project identity.

    Returns:
        Tuple of `(is_valid, warning_code, explanation)`.
    """
    if not isinstance(live_payload, dict):
        return (
            False,
            "LIVE_BRIDGE_INVALID_RESPONSE",
            "Live AE Bridge returned a non-object payload.",
        )
    if live_payload.get("ok") is False or live_payload.get("error"):
        err_msg = live_payload.get("error") or "unsuccessful response"
        return (
            False,
            "LIVE_BRIDGE_INVALID_RESPONSE",
            f"Live AE Bridge reported error: {err_msg}",
        )
    if not isinstance(live_payload.get("compositions"), list):
        return (
            False,
            "LIVE_BRIDGE_INVALID_RESPONSE",
            "Live AE Bridge payload is missing a valid 'compositions' list.",
        )

    raw_live_path = (
        live_payload.get("project_file")
        or live_payload.get("file_path")
        or live_payload.get("file")
    )
    if (
        not isinstance(raw_live_path, str)
        or not raw_live_path.strip()
        or raw_live_path.strip().lower() == "unsaved"
    ):
        return (
            False,
            "LIVE_BRIDGE_IDENTITY_MISSING",
            "Live AE Bridge payload does not establish an open project file path matching the analyzed input.",
        )

    live_sha256 = live_payload.get("sha256") or live_payload.get("project_sha256")
    if live_sha256 is not None and str(live_sha256).strip().lower() != target_sha256.lower():
        return (
            False,
            "LIVE_BRIDGE_PROJECT_MISMATCH",
            f"Live AE project SHA-256 does not match analyzed file '{target_path.name}'.",
        )

    try:
        target_norm = os.path.normcase(str(target_path.resolve()))
        live_resolved = Path(raw_live_path.strip()).resolve()
        live_norm = os.path.normcase(str(live_resolved))
    except Exception as exc:
        return (
            False,
            "LIVE_BRIDGE_IDENTITY_MISSING",
            f"Could not resolve live AE project file path '{raw_live_path}': {exc}",
        )

    if live_norm != target_norm:
        return (
            False,
            "LIVE_BRIDGE_PROJECT_MISMATCH",
            f"Live AE has '{raw_live_path}' open, which does not match analyzed project '{target_path}'.",
        )

    if live_resolved.exists():
        try:
            disk_sha = compute_sha256(live_resolved)
            if disk_sha.lower() != target_sha256.lower():
                return (
                    False,
                    "LIVE_BRIDGE_PROJECT_MISMATCH",
                    f"Live AE project file hash on disk differs from analyzed '{target_path.name}'.",
                )
        except OSError:
            pass

    return True, "", "Verified canonical project file identity."


def probe_live_ae_bridges(config: EngineConfig | None = None) -> dict[str, Any]:
    """Non-intrusively check whether JUNKDOGE ae-mcp or Solomon AE MCP Bridge is reachable."""
    cfg = config or EngineConfig()
    status: dict[str, Any] = {
        "junkdoge_ae_mcp": {"url": cfg.ae_mcp_junkdoge_url, "reachable": False, "detail": ""},
        "solomon_ae_bridge": {
            "url": f"http://127.0.0.1:{cfg.ae_mcp_solomon_port}/call",
            "reachable": False,
            "detail": "",
        },
        "any_live_bridge_online": False,
    }

    # 1. Probe JUNKDOGE ae-mcp (:11488)
    try:
        with httpx.Client(timeout=1.5) as client:
            resp = client.post(
                cfg.ae_mcp_junkdoge_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {"name": "ae_status", "arguments": {"depth": "ping"}},
                },
            )
            if resp.status_code < 500:
                status["junkdoge_ae_mcp"]["reachable"] = True
                status["junkdoge_ae_mcp"]["detail"] = f"HTTP {resp.status_code}"
    except Exception as exc:
        status["junkdoge_ae_mcp"]["detail"] = f"Offline ({type(exc).__name__})"

    # 2. Probe Solomon aftereffects-mcp (:7788)
    token_file = Path.home() / ".ae-mcp-bridge.json"
    token = ""
    if token_file.exists():
        try:
            token = json.loads(token_file.read_text(encoding="utf-8")).get("token", "")
        except Exception:
            token = ""
    try:
        headers = {"X-AE-Bridge-Token": token} if token else {}
        with httpx.Client(timeout=1.5) as client:
            resp = client.post(
                f"http://127.0.0.1:{cfg.ae_mcp_solomon_port}/call",
                headers=headers,
                json={"fn": "get_project_info", "args": {}},
            )
            if resp.status_code == 200:
                status["solomon_ae_bridge"]["reachable"] = True
                status["solomon_ae_bridge"]["detail"] = "Connected"
            else:
                status["solomon_ae_bridge"]["detail"] = f"HTTP {resp.status_code}"
    except Exception as exc:
        status["solomon_ae_bridge"]["detail"] = f"Offline ({type(exc).__name__})"

    status["any_live_bridge_online"] = bool(
        status["junkdoge_ae_mcp"]["reachable"] or status["solomon_ae_bridge"]["reachable"]
    )
    return status


class AfterEffectsReadOnlyBridge:
    """Read-only adapter for inspecting live After Effects state via MCP bridges or ExtendScript."""

    FORBIDDEN_JSX_PATTERNS = (
        ".save(",
        ".saveWithDialog(",
        ".close(",
        "app.open(",
        ".setValue(",
        ".setValueAtTime(",
        ".setValuesAtTimes(",
        ".remove(",
        ".addComp(",
        ".addSolid(",
        ".addNull(",
        ".addText(",
        ".addShape(",
        ".addCamera(",
        ".addLight(",
        ".addProperty(",
        "system.callSystem(",
    )

    def __init__(self, config: EngineConfig | None = None) -> None:
        self.config = config or EngineConfig()
        self.jsx_script_path = self.config.ae_scripts_dir / "vfx_readonly_extract.jsx"

    def validate_script_is_readonly(self, jsx_code: str) -> None:
        """Raise PermissionError if the ExtendScript payload contains any forbidden write/mutation API."""
        for pat in self.FORBIDDEN_JSX_PATTERNS:
            if pat in jsx_code:
                raise PermissionError(
                    f"Forbidden write/mutation ExtendScript pattern '{pat}' blocked by Read-Only Phase 1 policy."
                )

    def is_available(self) -> tuple[bool, str]:
        """Return (is_online, human_readable_status)."""
        probes = probe_live_ae_bridges(self.config)
        if probes["junkdoge_ae_mcp"]["reachable"]:
            return True, f"Connected via JUNKDOGE ae-mcp ({self.config.ae_mcp_junkdoge_url})"
        if probes["solomon_ae_bridge"]["reachable"]:
            return True, f"Connected via Solomon AE MCP Bridge (127.0.0.1:{self.config.ae_mcp_solomon_port})"

        ae_installs = discover_after_effects_installations()
        if ae_installs:
            names = ", ".join(i["name"] for i in ae_installs)
            return (
                False,
                f"After Effects is installed ({names}), but no live MCP CEP bridge panel "
                "is currently open/listening on ports 11488 or 7788. "
                "Live bridge marked as UNTESTED in this run (using offline parser).",
            )
        return (
            False,
            "After Effects is not installed and no live MCP bridge is listening. "
            "Live bridge marked as UNTESTED.",
        )

    def fetch_live_project_state(self) -> dict[str, Any]:
        """Execute a strictly read-only inspection against an active AE MCP bridge."""
        probes = probe_live_ae_bridges(self.config)
        if not probes["any_live_bridge_online"]:
            raise RuntimeError(
                "No live After Effects MCP bridge is currently listening on 127.0.0.1:11488 or 127.0.0.1:7788."
            )

        jsx_code = self.jsx_script_path.read_text(encoding="utf-8") + "\nJSON.stringify(VFXReadonlyExtractor.extractProject());"

        if probes["junkdoge_ae_mcp"]["reachable"]:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(
                    self.config.ae_mcp_junkdoge_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 10,
                        "method": "tools/call",
                        "params": {
                            "name": "ae_exec",
                            "arguments": {"code": jsx_code},
                        },
                    },
                )
                resp.raise_for_status()
                payload = resp.json()
                raw_res = payload.get("result", {})
                if isinstance(raw_res, dict) and "result" in raw_res:
                    return json.loads(raw_res["result"])
                return raw_res

        # Solomon AE MCP Bridge (:7788)
        token_file = Path.home() / ".ae-mcp-bridge.json"
        token = json.loads(token_file.read_text(encoding="utf-8")).get("token", "") if token_file.exists() else ""
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"http://127.0.0.1:{self.config.ae_mcp_solomon_port}/call",
                headers={"X-AE-Bridge-Token": token},
                json={"fn": "get_project_info", "args": {}},
            )
            resp.raise_for_status()
            return resp.json().get("result", {})

    def export_preview_frame(
        self, comp_name: str, time_seconds: float, output_png_path: Path
    ) -> dict[str, Any]:
        """Request a single read-only preview frame PNG from a live AE instance."""
        probes = probe_live_ae_bridges(self.config)
        if not probes["any_live_bridge_online"]:
            return {
                "ok": False,
                "status": "unavailable",
                "error": "Live After Effects MCP bridge is not running.",
            }
        escaped_path = str(output_png_path.resolve()).replace("\\", "/")
        escaped_comp = comp_name.replace('"', '\\"')
        jsx_code = (
            self.jsx_script_path.read_text(encoding="utf-8")
            + f'\nJSON.stringify(VFXReadonlyExtractor.exportPreviewFrame("{escaped_comp}", {float(time_seconds)}, "{escaped_path}"));'
        )
        if probes["junkdoge_ae_mcp"]["reachable"]:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(
                    self.config.ae_mcp_junkdoge_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 11,
                        "method": "tools/call",
                        "params": {"name": "ae_exec", "arguments": {"code": jsx_code}},
                    },
                )
                resp.raise_for_status()
                return resp.json()
        return {"ok": False, "status": "unsupported", "error": "Preview export requires JUNKDOGE ae-mcp"}
