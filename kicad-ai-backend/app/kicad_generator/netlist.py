"""
Internal netlist model for representing electronic circuits
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import uuid


@dataclass
class Pin:
    """Represents a pin on a component"""
    number: str
    name: str
    electrical_type: str = "input"
    
    
@dataclass
class Component:
    """Represents an electronic component"""
    reference: str
    value: str
    footprint: str
    symbol: str
    pins: List[Pin] = field(default_factory=list)
    properties: Dict[str, str] = field(default_factory=dict)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0
    
    def add_pin(self, number: str, name: str, electrical_type: str = "input"):
        """Add a pin to the component"""
        self.pins.append(Pin(number, name, electrical_type))
        
    def get_pin(self, number: str) -> Optional[Pin]:
        """Get a pin by number"""
        for pin in self.pins:
            if pin.number == number:
                return pin
        return None


@dataclass
class Net:
    """Represents an electrical net connecting pins"""
    name: str
    connections: List[tuple] = field(default_factory=list)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def add_connection(self, component_ref: str, pin_number: str):
        """Add a connection to this net"""
        self.connections.append((component_ref, pin_number))


class Netlist:
    """Container for the complete circuit netlist"""
    
    def __init__(self, name: str = "Circuit"):
        self.name = name
        self.components: Dict[str, Component] = {}
        self.nets: Dict[str, Net] = {}
        
    def add_component(self, component: Component):
        """Add a component to the netlist"""
        self.components[component.reference] = component
        
    def add_net(self, net: Net):
        """Add a net to the netlist"""
        self.nets[net.name] = net
        
    def connect(self, net_name: str, component_ref: str, pin_number: str):
        """Connect a component pin to a net"""
        if net_name not in self.nets:
            self.nets[net_name] = Net(name=net_name)
        self.nets[net_name].add_connection(component_ref, pin_number)
        
    def get_component(self, reference: str) -> Optional[Component]:
        """Get a component by reference"""
        return self.components.get(reference)
        
    def get_net(self, name: str) -> Optional[Net]:
        """Get a net by name"""
        return self.nets.get(name)
        
    def get_all_components(self) -> List[Component]:
        """Get all components"""
        return list(self.components.values())
        
    def get_all_nets(self) -> List[Net]:
        """Get all nets"""
        return list(self.nets.values())
