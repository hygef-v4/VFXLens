"""High-level orchestrator for After Effects Project Analysis (.aep / .aepx)."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from ..core.config import EngineConfig
from ..core.logging import get_logger
from ..core.safety import validate_project_file_safety
from ..schemas.common import AnalysisWarning, DataAvailabilityStatus
from ..schemas.project_schema import ProjectAnalysisResult
from .ae_bridge.bridge_client import AfterEffectsReadOnlyBridge, verify_live_project_identity
from .normalizer.comparator import compare_offline_and_live
from .parsers.aepx_parser import parse_aepx_project
from .parsers.py_aep_parser import parse_aep_with_py_aep

logger = get_logger("project_analyzer.analyzer")


def _make_analysis_id(prefix: str, file_path: Path) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", file_path.stem).strip("_")[:32] or "project"
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{slug}_{ts}"


def analyze_ae_project(
    project_path: Path | str,
    config: EngineConfig | None = None,
    use_ae_bridge: bool = False,
    analysis_id: str | None = None,
) -> ProjectAnalysisResult:
    """Analyze an After Effects `.aep` or `.aepx` project file in read-only mode."""
    cfg = config or EngineConfig()
    path = Path(project_path).resolve()
    fmt, _, _ = validate_project_file_safety(path, max_size_mb=cfg.max_project_size_mb)

    aid = analysis_id or _make_analysis_id("proj", path)
    rerun_cmd = f'vfx analyze-project "{path}"' + (" --use-ae-bridge" if use_ae_bridge else "")

    logger.info("Analyzing After Effects project: %s (format=%s)", path.name, fmt)

    if fmt == "aepx":
        result = parse_aepx_project(path, analysis_id=aid, rerun_command=rerun_cmd)
    else:
        result = parse_aep_with_py_aep(path, analysis_id=aid, rerun_command=rerun_cmd)

    # Check live bridge status transparently
    bridge = AfterEffectsReadOnlyBridge(cfg)
    bridge_online, bridge_note = bridge.is_available()
    result.live_bridge_status_note = bridge_note

    if use_ae_bridge:
        if bridge_online:
            try:
                live_payload = bridge.fetch_live_project_state()
                is_valid, warn_code, warn_msg = verify_live_project_identity(
                    path, result.metadata.sha256, live_payload
                )
                if is_valid:
                    result.live_bridge_tested = True
                    result.extraction_method = "hybrid_compared"
                    result.comparison_with_live = compare_offline_and_live(result, live_payload)
                else:
                    result.live_bridge_tested = False
                    result.comparison_with_live = None
                    result.warnings.append(
                        AnalysisWarning(
                            code=warn_code,
                            message=f"{warn_msg} Returning offline parse result.",
                            status=DataAvailabilityStatus.UNAVAILABLE,
                        )
                    )
            except Exception as exc:
                result.live_bridge_tested = False
                result.comparison_with_live = None
                result.warnings.append(
                    AnalysisWarning(
                        code="LIVE_BRIDGE_QUERY_FAILED",
                        message=f"Live AE Bridge query failed ({exc}); returning offline parse result.",
                        status=DataAvailabilityStatus.UNAVAILABLE,
                    )
                )
        else:
            result.live_bridge_tested = False
            result.warnings.append(
                AnalysisWarning(
                    code="LIVE_BRIDGE_NOT_RUNNING",
                    message=bridge_note,
                    status=DataAvailabilityStatus.UNAVAILABLE,
                )
            )

    return result
