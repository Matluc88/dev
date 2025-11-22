"""
BOM (Bill of Materials) generator
"""

from typing import List, Dict
from .netlist import Netlist, Component
import csv


class BOMGenerator:
    """Generates Bill of Materials from netlist"""
    
    def __init__(self, netlist: Netlist):
        self.netlist = netlist
        
    def generate_csv(self, output_path: str):
        """Generate BOM as CSV file"""
        bom_items = self._collect_bom_items()
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Item', 'Quantity', 'Reference', 'Value', 'Footprint', 'Description'])
            
            item_num = 1
            for bom_item in bom_items:
                writer.writerow([
                    item_num,
                    bom_item['quantity'],
                    ', '.join(bom_item['references']),
                    bom_item['value'],
                    bom_item['footprint'],
                    bom_item['description']
                ])
                item_num += 1
                
    def generate_text(self, output_path: str):
        """Generate BOM as text file"""
        bom_items = self._collect_bom_items()
        
        with open(output_path, 'w') as f:
            f.write("Bill of Materials\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Project: {self.netlist.name}\n")
            f.write(f"Total unique parts: {len(bom_items)}\n")
            f.write(f"Total components: {sum(item['quantity'] for item in bom_items)}\n\n")
            
            f.write("-" * 80 + "\n")
            f.write(f"{'Item':<6} {'Qty':<6} {'Reference':<20} {'Value':<20} {'Footprint':<30}\n")
            f.write("-" * 80 + "\n")
            
            for i, item in enumerate(bom_items, 1):
                refs = ', '.join(item['references'])
                f.write(f"{i:<6} {item['quantity']:<6} {refs:<20} {item['value']:<20} {item['footprint']:<30}\n")
                
            f.write("-" * 80 + "\n")
            
    def _collect_bom_items(self) -> List[Dict]:
        """Collect and group BOM items"""
        items_dict = {}
        
        for comp in self.netlist.get_all_components():
            key = (comp.value, comp.footprint, comp.symbol)
            
            if key not in items_dict:
                items_dict[key] = {
                    'value': comp.value,
                    'footprint': comp.footprint,
                    'symbol': comp.symbol,
                    'description': self._get_component_description(comp),
                    'references': [],
                    'quantity': 0
                }
            
            items_dict[key]['references'].append(comp.reference)
            items_dict[key]['quantity'] += 1
        
        bom_items = list(items_dict.values())
        bom_items.sort(key=lambda x: x['references'][0])
        
        return bom_items
        
    def _get_component_description(self, comp: Component) -> str:
        """Get a human-readable description of the component"""
        if "LED" in comp.value:
            return f"LED {comp.value}"
        elif "ESP32" in comp.value:
            return "ESP32 Development Board"
        elif "Servo" in comp.value:
            return "Servo Motor SG90"
        elif "IR" in comp.value:
            return "IR Proximity Sensor"
        elif comp.symbol == "Device:R":
            return f"Resistor {comp.value} Ohm"
        else:
            return comp.value
