from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_HEADERS = [
    "--- VARIANTE A: SOCIOLOGICA ---",
    "--- VARIANTE B: EVOCATIVA ---",
    "--- VARIANTE C: PSICODINAMICA ---",
    "--- NOTE STILISTICHE ---",
    "--- DOMANDE GUIDA ---",
]

FORBIDDEN_WORDS = {
    "incredibile",
    "meraviglioso",
    "terribile",
}

SAMPLE_OUTPUT = """Ho lavorato sul tuo testo mantenendo la voce originale ma sviluppandolo in tre direzioni stilistiche: sociologica, evocativa e psicodinamica. Tutte rispettano il tuo dettato: frase medio-lunga, ritmo dinamico ma non veloce, sintassi ineccepibile, rifiuto di patetismo e retorica. Leggile con calma e dimmi quale ti sembra più vicina a ciò che cerchi.

--- VARIANTE A: SOCIOLOGICA ---
Maria era cresciuta in una casa dove il denaro non mancava soltanto come mezzo, ma come misura di possibilità, e quel difetto di base aveva finito per educarla a una prudenza che, col tempo, si era trasformata in disciplina dell'assenza.

--- VARIANTE B: EVOCATIVA ---
L'infanzia di Maria aveva il rumore dei bicchieri posati male sul tavolo e un odore stanco che restava nelle tende; da lì aveva imparato la forma minuta della rinuncia, prima ancora di darle un nome.

--- VARIANTE C: PSICODINAMICA ---
Per Maria il bisogno non coincideva mai con una richiesta semplice, perché ogni domanda d'aiuto riapriva il timore di dipendere da qualcuno, e quel timore aveva radici antiche, profonde, quasi automatiche.

--- NOTE STILISTICHE ---
Per la Variante A: privilegia struttura, condizionamenti e posizione sociale.
Per la Variante B: concentra il peso del testo su atmosfera, immagine e memoria sensoriale.
Per la Variante C: scava nei meccanismi di difesa e nelle ambivalenze del soggetto.

--- DOMANDE GUIDA ---
1. Quale direzione ti sembra più affine al cuore di ciò che vuoi esprimere?
2. C'è un elemento di una variante che vorresti vedere integrato in un'altra?
3. Vuoi che sviluppi ulteriormente una delle tre direzioni?
"""


def validate_structure(text: str) -> list[str]:
    errors: list[str] = []
    current_index = -1
    for header in REQUIRED_HEADERS:
        next_index = text.find(header)
        if next_index == -1:
            errors.append(f"Header mancante: {header}")
        elif next_index < current_index:
            errors.append(f"Ordine errato per: {header}")
        else:
            current_index = next_index
    return errors


def extract_variant_blocks(text: str) -> dict[str, str]:
    pattern = re.compile(
        r"--- VARIANTE A: SOCIOLOGICA ---\n(?P<a>.*?)\n--- VARIANTE B: EVOCATIVA ---\n(?P<b>.*?)\n--- VARIANTE C: PSICODINAMICA ---\n(?P<c>.*?)\n--- NOTE STILISTICHE ---",
        re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        return {}
    return {key: value.strip() for key, value in match.groupdict().items()}


def validate_questions(text: str) -> list[str]:
    errors: list[str] = []
    questions = re.findall(r"^\d+\.\s+.+$", text, flags=re.MULTILINE)
    if len(questions) < 3:
        errors.append("Domande guida insufficienti: ne servono almeno 3.")
    return errors


def validate_forbidden_words(text: str) -> list[str]:
    errors: list[str] = []
    lowered = text.lower()
    for word in sorted(FORBIDDEN_WORDS):
        if re.search(rf"\b{re.escape(word)}\b", lowered):
            errors.append(f"Parola vietata trovata: {word}")
    if "!" in text:
        errors.append("Esclamazioni non ammesse.")
    return errors


def validate_sentence_profile(blocks: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for label, block in blocks.items():
        sentences = [piece.strip() for piece in re.split(r"(?<=[.!?])\s+", block) if piece.strip()]
        if not sentences:
            errors.append(f"Variante {label.upper()} vuota.")
            continue
        words = re.findall(r"\b[\wÀ-ÿ'-]+\b", block)
        average = len(words) / len(sentences)
        if average < 12:
            errors.append(f"Variante {label.upper()} troppo breve o telegrafica: media parole/frase {average:.1f}.")
        if average > 45:
            errors.append(f"Variante {label.upper()} eccessivamente estesa: media parole/frase {average:.1f}.")
    return errors


def run_checks(text: str) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_structure(text))
    blocks = extract_variant_blocks(text)
    if not blocks:
        errors.append("Impossibile estrarre correttamente le tre varianti.")
    else:
        errors.extend(validate_sentence_profile(blocks))
    errors.extend(validate_questions(text))
    errors.extend(validate_forbidden_words(text))
    return errors


def load_text(file_path: str | None, use_sample: bool) -> str:
    if use_sample:
        return SAMPLE_OUTPUT
    if file_path:
        return Path(file_path).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida il formato base del Creative Writer.")
    parser.add_argument("--file", help="Percorso del file da validare.")
    parser.add_argument("--sample", action="store_true", help="Valida un esempio integrato.")
    args = parser.parse_args()

    text = load_text(args.file, args.sample)
    if not text.strip():
        print("Nessun testo da validare. Usa --sample, --file oppure stdin.")
        return 1

    errors = run_checks(text)
    if errors:
        print("VALIDAZIONE FALLITA")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALIDAZIONE OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
