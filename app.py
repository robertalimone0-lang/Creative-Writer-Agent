from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request

from creative_writer import (
    CreativeWriterEngine,
    VariantPack,
    extract_text_from_docx,
    extract_text_from_pdf,
)
from italian_tools import ItalianLinguisticStudio
from open_resources import OpenResourcesHub
from test import run_checks


MAX_TEXT_LENGTH = 120_000
MAX_UPLOAD_SIZE = 8 * 1024 * 1024
ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}
VARIANT_ORDER = [
    ("sociological", "Sociologica", "a"),
    ("evocative", "Evocativa", "b"),
    ("psychodynamic", "Psicodinamica", "c"),
    ("lyrical", "Lirica", "d"),
    ("minimal", "Minimale", "e"),
    ("dialogic", "Dialogica", "f"),
]


engine = CreativeWriterEngine()
linguistic_studio = ItalianLinguisticStudio()
resource_hub = OpenResourcesHub()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE
    app.config["JSON_SORT_KEYS"] = False

    @app.get("/")
    def index() -> str:
        return render_template(
            "index.html",
            status_payload={
                "engine_has_spacy": engine.nlp is not None,
                "analysis_model": getattr(linguistic_studio, "_model_name", "") or "non disponibile",
                "analysis_available": getattr(linguistic_studio, "_nlp", None) is not None,
                "upload_types": ", ".join(sorted(ext.lstrip(".") for ext in ALLOWED_EXTENSIONS)),
            },
        )

    @app.get("/health")
    def health() -> Any:
        return jsonify({"ok": True, "app": "creative-writer-ai"})

    @app.post("/api/refine")
    def refine() -> Any:
        note = request.form.get("note", "").strip()
        include_analysis = _coerce_bool(request.form.get("include_analysis"))

        try:
            source_text, origin_label = _resolve_source_text()
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        if not source_text:
            return jsonify({"error": "Inserisci un testo o carica un file prima di generare le varianti."}), 400

        if len(source_text) > MAX_TEXT_LENGTH:
            return jsonify(
                {
                    "error": (
                        f"Il testo supera il limite di {MAX_TEXT_LENGTH:,} caratteri. "
                        f"Attuali: {len(source_text):,}."
                    )
                }
            ), 400

        pack = engine.transform(source_text, user_note=note)
        structured_output = pack.to_structured_text()
        errors = run_checks(structured_output)
        analysis = linguistic_studio.analyze_text(source_text) if include_analysis else None

        return jsonify(
            {
                "meta": {
                    "characters": len(source_text),
                    "words": len(source_text.split()),
                    "source": origin_label,
                    "note_used": bool(note),
                },
                "variants": _serialize_variants(pack),
                "questions": pack.questions,
                "structured_output": structured_output,
                "errors": errors,
                "analysis": analysis,
            }
        )

    @app.post("/api/analyze")
    def analyze_text() -> Any:
        payload = request.get_json(silent=True) or {}
        text = str(payload.get("text", "")).strip()
        if not text:
            return jsonify({"error": "Inserisci prima un testo da analizzare."}), 400
        return jsonify(linguistic_studio.analyze_text(text))

    @app.get("/api/resources")
    def resources() -> Any:
        query = request.args.get("q", "").strip()
        if not query:
            return jsonify({"error": "Inserisci una parola o un autore da cercare."}), 400
        payload = resource_hub.lookup_term(query)
        return jsonify(_to_plain_data(payload))

    @app.errorhandler(413)
    def file_too_large(_: Any) -> Any:
        return jsonify({"error": "File troppo grande. Limite massimo: 8 MB."}), 413

    return app


def _resolve_source_text() -> tuple[str, str]:
    inline_text = request.form.get("text", "").strip()
    uploaded_file = request.files.get("file")

    if inline_text:
        return inline_text, "editor"

    if uploaded_file and uploaded_file.filename:
        extracted = _extract_text_from_upload(uploaded_file)
        cleaned = extracted.strip()
        return cleaned, uploaded_file.filename

    return "", "vuoto"


def _extract_text_from_upload(uploaded_file: Any) -> str:
    suffix = Path(uploaded_file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ext.lstrip(".") for ext in ALLOWED_EXTENSIONS))
        raise ValueError(f"Formato non supportato. Usa uno tra: {allowed}.")

    if suffix in {".txt", ".md"}:
        raw = uploaded_file.read()
        return _decode_text(raw)

    uploaded_file.stream.seek(0)
    if suffix == ".pdf":
        extracted = extract_text_from_pdf(uploaded_file.stream)
    else:
        extracted = extract_text_from_docx(uploaded_file.stream)

    if extracted.startswith("Errore "):
        raise ValueError(extracted)
    return extracted


def _decode_text(raw: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _serialize_variants(pack: VariantPack) -> list[dict[str, str]]:
    serialized: list[dict[str, str]] = []
    for attribute, label, note_key in VARIANT_ORDER:
        serialized.append(
            {
                "id": attribute,
                "label": label,
                "text": getattr(pack, attribute),
                "note": pack.notes.get(note_key, ""),
            }
        )
    return serialized


def _coerce_bool(value: str | None) -> bool:
    return str(value).lower() in {"1", "true", "yes", "on"}


def _to_plain_data(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, list):
        return [_to_plain_data(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_plain_data(item) for key, item in value.items()}
    return value


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
