from __future__ import annotations

import anthropic
import streamlit as st
import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class VariantPack:
    sociological: str
    evocative: str
    psychodynamic: str
    stylistic_notes: str
    guiding_questions: List[str]

class CreativeWriterEngine:
    def __init__(self):
        # Legge la chiave API prima dai secrets di Streamlit, poi dall'ambiente'
        try:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
        except:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation_history: List[Dict[str, str]] = []
        self.user_preferences: List[str] = []
    
    def _build_system_prompt(self) -> str:
        return """Sei un assistente esperto nella trasformazione di testi per scrittori creativi.
        
REGOLE STILISTICHE ASSOLUTE:
- Mantieni la voce originale, salvo richiesta esplicita di deviazione
- Sintassi sorvegliata, frase medio-lunga, ritmo dinamico ma non frenetico
- Lessico preciso, ricco ma non aulico
- RIFIUTO ASSOLUTO di patetismo, retorica, cliché, stereotipi emotivi
- NON usare: lacrime facili, commozione dichiarata, frasi fatte, luoghi comuni
- NON usare parole come "incredibile", "meraviglioso", "terribile" senza ancora concreta
- MOSTRA attraverso dettagli precisi e significativi
- LASCIA emergere l'emozione dalla situazione
- Affida peso espressivo a ritmo, sintassi e scelta verbale

Tre direzioni stilistiche obbligatorie:
1. SOCIOLOGICA: enfasi su contesto sociale, relazioni, strutture
2. EVOCATIVA: atmosfera, immagini, suggestioni sensoriali
3. PSICODINAMICA: motivazioni interiori, conflitti, dinamiche psicologiche"""
    
    def _build_user_prompt(self, text: str, instruction: str) -> str:
        preferences = ""
        if self.user_preferences:
            preferences = f"\nPreferenze già espresse: {,
.join(self.user_preferences[-3:])}\n"
        
        return f"""{preferences}

TESTO ORIGINALE:
"{text}"

ISTRUZIONI DELL'UTENTE:
{instruction if instruction else "Trasforma il testo nelle tre varianti stilistiche"}

RESTITUISCI STRETTAMENTE QUESTO FORMATO:
--- VARIANTE A: SOCIOLOGICA ---
[testo trasformato]

--- VARIANTE B: EVOCATIVA ---
[testo trasformato]

--- VARIANTE C: PSICODINAMICA ---
[testo trasformato]

--- NOTE STILISTICHE ---
[spiegazione delle scelte]

--- DOMANDE GUIDA ---
[3 domande per approfondire]"""
    
    def transform(self, text: str, instruction: str = "") -> VariantPack:
        self.conversation_history.append({"role": "user", "content": text})
        
        response = self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=3000,
            system=self._build_system_prompt(),
            messages=[{"role": "user", "content": self._build_user_prompt(text, instruction)}]
        )
        
        result = response.content[0].text
        
        import re
        sociological = re.search(r'--- VARIANTE A: SOCIOLOGICA ---\n(.*?)\n--- VARIANTE B:', result, re.DOTALL)
        evocative = re.search(r'--- VARIANTE B: EVOCATIVA ---\n(.*?)\n--- VARIANTE C:', result, re.DOTALL)
        psychodynamic = re.search(r'--- VARIANTE C: PSICODINAMICA ---\n(.*?)\n--- NOTE STILISTICHE ---', result, re.DOTALL)
        notes = re.search(r'--- NOTE STILISTICHE ---\n(.*?)\n--- DOMANDE GUIDA ---', result, re.DOTALL)
        questions = re.search(r'--- DOMANDE GUIDA ---\n(.*?)$', result, re.DOTALL)
        
        return VariantPack(
            sociological=sociological.group(1).strip() if sociological else "",
            evocative=evocative.group(1).strip() if evocative else "",
            psychodynamic=psychodynamic.group(1).strip() if psychodynamic else "",
            stylistic_notes=notes.group(1).strip() if notes else "",
            guiding_questions=[q.strip() for q in questions.group(1).split(n) if q.strip()] if questions else []
        )
    
    def add_preference(self, preference: str):
        self.user_preferences.append(preference)
    
    def set_working_text(self, text: str):
        self.conversation_history.append({"role": "assistant", "content": f"Testo di lavoro aggiornato: {text[:200]}..."})
