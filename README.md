# Creative Writer AI (Flask)

Creative Writer AI is a Flask web app that generates six stylistic rewrites of Italian text.
It replaces the old Streamlit chat with a clean, fast UI, file upload support, and a small
set of JSON endpoints.

## Identity
This project focuses on Italian prose with these guiding principles:
- Preserve the original voice unless an explicit change is requested.
- Maintain medium-long sentences and a dynamic but not frantic rhythm.
- Prefer precise vocabulary and avoid rhetorical excess.
- Avoid pathos, cliches, emotional stereotypes, and empty superlatives.
- Provide six mandatory stylistic directions: sociological, evocative, psychodynamic,
  lyrical, minimal, dialogic.

## Experience
The web app offers:
- A single workspace to paste text or upload a file (TXT/MD/PDF/DOCX).
- A director note to steer tone and rhythm.
- Six variants rendered side-by-side with notes.
- Optional Italian linguistic analysis (spaCy).
- Open resources search (Wiktionary + Wikisource).
- A structured output block and basic validation checks.

## Expected Output Format
Each transformation returns:
- `=== VARIANTE SOCIOLOGICA ===`
- `=== VARIANTE EVOCATIVA ===`
- `=== VARIANTE PSICODINAMICA ===`
- `=== VARIANTE LIRICA ===`
- `=== VARIANTE MINIMALE ===`
- `=== VARIANTE DIALOGICA ===`
- `=== DOMANDE GUIDA ===`

## Main Files
- `README.md`: this file
- `requirements.txt`: Python dependencies
- `test.py`: output validator
- `creative_writer.py`: transformation engine
- `app.py`: Flask web app and API routes
- `templates/index.html`: main UI
- `static/styles.css`, `static/app.js`: UI assets
- `open_resources.py`: open resources lookup
- `italian_tools.py`: Italian linguistic analysis

## Open Resources
The app can consult:
- Wiktionary for definitions, synonyms, and antonyms.
- Wikisource for public-domain texts.
- LanguageTool (optional) when a local server is available.
- spaCy for Italian NLP, with a lightweight fallback if the model is missing.

Note:
- "Open access" does not mean all books are allowed.
- Use public-domain works or properly licensed texts.
- For contemporary authors, prefer excerpts provided by the writer.

## Quick Start
```bash
cd /Users/robertalimone/creative-writer-ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open:
```
http://127.0.0.1:5000
```

Optional spaCy model:
```bash
python -m spacy download it_core_news_sm
```

## API
- `GET /` -> Web UI
- `POST /api/refine` -> Form-data: `text`, `note`, `include_analysis`, `file`
- `POST /api/analyze` -> JSON: `{ "text": "..." }`
- `GET /api/resources?q=term`

## License
MIT (see LICENSE)
