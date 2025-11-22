"""
OpenAI service for parsing natural language circuit descriptions
"""

import json
from openai import OpenAI
from app.models import CircuitSpec, SensorSpec, ActuatorSpec, LEDSpec, PowerSpec, BoardSize
from typing import Dict, Any


class AIService:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
    def parse_description(self, description: str, language: str = "it") -> Dict[str, Any]:
        """
        Parse natural language circuit description using GPT-4
        Returns a CircuitSpec and any clarification questions
        """
        
        system_prompt = """Sei un esperto di elettronica e progettazione di circuiti con ESP32.
Il tuo compito è analizzare descrizioni in linguaggio naturale di circuiti IoT e convertirle in specifiche strutturate.

REGOLE:
1. Identifica sempre il tipo di nodo (gate_controller, sensor_node, irrigation, lighting, alarm, ecc.)
2. Elenca tutti i componenti necessari: sensori, attuatori, LED, ecc.
3. Se qualcosa non è chiaro, aggiungi domande in "clarification_questions"
4. Fai assunzioni ragionevoli e documentale in "assumptions_made"
5. Usa sempre ESP32-DevKitC come microcontrollore di default
6. La scheda è sempre 10x10 cm (100x100 mm)
7. Alimentazione di default: 5V, max 2A

COMPONENTI DISPONIBILI:
- Servo: SG90 (5V, 500mA, PWM)
- Sensori: IR, ultrasuoni (HC-SR04), temperatura, umidità
- LED: rosso, verde, blu, giallo, bianco
- Attuatori: servo, relè, motori DC

ESEMPI:
Input: "Voglio un cancello con 2 servo e sensore IR"
Output: {
  "node_type": "gate_controller",
  "esp32_model": "ESP32-DevKitC",
  "actuators": [{"kind": "servo", "model": "SG90", "count": 2}],
  "sensors": [{"kind": "IR", "count": 1}],
  "status_leds": [{"color": "rosso"}, {"color": "verde"}],
  "assumptions_made": ["Aggiunti LED rosso e verde per stato"]
}

Input: "Controllo irrigazione con 3 pompe e sensore umidità"
Output: {
  "node_type": "irrigation_controller",
  "actuators": [{"kind": "pump", "count": 3}],
  "sensors": [{"kind": "humidity", "count": 1}],
  "clarification_questions": ["Che tipo di pompe? Relè o controllo diretto?"]
}

Rispondi SOLO con JSON valido, nessun testo aggiuntivo."""

        user_prompt = f"""Analizza questa descrizione di circuito e genera le specifiche:

DESCRIZIONE: {description}

Genera un JSON con questa struttura:
{{
  "node_type": "tipo_nodo",
  "description": "descrizione breve",
  "esp32_model": "ESP32-DevKitC",
  "board_size": {{"width_mm": 100, "height_mm": 100}},
  "power": {{"supply_voltage": 5.0, "max_current_ma": 2000}},
  "sensors": [{{"kind": "tipo", "count": 1, "mounting": "offboard"}}],
  "actuators": [{{"kind": "tipo", "model": "modello", "count": 1}}],
  "status_leds": [{{"color": "colore", "role": "status"}}],
  "clarification_questions": ["domanda1", "domanda2"],
  "assumptions_made": ["assunzione1", "assunzione2"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            spec_dict = json.loads(content)
            
            spec = CircuitSpec(**spec_dict)
            
            return {
                "spec": spec,
                "questions": spec.clarification_questions,
                "suggestions": spec.assumptions_made
            }
            
        except json.JSONDecodeError as e:
            return {
                "spec": None,
                "questions": [f"Non ho capito la descrizione. Puoi essere più specifico? Errore: {str(e)}"],
                "suggestions": []
            }
        except Exception as e:
            return {
                "spec": None,
                "questions": [f"Errore nell'analisi: {str(e)}. Riprova con una descrizione più dettagliata."],
                "suggestions": []
            }
    
    def refine_spec_with_answers(self, spec: CircuitSpec, questions: list[str], answers: list[str]) -> CircuitSpec:
        """
        Refine the circuit spec based on user answers to clarification questions
        """
        
        qa_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in zip(questions, answers)])
        
        system_prompt = """Sei un esperto di elettronica. Aggiorna le specifiche del circuito basandoti sulle risposte dell'utente."""
        
        user_prompt = f"""Specifiche attuali:
{spec.model_dump_json(indent=2)}

Domande e risposte:
{qa_text}

Aggiorna le specifiche incorporando le risposte. Rispondi SOLO con JSON valido."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            spec_dict = json.loads(content)
            return CircuitSpec(**spec_dict)
            
        except Exception:
            return spec
