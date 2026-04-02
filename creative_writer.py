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
    return _polish_text(result, preserve_linebreaks=tone == "lyrical")


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


_LANGUAGE_TOOL_READY = False
_LANGUAGE_TOOL = None


def _get_language_tool():
    global _LANGUAGE_TOOL_READY, _LANGUAGE_TOOL
    if _LANGUAGE_TOOL_READY:
        return _LANGUAGE_TOOL
    _LANGUAGE_TOOL_READY = True
    try:
        import language_tool_python  # type: ignore

        _LANGUAGE_TOOL = language_tool_python.LanguageTool("it")
    except Exception:
        _LANGUAGE_TOOL = None
    return _LANGUAGE_TOOL


def _dedupe_adjacent_words(text: str) -> str:
    return re.sub(r"\b(\w+)(\s+\1\b)+", r"\1", text, flags=re.IGNORECASE)


def _split_overlong_sentences(text: str, limit: int = 28) -> str:
    sentences = _split_sentences(text)
    refined = []
    for sentence in sentences:
        words = re.findall(r"\b[\wÀ-ÿ'-]+\b", sentence)
        if len(words) > limit:
            replaced = sentence
            for sep in [",", ";", ":"]:
                if sep in replaced:
                    left, right = replaced.split(sep, 1)
                    replaced = f"{left.strip()}. {right.strip()}"
                    break
            refined.append(replaced)
        else:
            refined.append(sentence)
    return " ".join(refined)


def _polish_fragment(text: str) -> str:
    cleaned = _clean_spacing(text)
    cleaned = _dedupe_adjacent_words(cleaned)
    cleaned = _split_overlong_sentences(cleaned)

    tool = _get_language_tool()
    if tool:
        try:
            import language_tool_python  # type: ignore

            matches = tool.check(cleaned)
            cleaned = language_tool_python.utils.correct(cleaned, matches)
        except Exception:
            pass
    return _clean_spacing(cleaned)


def _polish_text(text: str, preserve_linebreaks: bool = False) -> str:
    if preserve_linebreaks:
        lines = text.split("\n")
        polished_lines = []
        for line in lines:
            if line.strip():
                polished_lines.append(_polish_fragment(line))
            else:
                polished_lines.append("")
        return "\n".join(polished_lines).strip()

    paragraphs = _split_paragraphs(text)
    polished = [_polish_fragment(paragraph) for paragraph in paragraphs if paragraph.strip()]
    return "\n\n".join(polished).strip()


def _apply_synonyms(
    text: str,
    rng: random.Random,
    intensity: float = 0.2,
    custom: dict[str, list[str]] | None = None,
) -> str:
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
    if custom:
        mapping.update(custom)
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
    sociological_map = {
        "gente": ["comunita", "popolazione"],
        "famiglia": ["nucleo"],
        "famiglie": ["nuclei"],
        "borgo": ["centro", "paese"],
        "paese": ["comune", "centro"],
        "lavoro": ["occupazione", "impiego"],
        "tradizione": ["consuetudine"],
        "rito": ["consuetudine"],
        "potere": ["autorita"],
        "classe": ["ceto"],
    }
    result = _apply_synonyms(text, rng, intensity=0.2, custom=sociological_map)
    result = _polish_text(result)
    return _append_note(result, note)


def _apply_evocative(text: str, rng: random.Random, note: str) -> str:
    evocative_map = {
        "luce": ["chiarore", "lume"],
        "ombra": ["penombra", "oscurita"],
        "odore": ["profumo", "sentore"],
        "pioggia": ["scroscio", "acqua"],
        "vento": ["brezza", "soffio"],
        "freddo": ["gelo", "rigore"],
        "calore": ["tepore", "ardore"],
        "pietre": ["sassi", "rocce"],
        "cielo": ["volta", "orizzonte"],
        "umidita": ["vapore", "umore"],
    }
    result = _apply_synonyms(text, rng, intensity=0.24, custom=evocative_map)
    result = _polish_text(result)
    return _append_note(result, note)


def _apply_psychodynamic(text: str, rng: random.Random, note: str) -> str:
    psychodynamic_map = {
        "paura": ["timore", "angoscia"],
        "peso": ["pressione", "gravame"],
        "colpa": ["rimorso", "debito"],
        "malessere": ["inquietudine", "sommersione"],
        "desiderio": ["impulso", "brama"],
        "tensione": ["attrito", "contrasto"],
        "sordo": ["sommerso", "muto"],
        "silenzio": ["ritiro", "sospensione"],
    }
    result = _apply_synonyms(text, rng, intensity=0.22, custom=psychodynamic_map)
    result = _polish_text(result)
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
    result = _polish_text(result, preserve_linebreaks=True)
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
    result = _polish_text(result)
    return _append_note(result, note)


def _apply_dialogic(text: str, rng: random.Random, note: str) -> str:
    sentences = _split_sentences(text)
    rewritten = []
    for sentence in sentences:
        cleaned = sentence.strip()
        if not cleaned:
            continue
        if not cleaned.endswith((".", "!", "?")):
            cleaned += "."
        rewritten.append(f"- {cleaned}")
    result = "\n".join(rewritten)
    result = _polish_text(result, preserve_linebreaks=True)
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
