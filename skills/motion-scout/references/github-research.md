# GitHub evidence and lightweight REST fallback

Use available GitHub MCP/authenticated tools first. Repository search is different
from code search and installation-scoped search may not cover the public internet.
If unavailable, use native web search and the bundled public REST helper:

```powershell
uv run python skills/motion-scout/scripts/github_research.py search "webgpu particles archived:false" --limit 10 --sort updated --window 7 --date-basis pushed
uv run python skills/motion-scout/scripts/github_research.py repo owner/name
```

The query remains task-derived. Repeat useful searches for 30/90-day windows and
established projects; include low-star specialist candidates. Respect API errors,
timeouts and rate-limit instructions. Stop rather than rotating credentials or
retrying around restrictions. Do not transmit a configured token to arbitrary URLs.

For finalists record when available: canonical URL/name, created/updated/pushed
timestamps, stars/forks, archived/disabled status, issues/PR activity, license,
demo/docs URLs, inspected full commit SHA and actual dependency manifests. GitHub's
`open_issues_count` includes pull requests; do not call it unresolved bug count.
`updated_at` is not synonymous with a code commit. Missing fields remain unknown.

Inspect a tree and at least the relevant implementation, lifecycle/frame loop,
dependency file, license and representative example. Pin file citations to the
inspected SHA. A default-branch README can change after the report. Selective
temporary clones belong outside the project; fetch only the code/media needed
for inspection and do not execute their setup scripts.

## Recent momentum

Total stars, repo age, recent pushes and a new release are different signals.
Record them individually. Verify recent star growth using dated snapshots or
reliable historical data with an explicit interval. If none is available,
`recent_growth = unknown` is the correct output.

Optional observations, stored in an ignored caller-chosen path:

```powershell
New-Item -ItemType Directory -Path local/research/motion-scout -Force | Out-Null
uv run python skills/motion-scout/scripts/github_research.py observe owner/name --cache local/research/motion-scout/observations.jsonl
uv run python skills/motion-scout/scripts/github_research.py growth owner/name --cache local/research/motion-scout/observations.jsonl
```

The helper compares actual observations and reports the exact interval and net
star-count change. A one-hour observation is not seven-day growth. Net snapshots
do not count gross new stargazers. One snapshot is insufficient. GitHub's optional
star timestamp API needs the appropriate media type and complete time coverage;
a truncated page of currently retained stargazers is not complete historical
growth, and removed stars complicate reconstruction. Prefer honest unknowns to
large unbounded pagination or invented velocity.

Use [cache rules](cache-policy.md) and keep original metric source/timestamp with
every popularity claim. The helper's search ranking is discovery order, not this
skill's creative/engineering ranking.
