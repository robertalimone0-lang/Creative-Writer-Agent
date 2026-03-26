from __future__ import annotations

import streamlit as st

from creative_writer import CreativeWriterEngine, VariantPack
from italian_tools import ItalianLinguisticStudio
from open_resources import OpenResourcesHub
from test import run_checks

st.set_page_config(page_title="Creative Writer AI", layout="wide")


def init_state() -> None:
    if "engine" not in st.session_state:
        st.session_state.engine = CreativeWriterEngine()
    if "working_text" not in st.session_state:
        st.session_state.working_text = ""
    if "active_source_text" not in st.session_state:
        st.session_state.active_source_text = ""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "prompt": "",
                "display": (
                    "Portami un testo oppure incollalo nel testo di lavoro qui a sinistra. "
                    "Poi parlami come faresti con un chatbot: dimmi cosa vuoi ottenere, quale timbro vuoi "
                    "spingere, cosa vuoi trattenere, cosa vuoi eliminare."
                ),
                "pack": None,
                "structured_output": "",
                "errors": [],
                "source_text": "",
            }
        ]
    if "last_pack" not in st.session_state:
        st.session_state.last_pack = None
    if "last_structured_output" not in st.session_state:
        st.session_state.last_structured_output = ""
    if "resource_hub" not in st.session_state:
        st.session_state.resource_hub = OpenResourcesHub()
    if "linguistic_studio" not in st.session_state:
        st.session_state.linguistic_studio = ItalianLinguisticStudio()
    if "resource_query" not in st.session_state:
        st.session_state.resource_query = ""
    if "resource_payload" not in st.session_state:
        st.session_state.resource_payload = None
    if "languagetool_url" not in st.session_state:
        st.session_state.languagetool_url = "http://localhost:8081/v2/check"
    if "grammar_payload" not in st.session_state:
        st.session_state.grammar_payload = None
    if "spacy_payload" not in st.session_state:
        st.session_state.spacy_payload = None
    if "preference_memory" not in st.session_state:
        st.session_state.preference_memory = {
            "preferred_direction": "",
            "rejected_directions": [],
            "desired_traits": [],
            "avoid_traits": [],
            "feedback_log": [],
        }


def generate_response(user_prompt: str) -> None:
    prompt = user_prompt.strip()
    source_text, user_note, source_mode = resolve_source_and_note(prompt)

    if not source_text:
        return

    update_preference_memory(prompt)
    pack = engine.transform(
        source_text,
        user_note=user_note,
        preference_memory=st.session_state.preference_memory,
    )
    structured_output = pack.to_structured_text()
    errors = run_checks(structured_output)

    st.session_state.chat_messages.append(
        {
            "role": "user",
            "prompt": prompt,
            "display": prompt,
        }
    )
    st.session_state.chat_messages.append(
        {
            "role": "assistant",
            "prompt": prompt,
            "display": build_assistant_reply(source_mode),
            "pack": pack,
            "structured_output": structured_output,
            "errors": errors,
            "source_text": source_text,
            "memory_snapshot": memory_summary(),
        }
    )
    st.session_state.last_pack = pack
    st.session_state.last_structured_output = structured_output
    st.session_state.active_source_text = source_text


def resolve_source_and_note(prompt: str) -> tuple[str, str, str]:
    working_text = st.session_state.working_text.strip()
    active_source = st.session_state.active_source_text.strip()

    if working_text:
        return working_text, prompt, "working"
    if active_source and looks_like_instruction(prompt):
        return active_source, prompt, "memory"
    return prompt, "", "fresh"


def looks_like_instruction(prompt: str) -> bool:
    lowered = prompt.lower().strip()
    if not lowered:
        return False
    instruction_starts = (
        "rendi",
        "riscrivi",
        "prova",
        "spingi",
        "accentua",
        "alleggerisci",
        "approfondisci",
        "sviluppa",
        "mantieni",
        "evita",
        "scarta",
        "togli",
        "riduci",
        "aumenta",
        "continua",
        "riparti",
        "adesso",
        "meno",
        "più",
        "piu",
        "preferisco",
        "la a",
        "la b",
        "la c",
    )
    if lowered.startswith(instruction_starts):
        return True
    if len(lowered.split()) <= 12 and any(
        token in lowered for token in ("più", "piu", "meno", "variante", "metafore", "ritmo", "tono")
    ):
        return True
    return False


