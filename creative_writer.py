from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


INTRO_TEXT = (
    "Ho lavorato sul tuo testo mantenendo la voce originale ma sviluppandolo in tre direzioni stilistiche: "
    "sociologica, evocativa e psicodinamica. Tutte rispettano il tuo dettato: frase medio-lunga, ritmo dinamico "
    "ma non veloce, sintassi ineccepibile, rifiuto di patetismo e retorica. Leggile con calma e dimmi quale ti "
    "sembra più vicina a ciò che cerchi."
)


@dataclass
class VariantPack:
    intro: str
    sociological: str
    evocative: str
    psychodynamic: str
    notes: dict[str, str]
    questions: list[str]

    def to_structured_text(self) -> str:
        return (
            f"{self.intro}\n\n"
            "--- VARIANTE A: SOCIOLOGICA ---\n"
            f"{self.sociological}\n\n"
            "--- VARIANTE B: EVOCATIVA ---\n"
            f"{self.evocative}\n\n"
            "--- VARIANTE C: PSICODINAMICA ---\n"
            f"{self.psychodynamic}\n\n"
            "--- NOTE STILISTICHE ---\n"
            f"Per la Variante A: {self.notes['a']}\n"
            f"Per la Variante B: {self.notes['b']}\n"
            f"Per la Variante C: {self.notes['c']}\n\n"
            "--- DOMANDE GUIDA ---\n"
            + "\n".join(f"{index}. {question}" for index, question in enumerate(self.questions, start=1))
        )


