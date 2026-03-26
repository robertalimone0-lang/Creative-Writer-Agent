from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


USER_AGENT = "CreativeWriterAI/0.1"


@dataclass
class LexicalEntry:
    title: str
    page_url: str
    definitions: list[str]
    synonyms: list[str]
    antonyms: list[str]


@dataclass
class SearchHit:
    title: str
    url: str


class OpenResourcesHub:
    wiktionary_api = "https://it.wiktionary.org/w/api.php"
    wikisource_api = "https://it.wikisource.org/w/api.php"

    def lookup_term(self, term: str) -> dict[str, Any]:
        cleaned = term.strip()
        if not cleaned:
            return {"lexical": None, "texts": []}

        lexical = self.lookup_wiktionary(cleaned)
        texts = self.search_wikisource(cleaned)
        return {
            "lexical": lexical,
            "texts": texts,
        }

    def lookup_wiktionary(self, term: str) -> LexicalEntry | None:
        title = self._resolve_wikimedia_title(self.wiktionary_api, term)
        if not title:
            return None

        payload = self._fetch_json(
            self.wiktionary_api,
            {
                "action": "parse",
                "page": title,
                "prop": "wikitext",
                "format": "json",
                "formatversion": "2",
            },
        )
        wikitext = payload.get("parse", {}).get("wikitext", "")
        if not wikitext:
            return None

        definitions = self._extract_definitions(wikitext)
        synonyms = self._extract_section_items(wikitext, "Sinonimi")
        antonyms = self._extract_section_items(wikitext, "Contrari")
        return LexicalEntry(
            title=title,
            page_url=f"https://it.wiktionary.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}",
            definitions=definitions[:3],
            synonyms=synonyms[:12],
            antonyms=antonyms[:12],
        )

    def search_wikisource(self, term: str, limit: int = 6) -> list[SearchHit]:
        payload = self._fetch_json(
            self.wikisource_api,
            {
                "action": "opensearch",
                "search": term,
                "limit": str(limit),
                "namespace": "0",
                "format": "json",
            },
        )
        titles = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        urls = payload[3] if isinstance(payload, list) and len(payload) > 3 else []
        return [SearchHit(title=title, url=url) for title, url in zip(titles, urls)]

    def check_with_languagetool(self, text: str, endpoint: str) -> dict[str, Any]:
        cleaned_endpoint = endpoint.strip()
        if not cleaned_endpoint:
            return {
                "available": False,
                "message": "Imposta l'URL di un server LanguageTool locale, per esempio http://localhost:8081/v2/check",
                "matches": [],
            }

        data = urllib.parse.urlencode(
            {
                "language": "it",
                "text": text,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            cleaned_endpoint,
            data=data,
            headers={
                "User-Agent": USER_AGENT,
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=8) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            return {
                "available": False,
                "message": f"LanguageTool non raggiungibile: {exc}",
                "matches": [],
            }

        matches = []
        for match in payload.get("matches", [])[:10]:
            replacements = [item.get("value", "") for item in match.get("replacements", [])[:5]]
            matches.append(
                {
                    "message": match.get("message", ""),
                    "offset": match.get("offset", 0),
                    "length": match.get("length", 0),
                    "replacements": replacements,
                }
            )

        return {
            "available": True,
            "message": f"Controllo completato: {len(payload.get('matches', []))} segnalazioni.",
            "matches": matches,
        }

    def _resolve_wikimedia_title(self, api_url: str, term: str) -> str:
        direct = self._fetch_json(
            api_url,
            {
                "action": "query",
                "titles": term,
                "format": "json",
            },
        )
        pages = direct.get("query", {}).get("pages", {})
        for page in pages.values():
            title = page.get("title", "")
            if title and "missing" not in page:
                return title

        payload = self._fetch_json(
            api_url,
            {
                "action": "opensearch",
                "search": term,
                "limit": "1",
                "namespace": "0",
                "format": "json",
            },
        )
        titles = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        return titles[0] if titles else ""

    def _fetch_json(self, api_url: str, params: dict[str, str]) -> Any:
        query = urllib.parse.urlencode(params)
        request = urllib.request.Request(
            f"{api_url}?{query}",
            headers={"User-Agent": USER_AGENT},
        )
        with urllib.request.urlopen(request, timeout=8) as response:
            return json.loads(response.read().decode("utf-8"))

    def _extract_definitions(self, wikitext: str) -> list[str]:
        definitions = []
        for line in wikitext.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") and not stripped.startswith("#:"):
                cleaned = self._clean_wikicode(stripped.lstrip("#").strip())
                if cleaned:
                    definitions.append(cleaned)
        return definitions

    def _extract_section_items(self, wikitext: str, section_name: str) -> list[str]:
        pattern = re.compile(
            rf"=+\s*{re.escape(section_name)}\s*=+\s*\n(?P<body>.*?)(?=\n=+\s*[^=\n]+\s*=+\s*\n|$)",
            re.DOTALL | re.IGNORECASE,
        )
        match = pattern.search(wikitext)
        if not match:
            return []

        items = []
        for line in match.group("body").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(("*", "#", ":")):
                cleaned = self._clean_wikicode(stripped.lstrip("*#:").strip())
                if cleaned:
                    items.extend(self._split_items(cleaned))
        return list(dict.fromkeys(items))

    def _split_items(self, text: str) -> list[str]:
        parts = re.split(r",|;|/|\u2022", text)
        cleaned = []
        for part in parts:
            item = part.strip()
            if item:
                cleaned.append(item)
        return cleaned

    def _clean_wikicode(self, text: str) -> str:
        cleaned = text
        cleaned = re.sub(r"\{\{[^{}]*\}\}", "", cleaned)
        cleaned = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"\2", cleaned)
        cleaned = re.sub(r"\[\[([^\]]+)\]\]", r"\1", cleaned)
        cleaned = re.sub(r"<[^>]+>", "", cleaned)
        cleaned = re.sub(r"''+", "", cleaned)
        cleaned = re.sub(r"\[[0-9]+\]", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip(" ,;:")
