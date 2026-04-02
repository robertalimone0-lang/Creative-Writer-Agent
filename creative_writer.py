from dataclasses import dataclass
from typing import List, Dict, Optional
import re
import random

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
    def __init__(self, api_key: Optional[str] = None):
        self.use_openai = False
        try:
            import spacy
            self.nlp = spacy.load("it_core_news_sm")
        except:
            self.nlp = None
        
    def transform(self, source_text: str, user_note: str = "", preference_memory: Dict = None) -> VariantPack:
        if preference_memory is None:
            preference_memory = {}
        
        doc = None
        if self.nlp:
            doc = self.nlp(source_text[:5000])
        
        sociological = self._apply_sociological(source_text, doc, user_note)
        evocative = self._apply_evocative(source_text, doc, user_note)
        psychodynamic = self._apply_psychodynamic(source_text, doc, user_note)
        lyrical = self._apply_lyrical(source_text, doc, user_note)
        minimal = self._apply_minimal(source_text, doc, user_note)
        dialogic = self._apply_dialogic(source_text, doc, user_note)
        
        questions = [
            "Quale direzione preferisci?",
            "Cosa vorresti potenziare?",
            "Cosa vorresti attenuare?"
        ]
        
        notes = {
            "a": "Sociologica: evidenzia relazioni sociali e contesto",
            "b": "Evocativa: usa immagini e atmosfere",
            "c": "Psicodinamica: esplora motivazioni interiori",
            "d": "Lirica: cura ritmo e musicalità",
            "e": "Minimale: essenziale e diretto",
            "f": "Dialogica: enfasi sulla voce narrante"
        }
        
        return VariantPack(
            sociological=sociological,
            evocative=evocative,
            psychodynamic=psychodynamic,
            lyrical=lyrical,
            minimal=minimal,
            dialogic=dialogic,
            questions=questions,
            notes=notes
        )
    
    def _apply_sociological(self, text: str, doc, note: str) -> str:
        result = text
        social_terms = ["nel contesto sociale", "nelle relazioni tra", "nel sistema di", "le dinamiche di potere"]
        if len(text.split()) > 50:
            result = f"[ANALISI SOCIOLOGICA]\n\n{text}\n\n[CONTESTO: evidenziare le relazioni sociali e le strutture di potere implicite]"
        else:
            result = f"Dal punto di vista sociale: {text[:len(text)//2]}… nel contesto delle relazioni che la definiscono."
        
        if note:
            result += f"\n\nNota: {note}"
        return result
    
    def _apply_evocative(self, text: str, doc, note: str) -> str:
        evocative_phrases = [
            "come un'ombra che si allunga",
            "nel silenzio che avvolge",
            "con la leggerezza di una foglia",
            "come un ricordo che riaffiora",
            "tra le pieghe del tempo"
        ]
        
        if len(text.split()) > 50:
            result = f"[ATMOSFERA EVOCATIVA]\n\n{text}\n\n[Sfumature: immagini sensoriali, luci e ombre, atmosfere sospese]"
        else:
            result = f"{text} {random.choice(evocative_phrases)}."
        
        if note:
            result += f"\n\nNota: {note}"
        return result
    
    def _apply_psychodynamic(self, text: str, doc, note: str) -> str:
        if len(text.split()) > 50:
            result = f"[LETTURA PSICODINAMICA]\n\n{text}\n\n[In profondità: esplorare i conflitti interiori e le motivazioni inconsce]"
        else:
            result = f"Sul piano interiore: {text} Rivelando un bisogno profondo di {random.choice(['appartenenza', 'riconoscimento', 'autonomia', 'sicurezza'])}."
        
        if note:
            result += f"\n\nNota: {note}"
        return result
    
    def _apply_lyrical(self, text: str, doc, note: str) -> str:
        if len(text.split()) > 50:
            result = f"[VARIAZIONE LIRICA]\n\n{text}\n\n[Ritmo: cesure, assonanze, musicalità della prosa]"
        else:
            result = f"{text} Il suo ritmo si fa canto, le parole diventano note."
        
        if note:
            result += f"\n\nNota: {note}"
        return result
    
    def _apply_minimal(self, text: str, doc, note: str) -> str:
        sentences = re.split(r'[.!?]+', text)
        short_sentences = []
        for sent in sentences[:10]:
            words = sent.split()[:8]
            if words:
                short_sentences.append(' '.join(words))
        
        if len(text.split()) > 50:
            result = f"[VERSIONE MINIMALE]\n\n{text}\n\n[Essenziale: eliminare ridondanze, stringere, andare al nocciolo]"
        else:
            result = '. '.join(short_sentences) + '.'
        
        if note:
            result += f"\n\nNota: {note}"
        return result
    
    def _apply_dialogic(self, text: str, doc, note: str) -> str:
        if len(text.split()) > 50:
            result = f"[MONOLOGO INTERIORE]\n\n{text}\n\n[Voce: enfatizzare la prospettiva soggettiva, il punto di vista narrante]"
        else:
            result = f"Io penso che {text} Mi sembra di vedere {text[:30]}…"
        
        if note:
            result += f"\n\nNota: {note}"
        return result


def extract_text_from_pdf(file) -> str:
    try:
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Errore PDF: {e}"


def extract_text_from_docx(file) -> str:
    try:
        import docx
        doc = docx.Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        return f"Errore DOCX: {e}"
