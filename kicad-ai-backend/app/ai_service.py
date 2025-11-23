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
1. Identifica sempre il tipo di nodo (gate_controller, sensor_node, irrigation, lighting, alarm, power_controller, ecc.)
2. Elenca tutti i componenti necessari: sensori, attuatori, LED, driver di potenza, alimentazioni
3. Se qualcosa non è chiaro, aggiungi domande in "clarification_questions"
4. Fai assunzioni ragionevoli e documentale in "assumptions_made"
5. Usa sempre ESP32-DevKitC come microcontrollore di default
6. La scheda è sempre 10x10 cm (100x100 mm)
7. Alimentazione di default: 5V, max 2A (per logica), 12V per attuatori di potenza

COMPONENTI DISPONIBILI:
- Servo: SG90 (5V, 500mA, PWM)
- Sensori: IR/fotocellula, ultrasuoni (HC-SR04), temperatura, umidità, microfono MAX9814 (audio/voce)
- LED: rosso, verde, blu, giallo, bianco, bicolore rosso/verde, LED strip RGB 5V (500mm, 3A)
- Attuatori bassa potenza: servo, relè piccoli
- Attuatori alta potenza: attuatori lineari 12V, motori DC, relè di potenza, LED strip RGB 5V (tramite MOSFET)
- Driver: MOSFET logic-level (IRLZ44N), relè 12V
- Passivi: resistori (220Ω, 330Ω, 100kΩ), condensatori (100nF, 470µF, 1000µF)
- Connettori: morsettiere, JST-XH (2-pin, 3-pin), regolatori 12V→5V

CIRCUITI MULTI-TENSIONE:
Per circuiti con attuatori 12V, usa sempre:
- power_domains: [{"name": "12V", "voltage": 12.0, "max_current_ma": 3000, "role": "actuator"}, {"name": "5V", "voltage": 5.0, "max_current_ma": 1500, "role": "logic"}]
- power_connectors: [{"name": "12V_IN", "voltage": 12.0, "connector_type": "terminal_block"}]
- high_power_actuators: per attuatori che richiedono driver MOSFET o relè

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

Input: "Attuatore lineare 12V con fotocellula IR e LED bicolore"
Output: {
  "node_type": "power_controller",
  "esp32_model": "ESP32-DevKitC",
  "sensors": [{"kind": "IR", "count": 1, "mounting": "offboard"}],
  "status_leds": [{"color": "bicolore"}],
  "power_domains": [
    {"name": "12V", "voltage": 12.0, "max_current_ma": 3000, "role": "actuator"},
    {"name": "5V", "voltage": 5.0, "max_current_ma": 1500, "role": "logic"}
  ],
  "high_power_actuators": [
    {"kind": "linear_actuator", "supply_voltage": 12.0, "max_current_ma": 2000, "driver_type": "mosfet"}
  ],
  "power_connectors": [
    {"name": "12V_IN", "voltage": 12.0, "connector_type": "terminal_block"}
  ],
  "assumptions_made": ["Usato MOSFET logic-level per attuatore", "Aggiunto regolatore 12V→5V per logica", "LED bicolore per stato fascio IR"]
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
