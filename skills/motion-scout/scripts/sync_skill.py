"""Create or check Codex/Claude discovery links to a repo-owned VFXLens skill."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


def create_link(destination: Path, canonical: Path) -> None:
    if os.name == "nt":
        # Encoded literal paths avoid shell metacharacters and require no symlink privilege.
        def literal(path):
            return "'" + str(path).replace("'", "''") + "'"
        script = ("$ErrorActionPreference='Stop'; New-Item -ItemType Junction -Path "
                  + literal(destination) + " -Target " + literal(canonical) + " | Out-Null")
        encoded = base64.b64encode(script.encode("utf-16le")).decode("ascii")
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
            capture_output=True, encoding="utf-8", errors="replace", check=False,
        )
        if result.returncode:
            raise OSError(f"Junction creation failed: {result.stderr.strip()}")
    else:
        destination.symlink_to(os.path.relpath(canonical, destination.parent), target_is_directory=True)


SOURCES = {"motion-scout": "skills/motion-scout", "vfxlens": "skills/vfxlens",
           "remotion-3d-director": ".agents/skills/remotion-3d-director", "longform-2d": "skills/longform-2d"}


def synchronize(project: Path, check: bool = False, skill: str = "motion-scout") -> dict:
    project = project.resolve(strict=True)
    if skill not in SOURCES:
        raise ValueError("Unknown repo-owned skill")
    canonical = project / SOURCES[skill]
    source = canonical / "SKILL.md"
    if not (project / "AGENTS.md").is_file() or not (project / "studio/package.json").is_file():
        raise ValueError("Not a VFXLens root: AGENTS.md and studio/package.json are required")
    if not source.is_file() or f"name: {skill}\n" not in source.read_text(encoding="utf-8"):
        raise ValueError(f"Canonical {SOURCES[skill]}/SKILL.md is missing or has the wrong name")
    canonical = canonical.resolve(strict=True)
    targets = [("Codex", project / ".agents/skills" / skill),
               ("Claude Code", project / ".claude/skills" / skill)]
    # Preflight both paths before creating either; never replace another task's folder.
    for _, destination in targets:
        if os.path.lexists(destination):
            try:
                matches = destination.resolve(strict=True) == canonical
            except (OSError, RuntimeError):
                matches = False
            if not matches:
                raise ValueError(f"Existing unrelated/stale destination; left untouched: {destination}")
    expected_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    rows = []
    for client, destination in targets:
        created = False
        if not os.path.lexists(destination) and not check:
            destination.parent.mkdir(parents=True, exist_ok=True)
            create_link(destination, canonical)
            created = True
        linked = destination.exists() and destination.resolve(strict=True) == canonical
        same_content = linked and hashlib.sha256((destination / "SKILL.md").read_bytes()).hexdigest() == expected_hash
        rows.append({"client": client, "path": str(destination), "created": created,
                     "linked": linked, "same_content": same_content})
    return {"ok": all(row["linked"] and row["same_content"] for row in rows),
            "canonical": str(canonical), "skill_sha256": expected_hash, "clients": rows,
            "scope": "Filesystem discovery paths/content; interactive client selection is not tested"}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--check", action="store_true", help="Read-only verification; create nothing")
    parser.add_argument("--skill", choices=SOURCES, default="motion-scout")
    args = parser.parse_args(argv)
    try:
        result = synchronize(args.project_root, args.check, args.skill)
    except (OSError, ValueError, RuntimeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=True))
        return 1
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
