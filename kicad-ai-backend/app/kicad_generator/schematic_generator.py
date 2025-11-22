"""
Schematic generator - converts netlist to KiCad .kicad_sch format
"""

from typing import Dict, List
from .netlist import Netlist, Component, Net
import uuid


class SchematicGenerator:
    """Generates KiCad schematic files from netlist"""
    
    def __init__(self, netlist: Netlist, kicad_version: str = "7.0"):
        self.netlist = netlist
        self.kicad_version = kicad_version
        
    def generate(self, output_path: str):
        """Generate the .kicad_sch file"""
        content = self._generate_header()
        content += self._generate_symbols()
        content += self._generate_wires()
        content += self._generate_labels()
        content += self._generate_footer()
        
        with open(output_path, 'w') as f:
            f.write(content)
            
    def _generate_header(self) -> str:
        """Generate the schematic header"""
        return f'''(kicad_sch (version 20230121) (generator kicad_generator)

  (uuid {uuid.uuid4()})

  (paper "A4")

  (lib_symbols
    (symbol "Device:R" (pin_numbers hide) (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "R" (at 2.032 0 90)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "R" (at 0 0 90)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "" (at -1.778 0 90)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "R_0_1"
        (rectangle (start -1.016 -2.54) (end 1.016 2.54)
          (stroke (width 0.254) (type default))
          (fill (type none))
        )
      )
      (symbol "R_1_1"
        (pin passive line (at 0 3.81 270) (length 1.27)
          (name "~" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
        (pin passive line (at 0 -3.81 90) (length 1.27)
          (name "~" (effects (font (size 1.27 1.27))))
          (number "2" (effects (font (size 1.27 1.27))))
        )
      )
    )
    (symbol "Device:LED" (pin_numbers hide) (pin_names (offset 1.016) hide) (in_bom yes) (on_board yes)
      (property "Reference" "D" (at 0 2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "LED" (at 0 -2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "LED_0_1"
        (polyline
          (pts
            (xy -1.27 -1.27)
            (xy -1.27 1.27)
          )
          (stroke (width 0.254) (type default))
          (fill (type none))
        )
        (polyline
          (pts
            (xy 1.27 -1.27)
            (xy 1.27 1.27)
            (xy -1.27 0)
            (xy 1.27 -1.27)
          )
          (stroke (width 0.254) (type default))
          (fill (type none))
        )
      )
      (symbol "LED_1_1"
        (pin passive line (at -3.81 0 0) (length 2.54)
          (name "K" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
        (pin passive line (at 3.81 0 180) (length 2.54)
          (name "A" (effects (font (size 1.27 1.27))))
          (number "2" (effects (font (size 1.27 1.27))))
        )
      )
    )
    (symbol "MCU_Module:ESP32-DevKitC" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 0 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "ESP32-DevKitC" (at 0 -2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "ESP32-DevKitC_0_1"
        (rectangle (start -12.7 25.4) (end 12.7 -25.4)
          (stroke (width 0.254) (type default))
          (fill (type background))
        )
      )
      (symbol "ESP32-DevKitC_1_1"
        (pin power_in line (at -15.24 22.86 0) (length 2.54)
          (name "3V3" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at -15.24 20.32 0) (length 2.54)
          (name "EN" (effects (font (size 1.27 1.27))))
          (number "2" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at -15.24 17.78 0) (length 2.54)
          (name "VP" (effects (font (size 1.27 1.27))))
          (number "3" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at -15.24 15.24 0) (length 2.54)
          (name "VN" (effects (font (size 1.27 1.27))))
          (number "4" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at -15.24 12.7 0) (length 2.54)
          (name "IO34" (effects (font (size 1.27 1.27))))
          (number "5" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at -15.24 10.16 0) (length 2.54)
          (name "IO35" (effects (font (size 1.27 1.27))))
          (number "6" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at -15.24 7.62 0) (length 2.54)
          (name "IO32" (effects (font (size 1.27 1.27))))
          (number "7" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at -15.24 5.08 0) (length 2.54)
          (name "IO33" (effects (font (size 1.27 1.27))))
          (number "8" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at -15.24 2.54 0) (length 2.54)
          (name "IO25" (effects (font (size 1.27 1.27))))
          (number "9" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at -15.24 0 0) (length 2.54)
          (name "IO26" (effects (font (size 1.27 1.27))))
          (number "10" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at -15.24 -2.54 0) (length 2.54)
          (name "IO27" (effects (font (size 1.27 1.27))))
          (number "11" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at -15.24 -5.08 0) (length 2.54)
          (name "IO14" (effects (font (size 1.27 1.27))))
          (number "12" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at -15.24 -7.62 0) (length 2.54)
          (name "IO12" (effects (font (size 1.27 1.27))))
          (number "13" (effects (font (size 1.27 1.27))))
        )
        (pin power_in line (at -15.24 -10.16 0) (length 2.54)
          (name "GND" (effects (font (size 1.27 1.27))))
          (number "14" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at -15.24 -12.7 0) (length 2.54)
          (name "IO13" (effects (font (size 1.27 1.27))))
          (number "15" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at 15.24 22.86 180) (length 2.54)
          (name "VIN" (effects (font (size 1.27 1.27))))
          (number "16" (effects (font (size 1.27 1.27))))
        )
        (pin power_in line (at 15.24 20.32 180) (length 2.54)
          (name "GND" (effects (font (size 1.27 1.27))))
          (number "17" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at 15.24 17.78 180) (length 2.54)
          (name "IO23" (effects (font (size 1.27 1.27))))
          (number "18" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at 15.24 15.24 180) (length 2.54)
          (name "IO22" (effects (font (size 1.27 1.27))))
          (number "19" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at 15.24 12.7 180) (length 2.54)
          (name "TX0" (effects (font (size 1.27 1.27))))
          (number "20" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at 15.24 10.16 180) (length 2.54)
          (name "RX0" (effects (font (size 1.27 1.27))))
          (number "21" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at 15.24 7.62 180) (length 2.54)
          (name "IO21" (effects (font (size 1.27 1.27))))
          (number "22" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at 15.24 5.08 180) (length 2.54)
          (name "IO19" (effects (font (size 1.27 1.27))))
          (number "23" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at 15.24 2.54 180) (length 2.54)
          (name "IO18" (effects (font (size 1.27 1.27))))
          (number "24" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at 15.24 0 180) (length 2.54)
          (name "IO5" (effects (font (size 1.27 1.27))))
          (number "25" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at 15.24 -2.54 180) (length 2.54)
          (name "IO17" (effects (font (size 1.27 1.27))))
          (number "26" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at 15.24 -5.08 180) (length 2.54)
          (name "IO16" (effects (font (size 1.27 1.27))))
          (number "27" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at 15.24 -7.62 180) (length 2.54)
          (name "IO4" (effects (font (size 1.27 1.27))))
          (number "28" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at 15.24 -10.16 180) (length 2.54)
          (name "IO0" (effects (font (size 1.27 1.27))))
          (number "29" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at 15.24 -12.7 180) (length 2.54)
          (name "IO2" (effects (font (size 1.27 1.27))))
          (number "30" (effects (font (size 1.27 1.27))))
        )
        (pin bidirectional line (at 15.24 -15.24 180) (length 2.54)
          (name "IO15" (effects (font (size 1.27 1.27))))
          (number "31" (effects (font (size 1.27 1.27))))
        )
      )
    )
    (symbol "Connector:Servo_Connector" (in_bom yes) (on_board yes)
      (property "Reference" "J" (at 0 5.08 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "Servo" (at 0 -5.08 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "Servo_Connector_0_1"
        (rectangle (start -5.08 3.81) (end 5.08 -3.81)
          (stroke (width 0.254) (type default))
          (fill (type background))
        )
      )
      (symbol "Servo_Connector_1_1"
        (pin power_in line (at -7.62 2.54 0) (length 2.54)
          (name "VCC" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
        (pin power_in line (at -7.62 0 0) (length 2.54)
          (name "GND" (effects (font (size 1.27 1.27))))
          (number "2" (effects (font (size 1.27 1.27))))
        )
        (pin input line (at -7.62 -2.54 0) (length 2.54)
          (name "PWM" (effects (font (size 1.27 1.27))))
          (number "3" (effects (font (size 1.27 1.27))))
        )
      )
    )
    (symbol "Sensor:IR_Sensor" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 5.08 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "IR_Sensor" (at 0 -5.08 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "IR_Sensor_0_1"
        (rectangle (start -5.08 3.81) (end 5.08 -3.81)
          (stroke (width 0.254) (type default))
          (fill (type background))
        )
      )
      (symbol "IR_Sensor_1_1"
        (pin power_in line (at -7.62 2.54 0) (length 2.54)
          (name "VCC" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
        (pin power_in line (at -7.62 0 0) (length 2.54)
          (name "GND" (effects (font (size 1.27 1.27))))
          (number "2" (effects (font (size 1.27 1.27))))
        )
        (pin output line (at -7.62 -2.54 0) (length 2.54)
          (name "OUT" (effects (font (size 1.27 1.27))))
          (number "3" (effects (font (size 1.27 1.27))))
        )
      )
    )
  )

'''

    def _generate_symbols(self) -> str:
        """Generate symbol instances for all components"""
        content = ""
        for comp in self.netlist.get_all_components():
            content += self._generate_symbol_instance(comp)
        return content
        
    def _generate_symbol_instance(self, comp: Component) -> str:
        """Generate a single symbol instance"""
        return f'''  (symbol (lib_id "{comp.symbol}") (at {comp.x} {comp.y} 0) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (uuid {comp.uuid})
    (property "Reference" "{comp.reference}" (at {comp.x} {comp.y + 5.08} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{comp.value}" (at {comp.x} {comp.y - 5.08} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "{comp.footprint}" (at {comp.x} {comp.y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "" (at {comp.x} {comp.y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
  )

'''

    def _generate_wires(self) -> str:
        """Generate wire connections"""
        return ""
        
    def _generate_labels(self) -> str:
        """Generate net labels"""
        content = ""
        y_offset = 0
        for net in self.netlist.get_all_nets():
            if net.name not in ["GND", "VCC", "+5V", "+3V3"]:
                content += f'''  (label "{net.name}" (at 200 {100 + y_offset} 0)
    (effects (font (size 1.27 1.27)) (justify left bottom))
    (uuid {uuid.uuid4()})
  )

'''
                y_offset += 5
        return content
        
    def _generate_footer(self) -> str:
        """Generate schematic footer"""
        return '''  (sheet_instances
    (path "/" (page "1"))
  )
)
'''
