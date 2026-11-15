import io
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError
from urllib.request import Request

import github_research as gh


def response(payload):
    result = MagicMock()
    result.__enter__.return_value.read.return_value = json.dumps(payload).encode()
    return result


class GitHubResearchTests(unittest.TestCase):
    def test_repo_metadata_normalizes_github_url(self):
        data = {"html_url": "https://github.com/Org/Repo", "full_name": "Org/Repo",
                "created_at": "2024-01-01T00:00:00Z", "updated_at": "2024-02-01T00:00:00Z",
                "pushed_at": "2024-02-02T00:00:00Z", "stargazers_count": 8,
                "forks_count": 2, "open_issues_count": 3, "archived": False,
                "disabled": False, "license": {"spdx_id": "MIT"}, "default_branch": "main",
                "homepage": "", "languages_url": "https://api.github.com/repos/Org/Repo/languages"}
        with patch.object(gh, "_request", return_value=data) as request, \
             patch.object(gh, "iso_now", return_value="2026-01-01T00:00:00Z"):
            result = gh.repo_metadata("https://github.com/Org/Repo.git")
        request.assert_called_once_with("/repos/Org/Repo")
        self.assertEqual(result["full_name"], "Org/Repo")
        self.assertEqual(result["stars"], 8)
        self.assertEqual(result["observed_at"], "2026-01-01T00:00:00Z")

    def test_search_date_window_uses_current_utc_and_marks_scope(self):
        fixed = datetime(2026, 11, 15, 12, tzinfo=timezone.utc)
        with patch.object(gh, "_request", return_value={"total_count": 1, "items": [{"id": 4}]}) as req:
            result = gh.search("motion graphics", limit=1, sort="updated", window=7,
                               date_basis="pushed", now=fixed)
        query = req.call_args.args[1]["q"]
        self.assertIn("pushed:2026-11-08..2026-11-15", query)
        self.assertEqual(result["time_qualification"]["basis"], "pushed")
        self.assertIn("not evidence of star velocity", result["interpretation"])

    def test_rate_limit_stops_once_and_reports_headers(self):
        error = HTTPError("https://api.github.com/x", 429, "slow down",
                          {"Retry-After": "30", "X-RateLimit-Remaining": "0",
                           "X-RateLimit-Reset": "123"}, None)
        with patch.object(gh, "urlopen", side_effect=error) as call:
            with self.assertRaisesRegex(gh.ResearchError, "Retry-After: 30.*stopped without retrying"):
                gh._request("/repos/a/b")
        call.assert_called_once()
        self.assertTrue(error.closed)

    def test_http_403_reports_rate_info_without_retry(self):
        error = HTTPError("https://api.github.com/x", 403, "limited",
                          {"X-RateLimit-Remaining": "0"}, None)
        with patch.object(gh, "urlopen", side_effect=error) as call:
            with self.assertRaisesRegex(gh.ResearchError, "rate remaining: 0"):
                gh._request("/repos/a/b")
        call.assert_called_once()
        self.assertTrue(error.closed)

    def test_redirect_handler_rejects_malicious_location_with_auth_request(self):
        request = Request("https://api.github.com/repos/a/b", headers={"Authorization": "Bearer secret"})
        redirect = gh._RejectRedirects().redirect_request(
            request, None, 302, "Found", {"Location": "https://attacker.example/collect"},
            "https://attacker.example/collect")
        self.assertIsNone(redirect)

    def test_observe_rejects_unavailable_star_count_without_appending(self):
        with tempfile.TemporaryDirectory() as temp:
            cache = Path(temp) / "observations.jsonl"
            with patch.object(gh, "repo_metadata", return_value={"full_name": "a/b", "stars": None}):
                with self.assertRaisesRegex(gh.ResearchError, "snapshot not saved"):
                    gh.observe("a/b", str(cache))
            self.assertFalse(cache.exists())

    def test_timeout_is_reported_without_request_data(self):
        with patch.object(gh, "urlopen", side_effect=TimeoutError):
            with self.assertRaisesRegex(gh.ResearchError, "TimeoutError") as error:
                gh._request("/repos/a/b")
        self.assertNotIn("secret", str(error.exception))

    def test_token_is_sent_only_as_header_and_never_serialized(self):
        token = "secret-value-do-not-leak"
        with patch.dict("os.environ", {"GH_TOKEN": token}, clear=True), \
             patch.object(gh, "urlopen", return_value=response({"ok": True})) as request:
            payload = gh._request("/repos/a/b")
        sent = request.call_args.args[0]
        self.assertEqual(sent.get_header("Authorization"), f"Bearer {token}")
        self.assertNotIn(token, json.dumps(payload))
        self.assertNotIn(token, sent.full_url)

    def test_cli_stdout_is_valid_under_cp1252_with_non_ascii_api_data(self):
        raw = io.BytesIO()
        stdout = io.TextIOWrapper(raw, encoding="cp1252")
        with patch.object(gh, "_request", return_value={"total_count": 1,
                                                        "items": [{"name": "日本語✨"}]}), \
             patch.object(gh.sys, "stdout", stdout):
            self.assertEqual(gh.main(["search", "motion"]), 0)
            stdout.flush()
        text = raw.getvalue().decode("cp1252")
        result = json.loads(text)
        self.assertEqual(result["items"][0]["name"], "日本語✨")

    def test_rejects_invalid_repo_and_non_github_url(self):
        for value in ("owner", "a/b/c", "https://example.com/a/b", "a b/repo"):
            with self.subTest(value=value), self.assertRaises(gh.ResearchError):
                gh.normalize_repo(value)

    def test_snapshots_compare_actual_distinct_observations(self):
        with tempfile.TemporaryDirectory() as temp:
            cache = Path(temp) / "observations.jsonl"
            rows = [
                {"repo": "Org/Repo", "observed_at": "2026-01-01T00:00:00Z", "total_stars": 10},
                {"repo": "Org/Repo", "observed_at": "2026-01-01T00:00:00Z", "total_stars": 10},
                {"repo": "org/repo", "observed_at": "2026-01-03T12:00:00Z", "total_stars": 17},
                {"repo": "else/where", "observed_at": "2026-01-04T00:00:00Z", "total_stars": 999},
            ]
            cache.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            result = gh.growth("https://github.com/ORG/REPO.git", str(cache))
        self.assertEqual(result["status"], "observed")
        self.assertEqual(result["elapsed_seconds"], 216000)
        self.assertEqual(result["net_star_delta"], 7)

    def test_single_snapshot_is_unknown_and_malformed_cache_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            cache = Path(temp) / "observations.jsonl"
            cache.write_text(json.dumps({"repo": "a/b", "observed_at": "2026-01-01T00:00:00Z",
                                         "total_stars": 2}) + "\n", encoding="utf-8")
            self.assertEqual(gh.growth("a/b", str(cache))["status"], "unknown")
            cache.write_text("{broken\n", encoding="utf-8")
            with self.assertRaisesRegex(gh.ResearchError, "line 1"):
                gh.growth("a/b", str(cache))

    def test_conflicting_counts_at_same_timestamp_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            cache = Path(temp) / "observations.jsonl"
            rows = [{"repo": "a/b", "observed_at": "2026-01-01T00:00:00Z", "total_stars": 2},
                    {"repo": "a/b", "observed_at": "2026-01-01T00:00:00Z", "total_stars": 3}]
            cache.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            with self.assertRaisesRegex(gh.ResearchError, "conflicting star counts"):
                gh.growth("a/b", str(cache))


if __name__ == "__main__":
    unittest.main()
