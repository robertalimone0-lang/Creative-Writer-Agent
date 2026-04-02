from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import hashlib
import random
import re


@dataclass
class VariantPack:
    sociological: str
    evocative: str
    psychodynamic: str
    lyrical: str
    minimal: str
    dialogic: str
    questions: List[str]
    notes: Dict[str, str]

    def to_structured_text(self) -> str:
        return f"""=== VARIANTE SOCIOLOGICA ===
{self.sociological}

=== VARIANTE EVOCATIVA ===
{self.evocative}

=== VARIANTE PSICODINAMICA ===
{self.psychodynamic}

=== VARIANTE LIRICA ===
{self.lyrical}

=== VARIANTE MINIMALE ===
{self.minimal}

=== VARIANTE DIALOGICA ===
{self.dialogic}

=== DOMANDE GUIDA ===
{chr(10).join(f"{i+1}. {q}" for i, q in enumerate(self.questions))}
"""


class CreativeWriterEngine:
    def __init__(self, api_key: Optional[str] = None) -> None:
        self.use_openai = False
        try:
            import spacy  # type: ignore
            self.nlp = spacy.load("it_core_news_sm")
        except Exception:
            self.nlp = None

    def transform(self, source_text: str, user_note: str = "", preference_memory: Dict | None = None) -> VariantPack:
        if preference_memory is None:
            preference_memory = {}

        rng = _stable_rng(source_text + user_note)
        doc = None
        if self.nlp:
            doc = self.nlp(source_text[:5000])

        sociological = _apply_sociological(source_text, rng, user_note)
        evocative = _apply_evocative(source_text, rng, user_note)
        psychodynamic = _apply_psychodynamic(source_text, rng, user_note)
        lyrical = _apply_lyrical(source_text, rng, user_note)
        minimal = _apply_minimal(source_text, rng, user_note)
        dialogic = _apply_dialogic(source_text, rng, user_note)

        questions = [
            "Quale direzione preferisci?",
            "Cosa vorresti potenziare?",
            "Cosa vorresti attenuare?",
            "Vuoi una combinazione di due varianti?"
        ]

        notes = {
            "a": "Sociologica: contesto sociale, dinamiche di potere, sistemi impliciti.",
            "b": "Evocativa: immagini sensoriali, atmosfera, suggestioni.",
            "c": "Psicodinamica: conflitti interiori, desideri e tensioni.",
            "d": "Lirica: ritmo, musicalita e densita poetica.",
            "e": "Minimale: asciuttezza e precisione, eliminazione del superfluo.",
            "f": "Dialogica: voce narrante in primo piano, monologo interiore.",
        }

        return VariantPack(
            sociological=sociological,
            evocative=evocative,
            psychodynamic=psychodynamic,
            lyrical=lyrical,
            minimal=minimal,
            dialogic=dialogic,
            questions=questions,
            notes=notes,
        )


def paraphrase_text(text: str, tone: str = "neutral", intensity: float = 0.35) -> str:
    cleaned = text.strip()
    if not cleaned:
        return ""
    rng = _stable_rng(cleaned + tone)
    safe_intensity = max(0.0, min(1.0, intensity))
    result = _apply_synonyms(cleaned, rng, intensity=safe_intensity)
    if tone == "concise":
        result = _apply_minimal(result, rng, note="")
    elif tone == "evocative":
        result = _apply_evocative(result, rng, note="")
    elif tone == "lyrical":
        result = _apply_lyrical(result, rng, note="")
    return result


def _stable_rng(text: str) -> random.Random:
    seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16) % (2**32)
    return random.Random(seed)


def _split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def _split_sentences(text: str) -> list[str]:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    return sentences if sentences else [text.strip()]


def _clean_spacing(text: str) -> str:
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def _note_mentions(note: str, keywords: set[str]) -> bool:
    lowered = (note or "").lower()
    return any(keyword in lowered for keyword in keywords)


def _append_sentence(base: str, sentence: str) -> str:
    cleaned = base.rstrip()
    if not cleaned:
        return sentence
    if cleaned.endswith((".", "!", "?")):
        return f"{cleaned} {sentence}"
    return f"{cleaned}. {sentence}"


def _apply_synonyms(text: str, rng: random.Random, intensity: float = 0.2) -> str:
    mapping = {
        "molto": ["assai", "decisamente"],
        "grande": ["ampio", "vasto", "notevole"],
        "piccolo": ["minuto", "ridotto", "contenuto"],
        "casa": ["dimora", "abitazione"],
        "strada": ["via", "traccia"],
        "vedere": ["scorgere", "osservare"],
        "dire": ["affermare", "sostenere"],
        "persona": ["individuo", "figura"],
        "pensare": ["riflettere", "considerare"],
        "sentire": ["percepire", "avvertire"],
        "luogo": ["posto", "contesto"],
        "cielo": ["volta", "orizzonte"],
        "pioggia": ["scroscio", "acqua"],
        "clima": ["andamento", "meteo"],
        "gente": ["persone", "comunita"],
        "cose": ["elementi", "oggetti"],
        "borgo": ["paese", "centro"],
        "montagne": ["crinali", "rilievi"],
        "vita": ["esistenza", "quotidiano"],
        "tempo": ["ritmo", "scorrere"],
    }
    pattern = r"\b(" + "|".join(map(re.escape, mapping.keys())) + r")\b"

    def repl(match: re.Match) -> str:
        word = match.group(0)
        lower = word.lower()
        if lower in mapping and rng.random() < intensity:
            choice = rng.choice(mapping[lower])
            return choice.capitalize() if word[0].isupper() else choice
        return word

    return re.sub(pattern, repl, text, flags=re.IGNORECASE)