def build_assistant_reply(source_mode: str) -> str:
    if source_mode == "working":
        return "Ho lavorato sul testo di lavoro attivo. Qui sotto trovi le tre direzioni."
    if source_mode == "memory":
        return "Sto continuando a lavorare sul testo già attivo nella conversazione. Qui sotto trovi la nuova risposta."
    return "Ho preso il tuo ultimo messaggio come testo di partenza. Qui sotto trovi le tre direzioni."


def use_variant_as_working_text(variant_name: str) -> None:
    pack = st.session_state.last_pack
    if not pack:
        return
    variant_map = {
        "A": pack.sociological,
        "B": pack.evocative,
        "C": pack.psychodynamic,
    }
    chosen_text = variant_map.get(variant_name, "")
    st.session_state.working_text = chosen_text
    st.session_state.active_source_text = chosen_text
    direction_map = {
        "A": "sociological",
        "B": "evocative",
        "C": "psychodynamic",
    }
    direction = direction_map.get(variant_name, "")
    if direction:
        st.session_state.preference_memory["preferred_direction"] = direction
        rejected = [item for item in st.session_state.preference_memory.get("rejected_directions", []) if item != direction]
        st.session_state.preference_memory["rejected_directions"] = rejected
        st.session_state.preference_memory["feedback_log"].append(f"Preferita variante {variant_name}.")


def clear_chat() -> None:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "prompt": "",
            "display": (
                "Conversazione azzerata. Incolla un nuovo testo oppure parlami direttamente da qui, "
                "e ripartiamo."
            ),
            "pack": None,
            "structured_output": "",
            "errors": [],
            "source_text": "",
        }
    ]
    st.session_state.last_pack = None
    st.session_state.last_structured_output = ""
    st.session_state.active_source_text = ""
    st.session_state.preference_memory = {
        "preferred_direction": "",
        "rejected_directions": [],
        "desired_traits": [],
        "avoid_traits": [],
        "feedback_log": [],
    }


def lookup_resources() -> None:
    query = st.session_state.resource_query.strip()
    if not query:
        return
    st.session_state.resource_payload = resource_hub.lookup_term(query)


def grammar_check_working_text() -> None:
    text = st.session_state.working_text.strip()
    if not text:
        st.session_state.grammar_payload = {
            "available": False,
            "message": "Inserisci prima un testo di lavoro.",
            "matches": [],
        }
        return
    st.session_state.grammar_payload = resource_hub.check_with_languagetool(
        text,
        st.session_state.languagetool_url,
    )


def analyze_working_text() -> None:
    text = st.session_state.working_text.strip()
    st.session_state.spacy_payload = linguistic_studio.analyze_text(text)


