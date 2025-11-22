"""
Generation service for creating KiCad files from validated circuit specs
"""

import os
import tempfile
import base64
from pathlib import Path
from app.models import CircuitSpec, ValidationResult
from app.component_catalog import get_component, find_available_pwm_pins, find_available_gpio_pins
from app.kicad_generator import Netlist, Component, SchematicGenerator, BOMGenerator
from typing import Dict, Tuple


class GenerationService:
    def __init__(self):
        self.output_dir = Path(tempfile.gettempdir()) / "kicad_output"
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_circuit(self, spec: CircuitSpec, validation: ValidationResult, project_name: str = "circuit") -> Dict[str, str]:
        """
        Generate KiCad schematic and BOM files from validated circuit spec
        Returns dict with file paths
        """
        
        # Create netlist from spec
        netlist = self._create_netlist_from_spec(spec, validation)
        
        # Generate schematic
        schematic_path = self.output_dir / f"{project_name}.kicad_sch"
        schematic_gen = SchematicGenerator(netlist)
        schematic_gen.generate(str(schematic_path))
        
        # Generate BOM
        bom_csv_path = self.output_dir / f"{project_name}_bom.csv"
        bom_txt_path = self.output_dir / f"{project_name}_bom.txt"
        bom_gen = BOMGenerator(netlist)
        bom_gen.generate_csv(str(bom_csv_path))
        bom_gen.generate_text(str(bom_txt_path))
        
        # Read files and encode as base64 for transfer
        files = {}
        
        with open(schematic_path, 'r') as f:
            files['schematic'] = {
                'filename': f"{project_name}.kicad_sch",
                'content': base64.b64encode(f.read().encode()).decode()
            }
        
        with open(bom_csv_path, 'r') as f:
            files['bom_csv'] = {
                'filename': f"{project_name}_bom.csv",
                'content': base64.b64encode(f.read().encode()).decode()
            }
        
        with open(bom_txt_path, 'r') as f:
            files['bom_txt'] = {
                'filename': f"{project_name}_bom.txt",
                'content': base64.b64encode(f.read().encode()).decode()
            }
        
        return files
    
    def _create_netlist_from_spec(self, spec: CircuitSpec, validation: ValidationResult) -> Netlist:
        """Create internal netlist from circuit spec and pin assignments"""
        
        netlist = Netlist(name=spec.node_type.replace("_", " ").title())
        
        # Add ESP32
        esp32_comp = get_component(spec.esp32_model)
        if not esp32_comp:
            raise ValueError(f"ESP32 model {spec.esp32_model} not found")
        
        esp32 = Component(
            reference="U1",
            value=spec.esp32_model,
            footprint=esp32_comp.footprint,
            symbol=esp32_comp.symbol,
            x=50.0,  # Center of 100mm board
            y=50.0
        )
        netlist.add_component(esp32)
        
        # Track used pins
        used_pins = []
        component_counter = {"J": 1, "D": 1, "R": 1, "U": 2}  # U1 is ESP32
        
        # Add actuators (servos)
        for actuator in spec.actuators:
            if actuator.kind == "servo":
                servo_comp = get_component("SG90_servo")
                if not servo_comp:
                    continue
                
                for i in range(actuator.count):
                    # Find PWM pin
                    pwm_pins = find_available_pwm_pins(spec.esp32_model, used_pins)
                    if not pwm_pins:
                        continue
                    pwm_pin = pwm_pins[0]
                    used_pins.append(pwm_pin.number)
                    
                    # Create servo connector
                    ref = f"J{component_counter['J']}"
                    component_counter['J'] += 1
                    
                    servo = Component(
                        reference=ref,
                        value=f"Servo_{i+1}",
                        footprint=servo_comp.footprint,
                        symbol=servo_comp.symbol,
                        x=10.0,  # Left edge
                        y=20.0 + (i * 15.0)
                    )
                    netlist.add_component(servo)
                    
                    # Connect servo
                    netlist.connect("VCC", ref, "1")
                    netlist.connect("GND", ref, "2")
                    netlist.connect(f"SERVO{i+1}_PWM", ref, "3")
                    netlist.connect(f"SERVO{i+1}_PWM", "U1", pwm_pin.number)
        
        # Add sensors
        for sensor in spec.sensors:
            if sensor.kind == "IR":
                ir_comp = get_component("IR_sensor")
                if not ir_comp:
                    continue
                
                for i in range(sensor.count):
                    # Find GPIO pin
                    gpio_pins = find_available_gpio_pins(spec.esp32_model, used_pins)
                    if not gpio_pins:
                        continue
                    gpio_pin = gpio_pins[0]
                    used_pins.append(gpio_pin.number)
                    
                    # Create sensor
                    ref = f"U{component_counter['U']}"
                    component_counter['U'] += 1
                    
                    ir_sensor = Component(
                        reference=ref,
                        value=f"IR_Sensor_{i+1}",
                        footprint=ir_comp.footprint,
                        symbol=ir_comp.symbol,
                        x=90.0,  # Right edge
                        y=20.0 + (i * 15.0)
                    )
                    netlist.add_component(ir_sensor)
                    
                    # Connect sensor
                    netlist.connect("VCC", ref, "1")
                    netlist.connect("GND", ref, "2")
                    netlist.connect(f"IR{i+1}_OUT", ref, "3")
                    netlist.connect(f"IR{i+1}_OUT", "U1", gpio_pin.number)
            
            elif sensor.kind in ["ultrasuoni", "ultrasonic"]:
                ultra_comp = get_component("ultrasonic_sensor")
                if not ultra_comp:
                    continue
                
                for i in range(sensor.count):
                    # Find 2 GPIO pins
                    gpio_pins = find_available_gpio_pins(spec.esp32_model, used_pins)
                    if len(gpio_pins) < 2:
                        continue
                    trig_pin = gpio_pins[0]
                    echo_pin = gpio_pins[1]
                    used_pins.extend([trig_pin.number, echo_pin.number])
                    
                    # Create sensor
                    ref = f"U{component_counter['U']}"
                    component_counter['U'] += 1
                    
                    ultra_sensor = Component(
                        reference=ref,
                        value=f"Ultrasonic_{i+1}",
                        footprint=ultra_comp.footprint,
                        symbol="Sensor:HC-SR04",
                        x=90.0,
                        y=40.0 + (i * 20.0)
                    )
                    netlist.add_component(ultra_sensor)
                    
                    # Connect sensor
                    netlist.connect("VCC", ref, "1")
                    netlist.connect(f"ULTRA{i+1}_TRIG", ref, "2")
                    netlist.connect(f"ULTRA{i+1}_ECHO", ref, "3")
                    netlist.connect("GND", ref, "4")
                    netlist.connect(f"ULTRA{i+1}_TRIG", "U1", trig_pin.number)
                    netlist.connect(f"ULTRA{i+1}_ECHO", "U1", echo_pin.number)
        
        # Add status LEDs
        for i, led in enumerate(spec.status_leds):
            # Find GPIO pin
            gpio_pins = find_available_gpio_pins(spec.esp32_model, used_pins)
            if not gpio_pins:
                continue
            gpio_pin = gpio_pins[0]
            used_pins.append(gpio_pin.number)
            
            led_comp = get_component("LED_5mm")
            resistor_comp = get_component("resistor_330")
            
            if not led_comp or not resistor_comp:
                continue
            
            # Create LED
            led_ref = f"D{component_counter['D']}"
            component_counter['D'] += 1
            
            led_component = Component(
                reference=led_ref,
                value=f"LED_{led.color}",
                footprint=led_comp.footprint,
                symbol=led_comp.symbol,
                x=70.0,
                y=10.0 + (i * 10.0)
            )
            netlist.add_component(led_component)
            
            # Create resistor
            res_ref = f"R{component_counter['R']}"
            component_counter['R'] += 1
            
            resistor = Component(
                reference=res_ref,
                value="330",
                footprint=resistor_comp.footprint,
                symbol=resistor_comp.symbol,
                x=75.0,
                y=10.0 + (i * 10.0)
            )
            netlist.add_component(resistor)
            
            # Connect LED and resistor
            netlist.connect(f"LED{i+1}_ANODE", led_ref, "2")
            netlist.connect(f"LED{i+1}_ANODE", res_ref, "1")
            netlist.connect(f"LED{i+1}_GPIO", res_ref, "2")
            netlist.connect(f"LED{i+1}_GPIO", "U1", gpio_pin.number)
            netlist.connect("GND", led_ref, "1")
        
        # Connect ESP32 power
        netlist.connect("VCC", "U1", "1")  # 3V3 out
        netlist.connect("GND", "U1", "14")
        netlist.connect("GND", "U1", "17")
        
        return netlist