class CreativeWriterEngine:
    def transform(
        self,
        text: str,
        user_note: str = "",
        preference_memory: dict[str, Any] | None = None,
    ) -> VariantPack:
        cleaned = self._normalize_text(text)
        paragraphs = self._paragraphs(cleaned)
        if not paragraphs:
            paragraphs = [""]

        memory = preference_memory or {}
        sociological = "\n\n".join(
            self._rewrite_paragraph(paragraph, "sociological", memory) for paragraph in paragraphs
        )
        evocative = "\n\n".join(
            self._rewrite_paragraph(paragraph, "evocative", memory) for paragraph in paragraphs
        )
        psychodynamic = "\n\n".join(
            self._rewrite_paragraph(paragraph, "psychodynamic", memory) for paragraph in paragraphs
        )

        sociological = self._apply_preferences_to_variant(sociological, "sociological", memory)
        evocative = self._apply_preferences_to_variant(evocative, "evocative", memory)
        psychodynamic = self._apply_preferences_to_variant(psychodynamic, "psychodynamic", memory)

        intro = INTRO_TEXT

        return VariantPack(
            intro=intro,
            sociological=sociological,
            evocative=evocative,
            psychodynamic=psychodynamic,
            notes={
                "a": "mette a fuoco contesto, rapporti di forza e ruolo sociale senza raffreddare del tutto il testo.",
                "b": "concentra la pressione del brano su immagine, atmosfera e percezione sensoriale.",
                "c": "sposta il baricentro su difese, ambivalenze e logiche interiori che orientano il gesto.",
            },
            questions=[
                "Quale direzione ti sembra più affine al cuore di ciò che vuoi esprimere?",
                "C'è un elemento di una variante che vorresti vedere integrato in un'altra?",
                "Vuoi che sviluppi ulteriormente una delle tre direzioni?",
            ],
        )

    def _rewrite_paragraph(self, paragraph: str, mode: str, memory: dict[str, Any]) -> str:
        sentences = [self._refine_sentence(sentence) for sentence in self._sentences(paragraph)]
        if not sentences:
            return ""

        motifs = self._extract_motifs(paragraph)
        opener = self._build_opener(sentences, mode, memory, motifs)
        development = self._build_development(sentences[1:], mode, memory, motifs)
        closure = self._build_closure(sentences, mode, memory, motifs)
        pieces = [piece for piece in [opener, development, closure] if piece]
        return self._cleanup_output(" ".join(pieces))

    def _refine_sentence(self, sentence: str) -> str:
        refined = sentence.strip()
        refined = re.sub(r"\s+", " ", refined)
        refined = re.sub(r"\s+([,.;:!?])", r"\1", refined)
        refined = re.sub(r"\bmolto\b", "assai", refined, flags=re.IGNORECASE)
        refined = re.sub(r"\bsembra\b", "pare", refined, flags=re.IGNORECASE)
        refined = re.sub(r"\bsembrava\b", "pareva", refined, flags=re.IGNORECASE)
        refined = re.sub(r"\bc'era\b", "vi era", refined, flags=re.IGNORECASE)
        refined = re.sub(r"\bc'erano\b", "vi erano", refined, flags=re.IGNORECASE)
        if refined and refined[-1] not in ".!?":
            refined += "."
        return refined

    def _apply_preferences_to_variant(self, text: str, mode: str, memory: dict[str, Any]) -> str:
        revised = text
        desired = self._desired_traits(memory)
        avoid = self._avoid_traits(memory)
        preferred = self._preferred_direction(memory)
        rejected = set(memory.get("rejected_directions", []))

        if "più breve" in desired or "asciutto" in desired:
            revised = revised.replace(", infatti,", ",")
            revised = revised.replace(" quasi ", " ")
        if "più lungo" in desired or "più denso" in desired:
            revised = revised.replace(" mostra ", " mostra con maggiore evidenza ")
        if "metafore" in avoid:
            revised = revised.replace("seconda coscienza del testo", "struttura sensibile della scena")
            revised = revised.replace("residuo di pressione", "traccia materiale")
        if "retorica" in avoid or "enfasi" in avoid:
            revised = revised.replace("con maggiore evidenza", "più chiaramente")

        if preferred == mode:
            revised = self._promote_mode(revised, mode)
        if mode in rejected:
            revised = self._soften_mode(revised, mode)

        return self._cleanup_output(revised)

    def _build_opener(
        self,
        sentences: list[str],
        mode: str,
        memory: dict[str, Any],
        motifs: list[str],
    ) -> str:
        first = sentences[0].rstrip(".")
        motif = self._motif_phrase(motifs)
        if mode == "sociological":
            templates = [
                f"{first}, e già in questo primo dato si leggono la pressione del contesto, la distribuzione dei ruoli e la pedagogia muta dell'ambiente.",
                f"{first}, ma il punto non è soltanto individuale: intorno si intravede un ordine di attese che regola gesti, margini e possibilità.",
            ]
            if self._preferred_direction(memory) == "sociological":
                templates.append(
                    f"{first}, entro una cornice in cui {motif} smettono di essere dettagli sparsi e diventano indizi di una struttura."
                )
            return self._pick_template(templates, first)
        if mode == "evocative":
            templates = [
                f"{first}, mentre attorno {motif} costruiscono un'atmosfera che non accompagna il testo soltanto, ma ne modifica la temperatura.",
                f"{first}, e subito l'aria della scena prende corpo: non come ornamento, ma come materia che aderisce ai gesti e li incide.",
            ]
            if "metafore" in self._avoid_traits(memory):
                templates = [
                    f"{first}, con una scena che si precisa per luce, materia e ritmo, senza forzare la mano figurale.",
                    f"{first}, e lo spazio si definisce con nettezza attraverso elementi concreti, quasi tattili.",
                ]
            return self._pick_template(templates, first)
        templates = [
            f"{first}, come se il gesto visibile fosse già la superficie di un conflitto meno dichiarato.",
            f"{first}, e sotto l'evidenza della scena si avverte una logica interiore fatta di trattenimento, difesa e desiderio sorvegliato.",
        ]
        if self._preferred_direction(memory) == "psychodynamic":
            templates.append(
                f"{first}, quasi che ciò che accade all'esterno serva soprattutto a tenere insieme qualcosa di più scisso e vulnerabile."
            )
        return self._pick_template(templates, first)

    def _build_development(
        self,
        remaining_sentences: list[str],
        mode: str,
        memory: dict[str, Any],
        motifs: list[str],
    ) -> str:
        if not remaining_sentences:
            return ""
        merged = self._merge_sentences(remaining_sentences[:2])
        motif = self._motif_phrase(motifs)
        if mode == "sociological":
            templates = [
                f"{merged}, e proprio per questo il privato appare inseparabile dalle abitudini, dalle rinunce e dalle asimmetrie che lo hanno formato.",
                f"{merged}, ma letto da vicino il brano mostra soprattutto come {motif} si organizzino dentro una disciplina sociale già interiorizzata.",
            ]
            return self._pick_template(templates, merged)
        if mode == "evocative":
            templates = [
                f"{merged}, e il dettaglio non spiega: deposita un colore, una densità, un attrito che continua a lavorare sotto la frase.",
                f"{merged}, mentre la scena si precisa per accumulo di materia sensibile, quasi che ogni elemento lasci una traccia nell'aria.",
            ]
            if "metafore" in self._avoid_traits(memory):
                templates = [
                    f"{merged}, e l'effetto nasce dalla precisione percettiva del dettaglio, non da un surplus di immagini.",
                    f"{merged}, con una resa più netta che ornata, affidata alla concretezza di luce, spazio e postura.",
                ]
            return self._pick_template(templates, merged)
        templates = [
            f"{merged}, e ciò che emerge non è una psicologia dichiarata, ma un sistema di risposte che protegge il soggetto mentre lo limita.",
            f"{merged}, lasciando affiorare una contraddizione: il bisogno di controllo convive con qualcosa che continua a incrinarlo dall'interno.",
        ]
        return self._pick_template(templates, merged)

    def _build_closure(
        self,
        sentences: list[str],
        mode: str,
        memory: dict[str, Any],
        motifs: list[str],
    ) -> str:
        motif = self._motif_phrase(motifs)
        last = sentences[-1].rstrip(".")
        if len(sentences) == 1:
            if mode == "sociological":
                return f"Così {motif} acquistano un valore che supera l'episodio e rimanda a una forma di ordine più vasta."
            if mode == "evocative":
                return f"Alla fine resta soprattutto una qualità dell'aria, una presenza sensibile che trattiene il brano nella memoria."
            return f"Alla fine il testo sembra custodire meno un fatto che il modo in cui quel fatto si è depositato nella vita interiore."

        if mode == "sociological":
            return f"In questa luce, {last.lower()} e il brano smette di essere solo esperienza per diventare anche sintomo di posizione, vincolo e adattamento."
        if mode == "evocative":
            return f"Per questo, {last.lower()} e ciò che rimane è la persistenza di un'atmosfera, più che la sola nuda informazione."
        return f"Per questo, {last.lower()} e il nodo vero resta la forma interiore del trattenimento, non il gesto in sé."

    def _promote_mode(self, text: str, mode: str) -> str:
        if mode == "sociological":
            return text.replace("ambiente", "ambiente sociale", 1)
        if mode == "evocative":
            return text.replace("atmosfera", "atmosfera sensibile", 1)
        if mode == "psychodynamic":
            return text.replace("contraddizione interiore", "ambivalenza interiore", 1)
        return text

    def _soften_mode(self, text: str, mode: str) -> str:
        if mode == "sociological":
            return text.replace("asimmetrie", "assetti").replace("gerarchie", "rapporti")
        if mode == "evocative":
            return text.replace("vibrazione", "presenza").replace("traccia materiale", "traccia")
        if mode == "psychodynamic":
            return text.replace("difese", "reazioni").replace("conflitto", "tensione")
        return text

    def _preferred_direction(self, memory: dict[str, Any]) -> str:
        return str(memory.get("preferred_direction", "") or "")

    def _desired_traits(self, memory: dict[str, Any]) -> list[str]:
        return list(memory.get("desired_traits", []))

    def _avoid_traits(self, memory: dict[str, Any]) -> list[str]:
        return list(memory.get("avoid_traits", []))

    def _extract_motifs(self, text: str) -> list[str]:
        stopwords = {
            "della", "delle", "degli", "dello", "dell", "nella", "nelle", "negli", "nello",
            "della", "questo", "questa", "quello", "quella", "come", "anche", "molto", "poco",
            "dentro", "fuori", "sopra", "sotto", "prima", "dopo", "perche", "perché", "mentre",
            "quando", "aveva", "erano", "era", "sono", "essere", "avere", "nulla", "tutto",
        }
        words = re.findall(r"\b[a-zà-ÿ']{4,}\b", text.lower())
        motifs = []
        for word in words:
            if word not in stopwords and word not in motifs:
                motifs.append(word)
        return motifs[:4]

    def _motif_phrase(self, motifs: list[str]) -> str:
        if not motifs:
            return "luogo, gesto e memoria"
        if len(motifs) == 1:
            return motifs[0]
        if len(motifs) == 2:
            return f"{motifs[0]} e {motifs[1]}"
        return ", ".join(motifs[:-1]) + f" e {motifs[-1]}"

    def _merge_sentences(self, sentences: list[str]) -> str:
        cleaned = [sentence.rstrip(".") for sentence in sentences if sentence.strip()]
        if not cleaned:
            return ""
        if len(cleaned) == 1:
            return cleaned[0]
        return f"{cleaned[0]}; {cleaned[1].lower()}"

    def _pick_template(self, templates: list[str], seed: str) -> str:
        if not templates:
            return seed
        checksum = sum(ord(char) for char in seed)
        return templates[checksum % len(templates)]

    def _normalize_text(self, text: str) -> str:
        normalized = text.replace("’", "'").replace("“", '"').replace("”", '"')
        normalized = re.sub(r"[ \t]+", " ", normalized)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        return normalized.strip()

    def _paragraphs(self, text: str) -> list[str]:
        return [chunk.strip() for chunk in re.split(r"\n\s*\n", text) if chunk.strip()]

    def _sentences(self, text: str) -> list[str]:
        return [chunk.strip() for chunk in re.split(r"(?<=[.!?])\s+", text) if chunk.strip()]

    def _cleanup_output(self, text: str) -> str:
        cleaned = re.sub(r"\s{2,}", " ", text)
        cleaned = re.sub(r"\.\.", ".", cleaned)
        return cleaned.strip()
