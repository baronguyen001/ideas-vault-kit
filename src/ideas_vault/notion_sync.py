"""Optional, bring-your-own-key Notion sync that pushes each idea into a Notion database.

This module is opt-in and never imported at CLI startup, so the core install stays
offline-first. It needs two things in the environment:

- ``NOTION_API_KEY`` — an internal integration token (``ntn_...`` / ``secret_...``).
- ``NOTION_DB`` — the target database (data source) id.

Each idea becomes one database row keyed by a stable ``idea_key`` (the idea folder
name). Re-running upserts: an existing row with the same key is updated in place,
otherwise a new page is created. Network access goes through :func:`_request`, a thin
``requests`` wrapper that tests monkeypatch, so CI never makes a live call.

``requests`` is an optional dependency installed via the ``notion`` extra
(``pip install "ideas-vault-kit[notion]"``). Without it, or without the env vars, the
sync degrades clearly instead of raising an opaque import error.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ideas_vault.frontmatter import IdeaMeta
from ideas_vault.index import _idea_number, collect, go_or_kill

_API_ROOT = "https://api.notion.com/v1"
_NOTION_VERSION = "2022-06-28"

ENABLE_HINT = "set NOTION_API_KEY + NOTION_DB to enable"
REQUESTS_HINT = 'install the extra to enable: pip install "ideas-vault-kit[notion]"'


class NotionError(RuntimeError):
    """Raised when a Notion request fails or returns an unexpected payload."""


class MissingConfigError(NotionError):
    """Raised when the key or database id is missing; the CLI degrades gracefully."""


class MissingRequestsError(NotionError):
    """Raised when the optional ``requests`` dependency is not installed."""


@dataclass(frozen=True)
class SyncResult:
    """Outcome of syncing one idea to Notion."""

    idea_key: str
    title: str
    action: str  # "created" or "updated"
    page_id: str


def idea_key(meta: IdeaMeta) -> str:
    """Stable upsert key for an idea: its folder name (unique within a vault)."""
    return meta.folder


def _require_requests() -> Any:
    try:
        import requests
    except ImportError as exc:  # pragma: no cover - exercised via monkeypatch in tests
        raise MissingRequestsError(REQUESTS_HINT) from exc
    return requests


def _headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": _NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _request(
    method: str,
    url: str,
    api_key: str,
    payload: dict | None = None,
    *,
    timeout: float = 30.0,
) -> dict:
    """Send a Notion API request and return the decoded JSON. Patched in tests."""
    requests = _require_requests()
    try:
        response = requests.request(
            method, url, headers=_headers(api_key), json=payload, timeout=timeout
        )
    except Exception as exc:  # requests.RequestException and friends
        msg = f"Notion request failed: {exc}"
        raise NotionError(msg) from exc
    if response.status_code >= 400:
        msg = f"Notion API error {response.status_code}: {response.text[:300]}"
        raise NotionError(msg)
    return response.json()


def _properties(meta: IdeaMeta) -> dict[str, Any]:
    """Map an idea to Notion property values, matching the documented database schema."""
    number = _idea_number(meta.folder)
    props: dict[str, Any] = {
        "Name": {"title": [{"text": {"content": meta.title or meta.folder}}]},
        "Idea Key": {"rich_text": [{"text": {"content": idea_key(meta)}}]},
        "Number": {"rich_text": [{"text": {"content": number}}]},
        "Verdict": {"select": {"name": meta.verdict or "Unscored"}},
        "Flag": {"select": {"name": go_or_kill(meta.verdict)}},
        "Market Status": {"select": {"name": meta.market_status or "unset"}},
        "Date": {"rich_text": [{"text": {"content": meta.date}}]},
    }
    if meta.score is not None:
        props["Score"] = {"number": meta.score}
    return props


def _find_page(api_key: str, database_id: str, key: str) -> str | None:
    """Return the page id whose ``Idea Key`` equals ``key``, or ``None`` if absent."""
    url = f"{_API_ROOT}/databases/{database_id}/query"
    payload = {
        "filter": {"property": "Idea Key", "rich_text": {"equals": key}},
        "page_size": 1,
    }
    data = _request("POST", url, api_key, payload)
    results = data.get("results") or []
    if not results:
        return None
    page_id = results[0].get("id")
    return str(page_id) if page_id else None


def _upsert(api_key: str, database_id: str, meta: IdeaMeta) -> SyncResult:
    key = idea_key(meta)
    props = _properties(meta)
    existing = _find_page(api_key, database_id, key)
    if existing is None:
        url = f"{_API_ROOT}/pages"
        payload = {"parent": {"database_id": database_id}, "properties": props}
        data = _request("POST", url, api_key, payload)
        return SyncResult(key, meta.title, "created", str(data.get("id", "")))
    url = f"{_API_ROOT}/pages/{existing}"
    _request("PATCH", url, api_key, {"properties": props})
    return SyncResult(key, meta.title, "updated", existing)


def sync(
    vault: Path,
    *,
    api_key: str | None = None,
    database_id: str | None = None,
) -> list[SyncResult]:
    """Upsert every scored idea in ``vault`` into the Notion database.

    The key is read from ``api_key`` or ``NOTION_API_KEY``; the database id from
    ``database_id`` or ``NOTION_DB``. Raises :class:`MissingConfigError` if either is
    absent so the CLI can degrade with a clear message.
    """
    key = api_key or os.getenv("NOTION_API_KEY")
    database = database_id or os.getenv("NOTION_DB")
    if not key or not database:
        raise MissingConfigError(ENABLE_HINT)

    return [_upsert(key, database, meta) for meta in collect(vault)]