def _apply_sociological(text: str, rng: random.Random, note: str) -> str:
    intros = [
        "Nel tessuto sociale,",
        "Sul piano collettivo,",
        "Dentro la trama delle relazioni,",
        "Nel quadro delle appartenenze,",
    ]

    paragraphs = _split_paragraphs(text)
    rewritten: list[str] = []
    for idx, paragraph in enumerate(paragraphs):
        sentences = _split_sentences(paragraph)
        if sentences:
            sentences[0] = f"{intros[idx % len(intros)]} {sentences[0].lstrip()}"
        merged = " ".join(sentences)
        merged = _apply_synonyms(merged, rng, intensity=0.14)
        rewritten.append(merged)
    result = "\n\n".join(rewritten)
    return _append_note(result, note)


def _apply_evocative(text: str, rng: random.Random, note: str) -> str:
    tails = [
        "Resta un odore di pioggia sulle pietre.",
        "Una luce bassa insiste sulle superfici.",
        "Il dettaglio sensoriale guida la scena.",
        "La materia del luogo si fa piu presente.",
    ]
    paragraphs = _split_paragraphs(text)
    rewritten = []
    add_tail = _note_mentions(note, {"atmosfera", "evocativa", "sensoriale", "immagine", "immagini"})
    for idx, paragraph in enumerate(paragraphs):
        merged = _apply_synonyms(paragraph, rng, intensity=0.22).rstrip()
        if add_tail:
            tail = tails[idx % len(tails)]
            merged = _append_sentence(merged, tail)
        rewritten.append(merged)
    result = "\n\n".join(rewritten)
    return _append_note(result, note)


def _apply_psychodynamic(text: str, rng: random.Random, note: str) -> str:
    frames = [
        "Sotto la superficie,",
        "In controluce,",
        "Nel punto in cui la paura si annida,",
        "Nel modo in cui il desiderio insiste,",
    ]
    closings = [
        "Una tensione resta implicita.",
        "Il conflitto rimane sotto traccia.",
        "La spinta interiore orienta tutto.",
    ]
    paragraphs = _split_paragraphs(text)
    rewritten = []
    add_closing = _note_mentions(note, {"conflitto", "psicodin", "tensione", "interiore"})
    for idx, paragraph in enumerate(paragraphs):
        sentences = _split_sentences(paragraph)
        if sentences:
            sentences[0] = f"{frames[idx % len(frames)]} {sentences[0].lstrip()}"
        merged = " ".join(sentences).rstrip()
        if add_closing:
            closing = closings[idx % len(closings)]
            merged = _append_sentence(merged, closing)
        rewritten.append(merged)
    result = "\n\n".join(rewritten)
    return _append_note(result, note)


def _apply_lyrical(text: str, rng: random.Random, note: str) -> str:
    paragraphs = _split_paragraphs(text)
    rewritten = []
    for paragraph in paragraphs:
        sentences = _split_sentences(paragraph)
        lines = []
        for sentence in sentences:
            cleaned = _apply_synonyms(sentence, rng, intensity=0.18).rstrip(".!?")
            lines.append(f"{cleaned}.")
        rewritten.append("\n".join(lines))
    result = "\n\n".join(rewritten)
    return _append_note(result, note)


def _apply_minimal(text: str, rng: random.Random, note: str) -> str:
    sentences = _split_sentences(text)
    shortened = []
    for sentence in sentences:
        core = re.split(r",|;|:", sentence)[0]
        words = re.findall(r"\b[\wÀ-ÿ'-]+\b", core)
        if not words:
            continue
        keep = words[: min(len(words), rng.randint(10, 14))]
        shortened.append(" ".join(keep))
    result = ". ".join(shortened)
    if result:
        result += "."
    return _append_note(result, note)


def _apply_dialogic(text: str, rng: random.Random, note: str) -> str:
    prompts = [
        "Io penso che",
        "Io ricordo che",
        "Io vedo che",
        "Io sento che",
    ]
    sentences = _split_sentences(text)
    rewritten = []
    for idx, sentence in enumerate(sentences):
        prompt = prompts[idx % len(prompts)]
        cleaned = sentence.rstrip(".!?")
        rewritten.append(f"{prompt} {cleaned}.")
    if rewritten:
        rewritten.append("E tu, cosa avresti fatto?")
    result = " ".join(rewritten)
    return _append_note(result, note)


def _append_note(text: str, note: str) -> str:
    cleaned = _clean_spacing(text)
    if note:
        return f"{cleaned}\n\nNota: {note}"
    return cleaned


def extract_text_from_pdf(file) -> str:
    try:
        import PyPDF2

        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as exc:
        return f"Errore PDF: {exc}"


def extract_text_from_docx(file) -> str:
    try:
        import docx

        doc = docx.Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as exc:
        return f"Errore DOCX: {exc}"
