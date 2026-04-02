diff --git a//Users/robertalimone/creative-writer-ai/README.md b//Users/robertalimone/creative-writer-ai/README.md
new file mode 100644
--- /dev/null
+++ b//Users/robertalimone/creative-writer-ai/README.md
@@ -0,0 +1,51 @@
+# Creative Writer AI (Flask)
+
+Creative Writer AI is a lightweight web app to generate six stylistic rewrites of Italian text.
+It is now a standard Flask app (no Streamlit), with a clean UI, optional linguistic analysis,
+and open resources search.
+
+## Features
+- 6 variants: sociological, evocative, psychodynamic, lyrical, minimal, dialogic
+- Upload TXT/MD/PDF/DOCX or paste text directly
+- Optional Italian linguistic analysis (spaCy)
+- Open resources lookup (Wiktionary + Wikisource)
+- Structured output plus validation hints
+
+## Requirements
+- Python 3.11+
+- Recommended: spaCy + Italian model (optional)
+
+Install dependencies:
+```bash
+python -m venv venv
+source venv/bin/activate
+pip install -r requirements.txt
+```
+
+Optional spaCy model:
+```bash
+python -m spacy download it_core_news_sm
+```
+
+## Run
+```bash
+venv/bin/python app.py
+```
+Then open:
+```
+http://127.0.0.1:5000
+```
+
+## API
+- `GET /` -> Web UI
+- `POST /api/refine` -> Form-data: `text`, `note`, `include_analysis`, `file`
+- `POST /api/analyze` -> JSON: `{ "text": "..." }`
+- `GET /api/resources?q=term`
+
+## Notes
+- Max text length: 120,000 characters
+- Upload limit: 8 MB
+- LanguageTool checks require a local server URL
+
+## License
+MIT (see LICENSE)
