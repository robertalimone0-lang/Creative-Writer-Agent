from __future__ import annotations

from collections import Counter
from typing import Any


class ItalianLinguisticStudio:
    def __init__(self) -> None:
        self._nlp = None
        self._model_name = ""
        self._spacy_loaded = False
        self._load_pipeline()

    def analyze_text(self, text: str) -> dict[str, Any]:
        cleaned = text.strip()
        if not cleaned:
            return {
                "available": self._spacy_loaded,
                "model": self._model_name or "non disponibile",
                "message": "Inserisci prima un testo da analizzare.",
                "token_count": 0,
                "sentence_count": 0,
                "average_sentence_length": 0,
                "key_lemmas": [],
                "repeated_lemmas": [],
                "pos_profile": [],
                "named_entities": [],
                "sentence_openings": [],
            }

        if self._nlp is None:
            return {
                "available": False,
                "model": "non disponibile",
                "message": (
                    "spaCy non è installato. Installa il pacchetto e, se vuoi l'analisi più ricca, "
                    "anche il modello italiano `it_core_news_sm`."
                ),
                "token_count": 0,
                "sentence_count": 0,
                "average_sentence_length": 0,
                "key_lemmas": [],
                "repeated_lemmas": [],
                "pos_profile": [],
                "named_entities": [],
                "sentence_openings": [],
            }

        doc = self._nlp(cleaned)
        tokens = [token for token in doc if not token.is_space]
        content_tokens = [
            token for token in tokens
            if token.is_alpha and not token.is_stop and len(token.text) > 2
        ]
        sentences = list(doc.sents) if doc.has_annotation("SENT_START") else [doc]
        lemmas = [
            (token.lemma_ if token.lemma_ and token.lemma_ != "-PRON-" else token.text).lower()
            for token in content_tokens
        ]
        lemma_counter = Counter(lemmas)
        pos_counter = Counter(token.pos_ or "X" for token in content_tokens)
        entities = [
            {"text": ent.text, "label": ent.label_}
            for ent in doc.ents[:10]
        ] if doc.ents else []
        openings = []
        for sentence in sentences[:8]:
            first = next((token.text for token in sentence if token.is_alpha), "")
            if first:
                openings.append(first)

        sentence_lengths = []
        for sentence in sentences:
            length = len([token for token in sentence if token.is_alpha])
            if length:
                sentence_lengths.append(length)

        average_sentence_length = round(sum(sentence_lengths) / len(sentence_lengths), 2) if sentence_lengths else 0

        message = (
            "Analisi italiana disponibile."
            if self._spacy_loaded
            else "Analisi di base disponibile con pipeline italiana minimale."
        )

        return {
            "available": True,
            "model": self._model_name,
            "message": message,
            "token_count": len(tokens),
            "sentence_count": len(sentences),
            "average_sentence_length": average_sentence_length,
            "key_lemmas": [lemma for lemma, _ in lemma_counter.most_common(12)],
            "repeated_lemmas": [lemma for lemma, count in lemma_counter.items() if count > 1][:12],
            "pos_profile": [{"tag": tag, "count": count} for tag, count in pos_counter.most_common(8)],
            "named_entities": entities,
            "sentence_openings": openings,
        }

    def _load_pipeline(self) -> None:
        try:
            import spacy  # type: ignore
        except Exception:
            self._nlp = None
            self._model_name = ""
            self._spacy_loaded = False
            return

        for model_name in ("it_core_news_sm",):
            try:
                self._nlp = spacy.load(model_name)
                self._model_name = model_name
                self._spacy_loaded = True
                return
            except Exception:
                continue

        try:
            self._nlp = spacy.blank("it")
            if "sentencizer" not in self._nlp.pipe_names:
                self._nlp.add_pipe("sentencizer")
            self._model_name = "spacy.blank('it')"
            self._spacy_loaded = False
        except Exception:
            self._nlp = None
            self._model_name = ""
            self._spacy_loaded = False
