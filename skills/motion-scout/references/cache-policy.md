# Optional research memory

Use a small ignored directory such as `local/research/motion-scout/`. Keep repo
URLs, technique tags, category, inspected SHA/version, public metadata source,
observed timestamp, compatibility/suitability notes and historical observations
only when actually measured. A report can carry these fields without a database.
The bundled REST helper uses append-only JSONL observations when explicitly asked.

Preserve observation timestamps. Refresh current metadata with a new entry rather
than relabelling old data as fresh. Do not store binaries, repositories, videos,
dependencies, secrets or full website mirrors in the cache. Bound API requests
and keep only relevant source evidence.

Staleness policy:

- Every invocation performs live research when access is available; cached results
  are leads/local history, never a substitute.
- For “latest/trending”, refresh relevant metrics/access and seek new candidates
  on that run, even if a snapshot is younger than a day.
- For ordinary comparisons, metadata older than 24 hours and technical/license
  notes older than seven days are stale leads. Recheck selected units at their
  actual commit before integration regardless of these convenience thresholds.
- A source pinned to an old SHA remains valid evidence about that SHA, not current
  maintenance, stars, licensing at a new revision or backend compatibility.
- On network failure, report offline/stale evidence and its age. Missing historical
  growth remains unknown; never backfill a fabricated baseline.

Project-specific acceptance decisions and private asset paths belong in the
production/research checkpoint, not a public skill example. Manual cache cleanup
must stay scoped to that cache; link setup and research helpers never delete
existing skill directories or user media.