def update_preference_memory(prompt: str) -> None:
    lowered = prompt.lower()
    memory = st.session_state.preference_memory

    if any(token in lowered for token in ("azzera preferenze", "riparti da zero", "reset preferenze")):
        memory["preferred_direction"] = ""
        memory["rejected_directions"] = []
        memory["desired_traits"] = []
        memory["avoid_traits"] = []
        memory["feedback_log"] = ["Preferenze azzerate su richiesta."]
        return

    direction_keywords = {
        "sociological": ("sociologica", "sociologico", "osservativa", "osservativo"),
        "evocative": ("evocativa", "evocativo", "atmosferica", "atmosferico"),
        "psychodynamic": ("psicodinamica", "psicodinamico", "analitica", "analitico", "clinica", "clinico"),
    }

    positive_cues = ("preferisco", "mi piace", "tieni", "mantieni", "vorrei più", "spingi", "punta su")
    negative_cues = ("non va", "non mi piace", "evita", "meno", "scarta", "rifiuta", "non accetto", "troppo")

    for direction, terms in direction_keywords.items():
        if any(term in lowered for term in terms):
            if any(cue in lowered for cue in positive_cues):
                memory["preferred_direction"] = direction
                memory["rejected_directions"] = [
                    item for item in memory["rejected_directions"] if item != direction
                ]
                memory["feedback_log"].append(f"Preferenza verso {direction}.")
            if any(cue in lowered for cue in negative_cues):
                rejected = memory.setdefault("rejected_directions", [])
                if direction not in rejected:
                    rejected.append(direction)
                if memory.get("preferred_direction") == direction:
                    memory["preferred_direction"] = ""
                memory["feedback_log"].append(f"Rifiuto di {direction}.")

    desired_map = {
        "asciutto": ("asciutto", "asciutta"),
        "più breve": ("più breve", "piu breve", "frasi più brevi", "frasi piu brevi"),
        "più lungo": ("più lungo", "piu lungo", "frasi più lunghe", "frasi piu lunghe"),
        "più denso": ("più denso", "piu denso", "più stratificato", "piu stratificato"),
        "ritmo": ("più ritmo", "piu ritmo", "ritmo", "più dinamico", "piu dinamico"),
    }
    avoid_map = {
        "metafore": ("meno metafore", "evita metafore", "troppo metaforico", "troppo evocativo"),
        "retorica": ("meno retorica", "evita retorica", "retorico"),
        "enfasi": ("meno enfasi", "evita enfasi", "enfatico", "enfatica"),
        "psicologismo": ("meno psicologia", "meno psicologismo", "troppo analitico", "troppo clinico"),
    }

    for label, cues in desired_map.items():
        if any(cue in lowered for cue in cues):
            append_unique(memory["desired_traits"], label)
            memory["feedback_log"].append(f"Richiesto: {label}.")

    for label, cues in avoid_map.items():
        if any(cue in lowered for cue in cues):
            append_unique(memory["avoid_traits"], label)
            memory["feedback_log"].append(f"Da evitare: {label}.")

    memory["feedback_log"] = memory["feedback_log"][-20:]


def append_unique(bucket: list[str], value: str) -> None:
    if value not in bucket:
        bucket.append(value)


def memory_summary() -> str:
    memory = st.session_state.preference_memory
    fragments = []
    preferred = memory.get("preferred_direction", "")
    if preferred:
        readable = {
            "sociological": "prevalenza sociologica",
            "evocative": "prevalenza evocativa",
            "psychodynamic": "prevalenza psicodinamica",
        }
        fragments.append(readable.get(preferred, preferred))
    desired = memory.get("desired_traits", [])
    avoid = memory.get("avoid_traits", [])
    rejected = memory.get("rejected_directions", [])
    if desired:
        fragments.append("tieni " + ", ".join(desired[:3]))
    if avoid:
        fragments.append("evita " + ", ".join(avoid[:3]))
    if rejected:
        readable_rejected = {
            "sociological": "sociologica",
            "evocative": "evocativa",
            "psychodynamic": "psicodinamica",
        }
        fragments.append(
            "scarta " + ", ".join(readable_rejected.get(item, item) for item in rejected[:3])
        )
    return " | ".join(fragments)


