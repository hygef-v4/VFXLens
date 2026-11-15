# Tool capabilities and cross-agent setup

## One source, two discovery paths

Canonical instructions/resources live in `skills/motion-scout/`. Run from the
repo root with Python 3.11+ (or `uv run python`):

```powershell
uv run python skills/motion-scout/scripts/sync_skill.py
uv run python skills/motion-scout/scripts/sync_skill.py --check
```

The helper creates missing project `.agents/skills/motion-scout` and
`.claude/skills/motion-scout` links. Windows uses PowerShell directory junctions;
POSIX uses directory symlinks. Both resolve to the canonical folder, so changes
are immediate and cannot drift. Existing unrelated directories/links are refused,
not replaced. After moving a checkout, inspect stale links rather than deleting
their targets. A filesystem without link support reports a blocker; it does not
silently introduce another manual copy.

From an unrelated working directory, use the absolute script path or
`--project-root <checkout>`. The script checks the root and canonical skill before
creating links. It can be run repeatedly and `--check` performs no writes.

Codex: invoke `$motion-scout`. Claude Code: invoke `/motion-scout` or explicitly
ask to use the project skill. Refresh/restart discovery when a new folder is not
yet listed. Link/content validation establishes that both paths can load the same
instructions; it does not prove a new interactive session has selected the skill.

The same tested helper can register the other two repo-owned skills without
copying or moving their canonical sources:

```powershell
uv run python skills/motion-scout/scripts/sync_skill.py --skill vfxlens
uv run python skills/motion-scout/scripts/sync_skill.py --skill remotion-3d-director
```

Add `--check` for read-only verification. Director's existing `.agents/skills/`
folder remains its canonical source; only its missing Claude link is created.

## Detect tools per run

Record a small capability table: available, tested, failed/unavailable, exact
fallback and evidence timestamp. Tool names vary between Codex and Claude:

1. Inspect the runtime's available GitHub MCP tools. Prefer a repository search,
   metadata, contents/tree and commit reader. A listed tool is not a tested
   connection; make one relevant read-only call before reporting it operational.
2. Check existing authenticated GitHub API/CLI capability. Credentials remain in
   host configuration or `GH_TOKEN` / `GITHUB_TOKEN`; never echo them. Do not request
   broad credentials when public read-only research can proceed without them.
3. Discover native web search/fetch and any browser surface. Prefer primary
   project/docs pages for implementation claims. Use browser access only when
   needed to inspect a demo or a page that text fetch cannot show.
4. Check whether authorized X search/API exists. Otherwise test indexed public
   posts with search/fetch and label the result accurately. No X capability is a
   valid limitation; it does not block GitHub research.
5. Look for `git`, Python and optionally `gh`. The bundled GitHub helper is a
   standard-library REST fallback, not an MCP replacement or authentication setup.

Do not assume every client has the same tools, keys, GPU or browser. If all
network paths fail, produce a clearly labelled blocked/offline report using local
evidence and the missing capability; do not report it as live research.

The checked-in [sample run](../examples/live-research-2026-11-15.md) records the
creation-time test. It is an example of reporting, not a seed list or evidence of
today's access. On every real invocation, detect capabilities again.

## Repeatable local checks

```powershell
uv run python -m unittest discover -s skills/motion-scout/scripts -p 'test_*.py' -v
uv run ruff check skills/motion-scout/scripts
uv run python skills/motion-scout/scripts/sync_skill.py --check
```

Unit tests mock network responses; they do not establish live access. Run a
brief-specific live `search` separately, then report any timeout/rate restriction.
Research-only validation inspects metadata, sources and demos without running an
upstream installer or rendering unreviewed code.
