from __future__ import annotations

import anthropic
import streamlit as st
import os
import re
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
        try:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
        except:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation_history: List[Dict[str, str]] = []
        self.user_preferences: List[str] = []
    
    def _build_system_prompt(self) -> str:
        return """You are an expert assistant for creative writers transforming texts.

ABSOLUTE STYLISTIC RULES:
- Preserve original voice unless explicit deviation is requested
- Monitored syntax, medium-long sentences, dynamic but not frantic rhythm
- Precise vocabulary, rich but not ornate
- ABSOLUTE REJECTION of pathos, rhetoric, clichés, emotional stereotypes
- DO NOT use: easy tears, declared emotion, clichés, commonplaces
- DO NOT use words like "incredible", "wonderful", "terrible" without concrete anchor
- SHOW through precise and meaningful details
- LET emotion emerge from the situation
- Give expressive weight to rhythm, syntax, and verb choice

Three mandatory stylistic directions:
1. SOCIOLOGICAL: emphasis on social context, relationships, structures
2. EVOCATIVE: atmosphere, images, sensory suggestions
3. PSYCHODYNAMIC: inner motivations, conflicts, psychological dynamics"""
    
    def _build_user_prompt(self, text: str, user_note: str = "", preference_memory: List[str] = None) -> str:
        preferences = ""
        if preference_memory and len(preference_memory) > 0:
            preferences = f"\nPreferences already expressed: {,
.join(preference_memory[-3:])}\n"
        
        user_note_text = f"\nUSER NOTE:\n{user_note}\n" if user_note else ""
        
        return f"""{preferences}{user_note_text}

ORIGINAL TEXT:
"{text}"

INSTRUCTIONS:
Transform the text into the three stylistic variants

STRICTLY RETURN THIS FORMAT:
--- VARIANT A: SOCIOLOGICAL ---
[transformed text]

--- VARIANT B: EVOCATIVE ---
[transformed text]

--- VARIANT C: PSYCHODYNAMIC ---
[transformed text]

--- STYLISTIC NOTES ---
[explanation of choices]

--- GUIDING QUESTIONS ---
[3 questions for further exploration]"""
    
    def transform(self, text: str, user_note: str = "", preference_memory: List[str] = None) -> VariantPack:
        self.conversation_history.append({"role": "user", "content": text})
        
        response = self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=3000,
            system=self._build_system_prompt(),
            messages=[{"role": "user", "content": self._build_user_prompt(text, user_note, preference_memory)}]
        )
        
        result = response.content[0].text
        
        sociological = re.search(r'--- VARIANT A: SOCIOLOGICAL ---\n(.*?)\n--- VARIANT B:', result, re.DOTALL)
        evocative = re.search(r'--- VARIANT B: EVOCATIVE ---\n(.*?)\n--- VARIANT C:', result, re.DOTALL)
        psychodynamic = re.search(r'--- VARIANT C: PSYCHODYNAMIC ---\n(.*?)\n--- STYLISTIC NOTES ---', result, re.DOTALL)
        notes = re.search(r'--- STYLISTIC NOTES ---\n(.*?)\n--- GUIDING QUESTIONS ---', result, re.DOTALL)
        questions = re.search(r'--- GUIDING QUESTIONS ---\n(.*?)$', result, re.DOTALL)
        
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
        self.conversation_history.append({"role": "assistant", "content": f"Working text updated: {text[:200]}..."})
