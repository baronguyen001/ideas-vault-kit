from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from ideas_vault import notion_sync
from ideas_vault.cli import cli
from ideas_vault.index import collect


class _FakeNotion:
    """Records Notion API calls and answers queries from an in-memory page store."""

    def __init__(self, existing: dict[str, str] | None = None) -> None:
        # Map of idea_key -> page_id for rows that already exist in the DB.
        self.existing = existing or {}
        self.calls: list[tuple[str, str, dict | None]] = []
        self._counter = 0

    def request(self, method: str, url: str, api_key: str, payload=None, *, timeout: float = 30.0):
        self.calls.append((method, url, payload))
        if url.endswith("/query"):
            key = payload["filter"]["rich_text"]["equals"]
            page_id = self.existing.get(key)
            return {"results": [{"id": page_id}] if page_id else []}
        if url.endswith("/pages"):  # create
            self._counter += 1
            return {"id": f"new-page-{self._counter}"}
        return {"id": url.rsplit("/", 1)[-1]}  # PATCH returns the page id


@pytest.fixture
def fake_notion(monkeypatch: pytest.MonkeyPatch) -> _FakeNotion:
    fake = _FakeNotion()
    monkeypatch.setattr(notion_sync, "_request", fake.request)
    return fake


def test_idea_key_is_stable_folder(seeded_vault: Path) -> None:
    metas = collect(seeded_vault)
    assert notion_sync.idea_key(metas[0]) == "001-first"


def test_properties_map_scores_and_verdict(seeded_vault: Path) -> None:
    meta = collect(seeded_vault)[0]
    props = notion_sync._properties(meta)
    assert props["Name"]["title"][0]["text"]["content"] == "First Idea"
    assert props["Idea Key"]["rich_text"][0]["text"]["content"] == "001-first"
    assert props["Verdict"]["select"]["name"] == "GO"
    assert props["Flag"]["select"]["name"] == "GO"
    assert props["Score"]["number"] == 32


def test_sync_creates_new_rows(seeded_vault: Path, fake_notion: _FakeNotion) -> None:
    results = notion_sync.sync(seeded_vault, api_key="k", database_id="db")
    assert [r.action for r in results] == ["created", "created"]
    assert results[0].idea_key == "001-first"
    # Each idea = one query (lookup) + one create.
    methods = [method for method, _url, _payload in fake_notion.calls]
    assert methods.count("POST") == 4  # 2 queries + 2 creates


def test_sync_updates_existing_row(seeded_vault: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _FakeNotion(existing={"001-first": "page-001"})
    monkeypatch.setattr(notion_sync, "_request", fake.request)
    results = notion_sync.sync(seeded_vault, api_key="k", database_id="db")
    by_key = {r.idea_key: r for r in results}
    assert by_key["001-first"].action == "updated"
    assert by_key["001-first"].page_id == "page-001"
    assert by_key["002-second"].action == "created"
    # The update goes through a PATCH to the existing page.
    assert any(method == "PATCH" and url.endswith("page-001") for method, url, _ in fake.calls)


def test_sync_requires_config(seeded_vault: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NOTION_API_KEY", raising=False)
    monkeypatch.delenv("NOTION_DB", raising=False)
    with pytest.raises(notion_sync.MissingConfigError, match="NOTION_API_KEY"):
        notion_sync.sync(seeded_vault)


def test_request_raises_on_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Resp:
        status_code = 401
        text = "unauthorized"

    class _Requests:
        def request(self, *_a, **_k):
            return _Resp()

    monkeypatch.setattr(notion_sync, "_require_requests", lambda: _Requests())
    with pytest.raises(notion_sync.NotionError, match="401"):
        notion_sync._request("POST", "https://api.notion.com/v1/pages", "k", {})


def test_request_wraps_transport_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Requests:
        def request(self, *_a, **_k):
            raise RuntimeError("boom")

    monkeypatch.setattr(notion_sync, "_require_requests", lambda: _Requests())
    with pytest.raises(notion_sync.NotionError, match="request failed"):
        notion_sync._request("POST", "https://api.notion.com/v1/pages", "k", {})


def test_request_returns_json_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Resp:
        status_code = 200

        def json(self):
            return {"ok": True}

    class _Requests:
        def request(self, method, url, headers=None, json=None, timeout=None):
            assert headers["Authorization"].startswith("Bearer ")
            assert headers["Notion-Version"]
            return _Resp()

    monkeypatch.setattr(notion_sync, "_require_requests", lambda: _Requests())
    assert notion_sync._request("GET", "https://api.notion.com/v1/x", "k") == {"ok": True}


def test_cli_notion_sync_without_config_degrades(
    seeded_vault: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("NOTION_API_KEY", raising=False)
    monkeypatch.delenv("NOTION_DB", raising=False)
    runner = CliRunner()
    result = runner.invoke(cli, ["notion-sync", "--vault", str(seeded_vault)])
    assert result.exit_code == 0, result.output
    assert "set NOTION_API_KEY + NOTION_DB to enable" in result.output


def test_cli_notion_sync_reports_actions(
    seeded_vault: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = _FakeNotion(existing={"001-first": "page-001"})
    monkeypatch.setattr(notion_sync, "_request", fake.request)
    monkeypatch.setenv("NOTION_API_KEY", "k")
    monkeypatch.setenv("NOTION_DB", "db")
    runner = CliRunner()
    result = runner.invoke(cli, ["notion-sync", "--vault", str(seeded_vault)])
    assert result.exit_code == 0, result.output
    assert "updated: 001-first" in result.output
    assert "created: 002-second" in result.output
    assert "Synced 2 ideas to Notion (1 created, 1 updated)." in result.output


def test_cli_notion_sync_missing_requests_degrades(
    seeded_vault: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def boom() -> object:
        raise notion_sync.MissingRequestsError(notion_sync.REQUESTS_HINT)

    monkeypatch.setattr(notion_sync, "_require_requests", boom)
    monkeypatch.setenv("NOTION_API_KEY", "k")
    monkeypatch.setenv("NOTION_DB", "db")
    runner = CliRunner()
    result = runner.invoke(cli, ["notion-sync", "--vault", str(seeded_vault)])
    assert result.exit_code == 0, result.output
    assert "pip install" in result.output


def test_cli_notion_sync_reports_api_error(
    seeded_vault: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def boom(*_a, **_k):
        raise notion_sync.NotionError("Notion API error 500: server error")

    monkeypatch.setattr(notion_sync, "_request", boom)
    monkeypatch.setenv("NOTION_API_KEY", "k")
    monkeypatch.setenv("NOTION_DB", "db")
    runner = CliRunner()
    result = runner.invoke(cli, ["notion-sync", "--vault", str(seeded_vault)])
    assert result.exit_code != 0
