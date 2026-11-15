"""Small, read-only GitHub REST helper for motion-scout research."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

API = "https://api.github.com"
TIMEOUT = 15
MAX_BODY = 2 * 1024 * 1024
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class ResearchError(Exception):
    pass


class _RejectRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def urlopen(request: Request, timeout: int):
    """Open without following redirects, so Authorization stays on the fixed API host."""
    return build_opener(_RejectRedirects()).open(request, timeout=timeout)


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso_now() -> str:
    return utc_now().isoformat().replace("+00:00", "Z")


def normalize_repo(value: str) -> str:
    value = value.strip()
    if "://" in value:
        parsed = urlparse(value)
        if parsed.scheme != "https" or parsed.netloc.lower() not in {"github.com", "www.github.com"}:
            raise ResearchError("repository URL must use https://github.com")
        value = parsed.path.strip("/")
    value = value.removesuffix(".git").strip("/")
    if not REPO_RE.fullmatch(value) or value.count("/") != 1:
        raise ResearchError("repository must be owner/name or a GitHub repository URL")
    if any(part in {".", ".."} for part in value.split("/")):
        raise ResearchError("repository owner and name must be valid path segments")
    return value


def _request(path: str, params: dict[str, str] | None = None) -> dict:
    url = f"{API}{path}"
    if params:
        url += "?" + urlencode(params)
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "VFXLens-motion-scout"}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=TIMEOUT) as response:
            raw = response.read(MAX_BODY + 1)
    except HTTPError as exc:
        retry = exc.headers.get("Retry-After")
        remaining = exc.headers.get("X-RateLimit-Remaining")
        reset = exc.headers.get("X-RateLimit-Reset")
        exc.close()
        details = [f"GitHub returned HTTP {exc.code}"]
        if retry:
            details.append(f"Retry-After: {retry}")
        if remaining:
            details.append(f"rate remaining: {remaining}")
        if reset:
            details.append(f"rate reset (UTC epoch): {reset}")
        if exc.code in (403, 429):
            details.append("stopped without retrying")
        raise ResearchError("; ".join(details)) from None
    except (URLError, TimeoutError, OSError) as exc:
        raise ResearchError(f"GitHub request failed: {type(exc).__name__}") from None
    if len(raw) > MAX_BODY:
        raise ResearchError(f"GitHub response exceeded {MAX_BODY} bytes")
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ResearchError("GitHub returned invalid JSON") from None
    if not isinstance(payload, dict):
        raise ResearchError("GitHub returned an unexpected JSON shape")
    return payload


def search(query: str, limit: int = 10, sort: str = "stars", window: int | None = None,
           date_basis: str = "created", now: datetime | None = None) -> dict:
    if not 1 <= limit <= 30:
        raise ResearchError("limit must be between 1 and 30")
    if sort not in {"stars", "updated"}:
        raise ResearchError("sort must be stars or updated")
    if window not in {None, 7, 30, 90}:
        raise ResearchError("window must be 7, 30, or 90 days")
    if date_basis not in {"created", "pushed"}:
        raise ResearchError("date-basis must be created or pushed")
    scoped_query = query.strip()
    if not scoped_query:
        raise ResearchError("query must not be empty")
    qualification = None
    if window is not None:
        end = now or utc_now()
        start = end - timedelta(days=window)
        date_filter = f"{start.date().isoformat()}..{end.date().isoformat()}"
        scoped_query += f" {date_basis}:{date_filter}"
        qualification = {"days": window, "basis": date_basis, "from": start.date().isoformat(),
                         "through": end.date().isoformat()}
    payload = _request("/search/repositories", {"q": scoped_query, "per_page": str(limit),
                                                  "sort": sort, "order": "desc"})
    items = payload.get("items")
    if not isinstance(items, list):
        raise ResearchError("GitHub search returned no items list")
    return {"query": scoped_query, "sort": sort, "time_qualification": qualification,
            "observed_at": iso_now(), "incomplete_results": payload.get("incomplete_results"),
            "total_count": payload.get("total_count"), "items": items[:limit],
            "interpretation": "A search ranking is not evidence of star velocity or virality."}


def repo_metadata(repo: str) -> dict:
    normalized = normalize_repo(repo)
    data = _request(f"/repos/{quote(normalized, safe='/')}")
    license_data = data.get("license")
    return {"url": data.get("html_url"), "full_name": data.get("full_name", normalized),
            "created_at": data.get("created_at"), "updated_at": data.get("updated_at"),
            "pushed_at": data.get("pushed_at"), "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"), "open_issues": data.get("open_issues_count"),
            "open_issues_includes_pull_requests": True,
            "archived": data.get("archived"), "disabled": data.get("disabled"),
            "license_spdx": license_data.get("spdx_id") if isinstance(license_data, dict) else None,
            "default_branch": data.get("default_branch"), "homepage": data.get("homepage"),
            "languages_url": data.get("languages_url"), "observed_at": iso_now(),
            "metadata_source": "GitHub REST API"}


def observe(repo: str, cache: str) -> dict:
    item = repo_metadata(repo)
    stars = item["stars"]
    if not isinstance(stars, int) or isinstance(stars, bool) or stars < 0:
        raise ResearchError("GitHub did not return an observed nonnegative star count; snapshot not saved")
    snapshot = {"repo": item["full_name"], "observed_at": item["observed_at"],
                "total_stars": stars, "metadata": item}
    try:
        with Path(cache).open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")) + "\n")
    except OSError as exc:
        raise ResearchError(f"could not append snapshot: {type(exc).__name__}") from None
    return snapshot


def growth(repo: str, cache: str) -> dict:
    normalized = normalize_repo(repo).lower()
    snapshots = []
    try:
        with Path(cache).open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                try:
                    row = json.loads(line)
                    stamp = datetime.fromisoformat(row["observed_at"].replace("Z", "+00:00"))
                    count = row["total_stars"]
                    row_repo = normalize_repo(row["repo"]).lower()
                    if stamp.tzinfo is None or stamp.utcoffset() is None:
                        raise ValueError
                    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
                        raise ValueError
                except (ValueError, TypeError, KeyError, json.JSONDecodeError, AttributeError):
                    raise ResearchError(f"malformed snapshot cache at line {line_number}") from None
                if row_repo == normalized:
                    snapshots.append((stamp, count))
    except OSError as exc:
        raise ResearchError(f"could not read snapshot cache: {type(exc).__name__}") from None
    snapshots.sort(key=lambda entry: entry[0])
    distinct = []
    for entry in snapshots:
        if distinct and entry[0] == distinct[-1][0] and entry[1] != distinct[-1][1]:
            raise ResearchError("conflicting star counts at the same observation timestamp")
        if not distinct or entry[0] != distinct[-1][0]:
            distinct.append(entry)
    if len(distinct) < 2:
        return {"repo": normalized, "status": "unknown", "reason": "fewer than two distinct observations"}
    first, last = distinct[0], distinct[-1]
    elapsed = last[0] - first[0]
    return {"repo": normalized, "status": "observed", "start_observed_at": first[0].isoformat(),
            "end_observed_at": last[0].isoformat(), "elapsed_seconds": elapsed.total_seconds(),
            "start_stars": first[1], "end_stars": last[1], "net_star_delta": last[1] - first[1],
            "interpretation": "Observed change between these timestamps; no velocity estimate."}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p_search = commands.add_parser("search")
    p_search.add_argument("query")
    p_search.add_argument("--limit", type=int, default=10)
    p_search.add_argument("--sort", choices=("stars", "updated"), default="stars")
    p_search.add_argument("--window", type=int, choices=(7, 30, 90))
    p_search.add_argument("--date-basis", choices=("created", "pushed"), default="created")
    p_repo = commands.add_parser("repo")
    p_repo.add_argument("repo")
    p_observe = commands.add_parser("observe")
    p_observe.add_argument("repo")
    p_observe.add_argument("--cache", required=True)
    p_growth = commands.add_parser("growth")
    p_growth.add_argument("repo")
    p_growth.add_argument("--cache", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "search":
            result = search(args.query, args.limit, args.sort, args.window, args.date_basis)
        elif args.command == "repo":
            result = repo_metadata(args.repo)
        elif args.command == "observe":
            result = observe(args.repo, args.cache)
        else:
            result = growth(args.repo, args.cache)
    except ResearchError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
