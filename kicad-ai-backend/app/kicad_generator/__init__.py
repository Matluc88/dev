"""
KiCad Generator - Automated schematic and PCB generation for IoT nodes
"""

__version__ = "0.1.0"

from .netlist import Component, Net, Netlist
from .schematic_generator import SchematicGenerator
from .bom_generator import BOMGenerator
from .templates import TemplateFactory

__all__ = [
    "Component",
    "Net", 
    "Netlist",
    "SchematicGenerator",
    "BOMGenerator",
    "TemplateFactory",
]
