from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from app.models import (
    ParseRequest, ParseResponse, GenerateRequest, GenerateResponse,
    CircuitSpec, ValidationResult
)
from app.ai_service import AIService
from app.validation_service import ValidationService
from app.generation_service import GenerationService
from app.component_catalog import COMPONENT_CATALOG

load_dotenv()

app = FastAPI(title="KiCad AI Generator API", version="1.0.0")

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize services
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

ai_service = AIService(api_key=OPENAI_API_KEY)
validation_service = ValidationService()
generation_service = GenerationService()


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/api/components")
async def get_components():
    """Get available components catalog"""
    return {
        "components": {
            comp_id: {
                "id": comp.id,
                "name": comp.name,
                "category": comp.category,
                "description": comp.description
            }
            for comp_id, comp in COMPONENT_CATALOG.items()
        }
    }


@app.post("/api/parse", response_model=ParseResponse)
async def parse_description(request: ParseRequest):
    """
    Parse natural language circuit description using AI
    Returns structured circuit specification and clarification questions
    """
    try:
        result = ai_service.parse_description(request.description, request.language)
        
        if result["spec"] is None:
            return ParseResponse(
                spec=CircuitSpec(node_type="unknown"),
                questions=result["questions"],
                suggestions=[]
            )
        
        return ParseResponse(
            spec=result["spec"],
            questions=result["questions"],
            suggestions=result["suggestions"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel parsing: {str(e)}")


@app.post("/api/validate", response_model=ValidationResult)
async def validate_circuit(spec: CircuitSpec):
    """
    Validate circuit specification
    Checks electrical feasibility, pin availability, power budget, etc.
    """
    try:
        validation = validation_service.validate_circuit(spec)
        return validation
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nella validazione: {str(e)}")


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_circuit(request: GenerateRequest):
    """
    Generate KiCad files from validated circuit specification
    Returns schematic, BOM, and validation results
    """
    try:
        # Validate first
        validation = validation_service.validate_circuit(request.spec)
        
        if not validation.valid:
            return GenerateResponse(
                success=False,
                validation=validation,
                message="Validazione fallita. Correggi gli errori prima di generare."
            )
        
        # Generate files
        files = generation_service.generate_circuit(
            request.spec,
            validation,
            request.project_name
        )
        
        return GenerateResponse(
            success=True,
            files=files,
            validation=validation,
            message=f"Circuito generato con successo! Componenti: {len(validation.pin_assignments)}, Consumo: {validation.power_budget_ma}mA"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nella generazione: {str(e)}")


@app.get("/api/info")
async def get_info():
    """Get API information and capabilities"""
    return {
        "name": "KiCad AI Generator",
        "version": "1.0.0",
        "description": "AI-powered circuit generator for ESP32-based IoT nodes",
        "features": [
            "Natural language circuit description parsing",
            "Intelligent component suggestion",
            "Electrical validation (pins, power, feasibility)",
            "Automatic KiCad schematic generation",
            "BOM generation (CSV + TXT)",
            "10x10cm PCB layout (coming soon)"
        ],
        "supported_components": list(COMPONENT_CATALOG.keys()),
        "supported_node_types": [
            "gate_controller",
            "sensor_node",
            "irrigation_controller",
            "lighting_controller",
            "alarm_system"
        ]
    }