def render_pack(pack: VariantPack, structured_output: str, errors: list[str], message_key: str) -> None:
    tab_a, tab_b, tab_c, tab_full = st.tabs(
        ["Variante A", "Variante B", "Variante C", "Output completo"]
    )

    with tab_a:
        st.text_area("Sociologica", value=pack.sociological, height=220, key=f"sociologica_{message_key}")
        st.caption(pack.notes["a"])
    with tab_b:
        st.text_area("Evocativa", value=pack.evocative, height=220, key=f"evocativa_{message_key}")
        st.caption(pack.notes["b"])
    with tab_c:
        st.text_area("Psicodinamica", value=pack.psychodynamic, height=220, key=f"psicodinamica_{message_key}")
        st.caption(pack.notes["c"])
    with tab_full:
        st.text_area(
            "Risposta strutturata",
            value=structured_output,
            height=360,
            key=f"structured_{message_key}",
            help="Questo blocco è selezionabile, copiabile e riutilizzabile.",
        )
        if errors:
            st.error("La validazione segnala ancora questi punti:")
            for error in errors:
                st.write(f"- {error}")
        else:
            st.success("Formato strutturale valido")

    st.markdown("**Domande guida**")
    for index, question in enumerate(pack.questions, start=1):
        st.write(f"{index}. {question}")


init_state()
engine = st.session_state.engine
resource_hub = st.session_state.resource_hub
linguistic_studio = st.session_state.linguistic_studio

st.title("Creative Writer AI")
st.caption("Una chat di lavoro per trasformare il testo senza perdere voce, ritmo e tenuta stilistica.")

with st.sidebar:
    st.markdown("### Testo di lavoro")
    st.text_area(
        "Base attiva",
        key="working_text",
        height=320,
        help="Se questo campo è pieno, i tuoi messaggi vengono trattati come istruzioni sul testo attivo.",
    )

    st.markdown("### Regole attive")
    st.write("- Voce originale preservata")
    st.write("- Frase medio-lunga")
    st.write("- Ritmo dinamico ma non frenetico")
    st.write("- Niente patetismo, retorica o cliché")
    st.write("- Tre varianti obbligatorie")

    st.markdown("### Azioni rapide")
    action_cols = st.columns(3)
    with action_cols[0]:
        st.button("Usa A", use_container_width=True, on_click=use_variant_as_working_text, args=("A",))
    with action_cols[1]:
        st.button("Usa B", use_container_width=True, on_click=use_variant_as_working_text, args=("B",))
    with action_cols[2]:
        st.button("Usa C", use_container_width=True, on_click=use_variant_as_working_text, args=("C",))

    st.button("Nuova chat", use_container_width=True, on_click=clear_chat)

    st.markdown("### Memoria del testo")
    if st.session_state.active_source_text.strip():
        excerpt = st.session_state.active_source_text.strip()
        if len(excerpt) > 180:
            excerpt = excerpt[:180].rsplit(" ", 1)[0] + "..."
        st.write(excerpt)
    else:
        st.write("Nessun testo attivo in memoria.")

    st.markdown("### Memoria della chat")
    summary = memory_summary()
    if summary:
        st.write(summary)
    else:
        st.write("Nessuna preferenza attiva.")

    feedback_log = st.session_state.preference_memory.get("feedback_log", [])
    if feedback_log:
        st.caption("Ultimi apprendimenti")
        for item in feedback_log[-5:]:
            st.write(f"- {item}")

main_col, side_col = st.columns([0.72, 0.28])

with main_col:
    for index, message in enumerate(st.session_state.chat_messages):
        with st.chat_message(message["role"]):
            st.write(message["display"])
            pack = message.get("pack")
            if pack:
                render_pack(
                    pack,
                    message.get("structured_output", ""),
                    message.get("errors", []),
                    message_key=f"msg_{index}",
                )

    user_prompt = st.chat_input(
        "Scrivimi come a un chatbot: 'rendi più atmosferico', 'scava il conflitto', 'riparti da questa bozza'..."
    )
    if user_prompt:
        generate_response(user_prompt)
        st.rerun()

