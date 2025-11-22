"""
Data models for circuit specifications and components
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class ComponentCategory(str, Enum):
    MCU = "mcu"
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    LED = "led"
    RESISTOR = "resistor"
    CONNECTOR = "connector"


class PinRole(str, Enum):
    POWER_IN = "power_in"
    POWER_OUT = "power_out"
    GROUND = "ground"
    GPIO = "gpio"
    SIGNAL_IN = "signal_in"
    SIGNAL_OUT = "signal_out"


class ComponentPin(BaseModel):
    number: str
    name: str
    role: PinRole
    voltage_min: Optional[float] = None
    voltage_max: Optional[float] = None
    current_ma: Optional[int] = None
    supports_pwm: bool = False
    supports_i2c: bool = False
    supports_spi: bool = False


class Component(BaseModel):
    id: str
    category: ComponentCategory
    name: str
    symbol: str
    footprint: str
    pins: List[ComponentPin]
    description: str
    width_mm: float = 10.0
    height_mm: float = 10.0
    typical_current_ma: int = 0


class SensorSpec(BaseModel):
    kind: str
    count: int = 1
    mounting: str = "offboard"
    connector_type: str = "3-pin"


class ActuatorSpec(BaseModel):
    kind: str
    model: Optional[str] = None
    count: int = 1
    mounting: str = "offboard"
    connector_type: str = "3-pin"


class LEDSpec(BaseModel):
    color: str
    role: str = "status"


class PowerSpec(BaseModel):
    supply_voltage: float = 5.0
    max_current_ma: int = 2000


class BoardSize(BaseModel):
    width_mm: float = 100.0
    height_mm: float = 100.0


class CircuitSpec(BaseModel):
    node_type: str
    description: Optional[str] = None
    esp32_model: str = "ESP32-DevKitC"
    board_size: BoardSize = BoardSize()
    power: PowerSpec = PowerSpec()
    sensors: List[SensorSpec] = []
    actuators: List[ActuatorSpec] = []
    status_leds: List[LEDSpec] = []
    clarification_questions: List[str] = []
    assumptions_made: List[str] = []


class ValidationResult(BaseModel):
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    pin_assignments: Dict[str, str] = {}
    power_budget_ma: int = 0


class ParseRequest(BaseModel):
    description: str
    language: str = "it"


class ParseResponse(BaseModel):
    spec: CircuitSpec
    questions: List[str] = []
    suggestions: List[str] = []


class GenerateRequest(BaseModel):
    spec: CircuitSpec
    project_name: str = "circuit"


class GenerateResponse(BaseModel):
    success: bool
    files: Dict[str, str] = {}
    validation: ValidationResult
    message: str = ""
