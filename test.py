REQUIRED_MARKERS = [
    "=== VARIANTE SOCIOLOGICA ===",
    "=== VARIANTE EVOCATIVA ===",
    "=== VARIANTE PSICODINAMICA ===",
    "=== VARIANTE LIRICA ===",
    "=== VARIANTE MINIMALE ===",
    "=== VARIANTE DIALOGICA ===",
    "=== DOMANDE GUIDA ===",
]


def run_checks(text: str) -> list[str]:
    errors: list[str] = []
    cleaned = (text or "").strip()
    if not cleaned:
        errors.append("Il testo e vuoto")
        return errors

    word_count = len(cleaned.split())
    if word_count < 25:
        errors.append("Il testo e molto breve per una risposta completa")

    for marker in REQUIRED_MARKERS:
        if marker not in cleaned:
            errors.append(f"Manca la sezione: {marker}")

    if "=== DOMANDE GUIDA ===" in cleaned:
        tail = cleaned.split("=== DOMANDE GUIDA ===", 1)[-1]
        question_lines = [
            line.strip()
            for line in tail.splitlines()
            if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6."))
        ]
        if len(question_lines) < 2:
            errors.append("Le domande guida sembrano incomplete")

    return errors