with side_col:
    st.markdown("### Come usarla")
    st.write("1. Incolla una bozza nel testo di lavoro, oppure scrivimi direttamente in chat.")
    st.write("2. Chiedimi una trasformazione: ritmo, tono, atmosfera, profondità analitica.")
    st.write("3. Confronta le tre varianti e porta A, B o C nel testo di lavoro.")

    st.markdown("### Ultima risposta")
    if st.session_state.last_structured_output:
        st.text_area(
            "Estratto completo",
            value=st.session_state.last_structured_output,
            height=260,
            key="latest_structured_output",
        )
    else:
        st.info("Non hai ancora generato una risposta.")

    st.markdown("### Risorse aperte")
    st.caption("Dizionari aperti, testi in pubblico dominio e aggancio opzionale a un correttore open-source locale.")
    st.text_input(
        "Lemma o autore",
        key="resource_query",
        help="Cerca una parola per definizioni, sinonimi e contrari, oppure un autore/titolo per Wikisource.",
    )
    resource_actions = st.columns(2)
    with resource_actions[0]:
        st.button("Cerca fonti", use_container_width=True, on_click=lookup_resources)
    with resource_actions[1]:
        st.button(
            "Controlla grammatica",
            use_container_width=True,
            on_click=grammar_check_working_text,
        )

    st.button(
        "Analizza italiano",
        use_container_width=True,
        on_click=analyze_working_text,
    )

    st.text_input(
        "LanguageTool URL",
        key="languagetool_url",
        help="Esempio locale: http://localhost:8081/v2/check",
    )

    resource_payload = st.session_state.resource_payload
    if resource_payload:
        lexical = resource_payload.get("lexical")
        texts = resource_payload.get("texts", [])

        if lexical:
            st.markdown("**Lessico da Wiktionary**")
            st.markdown(f"[{lexical.title}]({lexical.page_url})")
            if lexical.definitions:
                st.write("Definizioni:")
                for item in lexical.definitions:
                    st.write(f"- {item}")
            if lexical.synonyms:
                st.write("Sinonimi:")
                st.write(", ".join(lexical.synonyms))
            if lexical.antonyms:
                st.write("Contrari:")
                st.write(", ".join(lexical.antonyms))
        else:
            st.info("Nessuna voce lessicale trovata su Wiktionary per questa ricerca.")

        st.markdown("**Testi pubblici da Wikisource**")
        if texts:
            for item in texts:
                st.markdown(f"- [{item.title}]({item.url})")
        else:
            st.write("Nessun risultato disponibile.")

    grammar_payload = st.session_state.grammar_payload
    if grammar_payload:
        if grammar_payload.get("available"):
            st.success(grammar_payload.get("message", ""))
            for match in grammar_payload.get("matches", []):
                replacements = ", ".join(match.get("replacements", [])) or "nessun suggerimento"
                st.write(f"- {match.get('message', '')} | Suggerimenti: {replacements}")
        else:
            st.info(grammar_payload.get("message", ""))

    spacy_payload = st.session_state.spacy_payload
    if spacy_payload:
        st.markdown("### Analisi italiana")
        if spacy_payload.get("available"):
            st.success(spacy_payload.get("message", ""))
        else:
            st.info(spacy_payload.get("message", ""))

        metrics = st.columns(3)
        metrics[0].metric("Modello", spacy_payload.get("model", ""))
        metrics[1].metric("Frasi", spacy_payload.get("sentence_count", 0))
        metrics[2].metric("Media parole", spacy_payload.get("average_sentence_length", 0))

        key_lemmas = spacy_payload.get("key_lemmas", [])
        if key_lemmas:
            st.write("Lemmi chiave:")
            st.write(", ".join(key_lemmas))

        repeated_lemmas = spacy_payload.get("repeated_lemmas", [])
        if repeated_lemmas:
            st.write("Lemmi ripetuti:")
            st.write(", ".join(repeated_lemmas))

        openings = spacy_payload.get("sentence_openings", [])
        if openings:
            st.write("Attacchi di frase:")
            st.write(", ".join(openings))

        pos_profile = spacy_payload.get("pos_profile", [])
        if pos_profile:
            st.write("Profilo grammaticale:")
            st.write(", ".join(f"{item['tag']}: {item['count']}" for item in pos_profile))

        named_entities = spacy_payload.get("named_entities", [])
        if named_entities:
            st.write("Entità rilevate:")
            st.write(", ".join(f"{item['text']} ({item['label']})" for item in named_entities))
