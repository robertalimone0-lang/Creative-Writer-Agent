# Creative Writer Agent

`Creative Writer Agent` è una web app in Streamlit per lavorare sui testi come in una chat: conserva il testo attivo, raccoglie i feedback dell'utente e lo trasforma in tre direzioni stilistiche coerenti con un perimetro letterario preciso.

## Identità

Il progetto lavora su testi italiani con questi vincoli principali:

- voce originale preservata, salvo richiesta esplicita di deviazione
- sintassi sorvegliata, frase medio-lunga, ritmo dinamico ma non frenetico
- lessico preciso, ricco ma non aulico
- rifiuto di patetismo, retorica, cliché, stereotipi emotivi
- tre direzioni stilistiche obbligatorie: `sociologica`, `evocativa`, `psicodinamica`
- memoria conversazionale del testo attivo e delle preferenze espresse in chat

## Esperienza

L'app offre:

- una chat centrale per chiedere trasformazioni iterative
- un testo di lavoro persistente, riusato nei turni successivi
- tre varianti strutturate dello stesso testo
- memoria delle preferenze, per evitare di ripetere ogni volta il contesto
- risorse aperte per dizionari, sinonimi, contrari e riferimenti in pubblico dominio

## Struttura attesa dell'output

Ogni trasformazione completa deve restituire:

- `--- VARIANTE A: SOCIOLOGICA ---`
- `--- VARIANTE B: EVOCATIVA ---`
- `--- VARIANTE C: PSICODINAMICA ---`
- `--- NOTE STILISTICHE ---`
- `--- DOMANDE GUIDA ---`

## Regole assolute

Non usare mai:

- lacrime facili, commozione dichiarata, patetismo
- frasi fatte, luoghi comuni, stereotipi emotivi
- retorica enfatica, aggettivi gridati, esclamazioni
- parole come `incredibile`, `meraviglioso`, `terribile` senza un'ancora concreta

Fare invece:

- mostrare attraverso dettagli precisi e significativi
- lasciare emergere l'emozione dalla situazione
- affidare peso espressivo a ritmo, sintassi e scelta verbale
- preferire sottigliezza, precisione e continuità stilistica

## File principali

- `README.md`: manifesto e istruzioni base
- `requirements.txt`: dipendenze del progetto
- `test.py`: validatore locale del formato e dei divieti base
- `creative_writer.py`: motore locale di trasformazione
- `app_web.py`: interfaccia chat-like in Streamlit
- `open_resources.py`: accesso a risorse aperte
- `italian_tools.py`: analisi linguistica italiana con fallback locale

## Risorse aperte integrate

La base attuale può consultare:

- `Wiktionary` per definizioni, sinonimi e contrari quando presenti
- `Wikisource` per testi in pubblico dominio e riferimenti stilistici aperti
- `LanguageTool` come correttore grammaticale open-source, se avvii un server locale
- `spaCy` per analisi morfosintattica italiana, con fallback a pipeline locale minimale

Nota importante:

- `open source` e `open access` non equivalgono a “tutti i libri”.
- Per i libri, l'app deve limitarsi a testi in pubblico dominio o con licenza aperta.
- Per autori contemporanei o opere coperte da diritto d'autore, è meglio lavorare su estratti forniti da chi scrive o su corpora autorizzati.

## Avvio rapido

```bash
cd "/Users/robertalimone/Documents/writers-workshop"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python test.py --sample
streamlit run app_web.py
```

L'app locale sarà disponibile di default su `http://localhost:8501`.

## Deploy su Streamlit Community Cloud

Usa come file principale:

- `app_web.py`

Se la schermata richiede un URL GitHub del file Python, incolla:

- `https://github.com/robertalimone0-lang/Creative-Writer-Agent/blob/main/app_web.py`

## Prossimi passi

1. Raffinare la qualità creativa delle varianti.
2. Rafforzare la memoria stilistica tra sessioni.
3. Collegare in modo più profondo le risorse aperte al motore di trasformazione.
4. Integrare controlli automatici su fedeltà, coerenza e deriva stilistica.
