"""Check authored Markdown paths and GitHub-style section anchors, not downloaded skills."""
import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def section_ids(text):
    counts = Counter()
    result = set(re.findall(r'<a\s+(?:id|name)=["\']([^"\']+)', text))
    for line in text.splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*$", line)
        if match:
            slug = re.sub(r"[^\w\- ]", "", match[1].lower()).replace(" ", "-")
            result.add(slug if not counts[slug] else f"{slug}-{counts[slug]}")
            counts[slug] += 1
    return result


def test_authored_markdown_links_and_sections_resolve():
    files = [ROOT / name for name in ["README.md", "AGENTS.md", "CLAUDE.md"]]
    for folder in ["library", "docs", "workflows", "skills", ".agents/skills/remotion-3d-director"]:
        files.extend((ROOT / folder).rglob("*.md"))
    failures = []
    for file in files:
        text = re.sub(r"```.*?```", "", file.read_text(encoding="utf-8"), flags=re.S)
        for link in re.findall(r"\]\(([^)]+)\)", text):
            if "://" in link or link.startswith("mailto:") or "<" in link:
                continue
            path, _, fragment = unquote(link).partition("#")
            target = (file.parent / path).resolve() if path else file
            if not target.is_file():
                failures.append(f"{file.relative_to(ROOT)}: missing {link}")
            elif fragment and target.suffix == ".md" and fragment not in section_ids(target.read_text(encoding="utf-8")):
                failures.append(f"{file.relative_to(ROOT)}: missing section {link}")
    assert not failures, "\n".join(failures)
