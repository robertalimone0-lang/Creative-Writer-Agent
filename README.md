# Creative Writer AI (Flask)

Creative Writer AI is a Flask web app that generates six stylistic rewrites of Italian text.
It replaces the old Streamlit chat and does not rely on v0 or Next.js.

## Features
- 6 variants: sociological, evocative, psychodynamic, lyrical, minimal, dialogic
- Upload TXT/MD/PDF/DOCX or paste text directly
- Optional Italian linguistic analysis (spaCy)
- Open resources lookup (Wiktionary + Wikisource)
- Structured output plus validation checks

## Requirements
- Python 3.11+

Install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Optional spaCy model:
```bash
python -m spacy download it_core_news_sm
```

## Run
```bash
venv/bin/python app.py
```
Open:
```
http://127.0.0.1:5000
```

## API
- `GET /` -> Web UI
- `POST /api/refine` -> Form-data: `text`, `note`, `include_analysis`, `file`
- `POST /api/analyze` -> JSON: `{ "text": "..." }`
- `GET /api/resources?q=term`

## Main Files
- `app.py`: Flask web app and API routes
- `creative_writer.py`: transformation engine
- `open_resources.py`: open resources lookup
- `italian_tools.py`: Italian linguistic analysis
- `templates/index.html`: main UI
- `static/styles.css`, `static/app.js`: UI assets
- `test.py`: output validator

## License
MIT (see LICENSE)
