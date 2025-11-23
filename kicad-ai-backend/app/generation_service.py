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
            
            elif sensor.kind in ["microphone", "microfono", "audio", "MAX9814"]:
                mic_comp = get_component("MAX9814_microphone")
                jst_comp = get_component("JST_XH_3pin")
                bypass_cap = get_component("capacitor_100nF")
                
                if not mic_comp or not jst_comp:
                    continue
                
                for i in range(sensor.count):
                    # Find ADC-capable GPIO pin (GPIO34, GPIO35, GPIO36)
                    gpio_pins = find_available_gpio_pins(spec.esp32_model, used_pins)
                    adc_pin = None
                    for pin in gpio_pins:
                        if pin.name in ["IO34", "IO35", "IO36", "VP", "VN"]:
                            adc_pin = pin
                            break
                    
                    if not adc_pin:
                        # Fallback to any GPIO if no ADC pins available
                        if gpio_pins:
                            adc_pin = gpio_pins[0]
                        else:
                            continue
                    
                    used_pins.append(adc_pin.number)
                    
                    # Create JST connector for microphone
                    jst_ref = f"J{component_counter['J']}"
                    component_counter['J'] += 1
                    
                    mic_connector = Component(
                        reference=jst_ref,
                        value=f"MIC_IN_{i+1}",
                        footprint=jst_comp.footprint,
                        symbol=jst_comp.symbol,
                        x=10.0,
                        y=50.0 + (i * 15.0)
                    )
                    netlist.add_component(mic_connector)
                    
                    # Add bypass capacitor for microphone
                    if bypass_cap:
                        cap_ref = f"C{component_counter.get('C', 1)}"
                        component_counter['C'] = component_counter.get('C', 1) + 1
                        
                        bypass = Component(
                            reference=cap_ref,
                            value="100nF",
                            footprint=bypass_cap.footprint,
                            symbol=bypass_cap.symbol,
                            x=15.0,
                            y=50.0 + (i * 15.0)
                        )
                        netlist.add_component(bypass)
                        
                        # Connect bypass capacitor
                        netlist.connect("VCC", cap_ref, "1")
                        netlist.connect("GND", cap_ref, "2")
                    
                    # Connect microphone
                    netlist.connect("VCC", jst_ref, "1")
                    netlist.connect("GND", jst_ref, "2")
                    netlist.connect(f"MIC{i+1}_OUT", jst_ref, "3")
                    netlist.connect(f"MIC{i+1}_OUT", "U1", adc_pin.number)
        
        # Add status LEDs
        for i, led in enumerate(spec.status_leds):
            if led.color == "bicolore":
                # Bicolor LED needs 2 GPIO pins
                gpio_pins = find_available_gpio_pins(spec.esp32_model, used_pins)
                if len(gpio_pins) < 2:
                    continue
                red_pin = gpio_pins[0]
                green_pin = gpio_pins[1]
                used_pins.extend([red_pin.number, green_pin.number])
                
                bicolor_comp = get_component("LED_bicolor")
                resistor_comp = get_component("resistor_330")
                
                if not bicolor_comp or not resistor_comp:
                    continue
                
                # Create bicolor LED
                led_ref = f"D{component_counter['D']}"
                component_counter['D'] += 1
                
                led_component = Component(
                    reference=led_ref,
                    value="LED_Bicolor",
                    footprint=bicolor_comp.footprint,
                    symbol=bicolor_comp.symbol,
                    x=70.0,
                    y=10.0 + (i * 10.0)
                )
                netlist.add_component(led_component)
                
                # Create resistors for both colors
                res_red_ref = f"R{component_counter['R']}"
                component_counter['R'] += 1
                res_green_ref = f"R{component_counter['R']}"
                component_counter['R'] += 1
                
                resistor_red = Component(
                    reference=res_red_ref,
                    value="330",
                    footprint=resistor_comp.footprint,
                    symbol=resistor_comp.symbol,
                    x=75.0,
                    y=8.0 + (i * 10.0)
                )
                netlist.add_component(resistor_red)
                
                resistor_green = Component(
                    reference=res_green_ref,
                    value="330",
                    footprint=resistor_comp.footprint,
                    symbol=resistor_comp.symbol,
                    x=75.0,
                    y=12.0 + (i * 10.0)
                )
                netlist.add_component(resistor_green)
                
                # Connect bicolor LED
                netlist.connect(f"LED_RED", led_ref, "1")
                netlist.connect(f"LED_RED", res_red_ref, "1")
                netlist.connect(f"LED_RED_GPIO", res_red_ref, "2")
                netlist.connect(f"LED_RED_GPIO", "U1", red_pin.number)
                
                netlist.connect("GND", led_ref, "2")
                
                netlist.connect(f"LED_GREEN", led_ref, "3")
                netlist.connect(f"LED_GREEN", res_green_ref, "1")
                netlist.connect(f"LED_GREEN_GPIO", res_green_ref, "2")
                netlist.connect(f"LED_GREEN_GPIO", "U1", green_pin.number)
            else:
                # Standard single-color LED
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
        
        # Add power connectors and domains
        if spec.power_connectors:
            for connector in spec.power_connectors:
                term_comp = get_component("terminal_block_2pin")
                if not term_comp:
                    continue
                
                term_ref = f"J{component_counter['J']}"
                component_counter['J'] += 1
                
                terminal = Component(
                    reference=term_ref,
                    value=f"{connector.name}_{connector.voltage}V",
                    footprint=term_comp.footprint,
                    symbol=term_comp.symbol,
                    x=10.0,
                    y=80.0
                )
                netlist.add_component(terminal)
                
                # Connect to appropriate power net
                if connector.voltage == 12.0:
                    netlist.connect("VIN_12V", term_ref, "1")
                    netlist.connect("GND", term_ref, "2")
                elif connector.voltage == 5.0:
                    netlist.connect("VLOGIC_5V", term_ref, "1")
                    netlist.connect("GND", term_ref, "2")
        
        # Add voltage regulator if we have 12V domain
        if spec.power_domains:
            has_12v = any(d.voltage == 12.0 for d in spec.power_domains)
            has_5v_logic = any(d.voltage == 5.0 and d.role == "logic" for d in spec.power_domains)
            
            if has_12v and has_5v_logic:
                reg_comp = get_component("LM7805_regulator")
                if reg_comp:
                    reg_ref = f"U{component_counter['U']}"
                    component_counter['U'] += 1
                    
                    regulator = Component(
                        reference=reg_ref,
                        value="LM7805",
                        footprint=reg_comp.footprint,
                        symbol=reg_comp.symbol,
                        x=30.0,
                        y=80.0
                    )
                    netlist.add_component(regulator)
                    
                    # Connect regulator
                    netlist.connect("VIN_12V", reg_ref, "1")
                    netlist.connect("GND", reg_ref, "2")
                    netlist.connect("VLOGIC_5V", reg_ref, "3")
        
        # Add high-power actuators with drivers
        for i, actuator in enumerate(spec.high_power_actuators):
            # Find GPIO pin for control
            gpio_pins = find_available_gpio_pins(spec.esp32_model, used_pins)
            if not gpio_pins:
                continue
            gpio_pin = gpio_pins[0]
            used_pins.append(gpio_pin.number)
            
            if actuator.driver_type == "mosfet":
                # Add MOSFET driver circuit with gate resistors
                mosfet_comp = get_component("IRLZ44N_mosfet")
                diode_comp = get_component("diode_1N4007")
                gate_series_res = get_component("resistor_220")
                gate_pulldown_res = get_component("resistor_100k")
                
                # Determine if this is a LED strip or other actuator
                if actuator.kind in ["led_strip", "LED_strip", "strip_LED"]:
                    actuator_comp = get_component("LED_strip_5V")
                    jst_comp = get_component("JST_XH_2pin")
                    power_cap = get_component("capacitor_470uF")
                    use_jst = True
                else:
                    actuator_comp = get_component("linear_actuator_12V")
                    use_jst = False
                    power_cap = None
                
                if not mosfet_comp or not actuator_comp:
                    continue
                
                # Create MOSFET
                mosfet_ref = f"Q{component_counter.get('Q', 1)}"
                component_counter['Q'] = component_counter.get('Q', 1) + 1
                
                mosfet = Component(
                    reference=mosfet_ref,
                    value="IRLZ44N",
                    footprint=mosfet_comp.footprint,
                    symbol=mosfet_comp.symbol,
                    x=30.0,
                    y=40.0 + (i * 20.0)
                )
                netlist.add_component(mosfet)
                
                # Create gate series resistor (220Ω)
                if gate_series_res:
                    gate_res_ref = f"R{component_counter['R']}"
                    component_counter['R'] += 1
                    
                    gate_resistor = Component(
                        reference=gate_res_ref,
                        value="220",
                        footprint=gate_series_res.footprint,
                        symbol=gate_series_res.symbol,
                        x=25.0,
                        y=40.0 + (i * 20.0)
                    )
                    netlist.add_component(gate_resistor)
                
                # Create gate pulldown resistor (100kΩ)
                if gate_pulldown_res:
                    pulldown_ref = f"R{component_counter['R']}"
                    component_counter['R'] += 1
                    
                    pulldown_resistor = Component(
                        reference=pulldown_ref,
                        value="100k",
                        footprint=gate_pulldown_res.footprint,
                        symbol=gate_pulldown_res.symbol,
                        x=27.0,
                        y=42.0 + (i * 20.0)
                    )
                    netlist.add_component(pulldown_resistor)
                
                # Create flyback diode (only for inductive loads)
                if diode_comp and not use_jst:
                    diode_ref = f"D{component_counter['D']}"
                    component_counter['D'] += 1
                    
                    diode = Component(
                        reference=diode_ref,
                        value="1N4007",
                        footprint=diode_comp.footprint,
                        symbol=diode_comp.symbol,
                        x=35.0,
                        y=40.0 + (i * 20.0)
                    )
                    netlist.add_component(diode)
                
                # Create power supply capacitor for LED strip
                if power_cap and use_jst:
                    cap_ref = f"C{component_counter.get('C', 1)}"
                    component_counter['C'] = component_counter.get('C', 1) + 1
                    
                    power_capacitor = Component(
                        reference=cap_ref,
                        value="470uF",
                        footprint=power_cap.footprint,
                        symbol=power_cap.symbol,
                        x=20.0,
                        y=40.0 + (i * 20.0)
                    )
                    netlist.add_component(power_capacitor)
                    
                    # Connect power capacitor
                    if actuator.supply_voltage == 5.0:
                        netlist.connect("VCC", cap_ref, "1")
                    else:
                        netlist.connect("VIN_12V", cap_ref, "1")
                    netlist.connect("GND", cap_ref, "2")
                
                # Create actuator connector
                act_ref = f"J{component_counter['J']}"
                component_counter['J'] += 1
                
                if use_jst and jst_comp:
                    actuator_connector = Component(
                        reference=act_ref,
                        value=f"LED_STRIP_OUT_{i+1}",
                        footprint=jst_comp.footprint,
                        symbol=jst_comp.symbol,
                        x=40.0,
                        y=40.0 + (i * 20.0)
                    )
                else:
                    actuator_connector = Component(
                        reference=act_ref,
                        value=f"Actuator_{i+1}",
                        footprint=actuator_comp.footprint,
                        symbol=actuator_comp.symbol,
                        x=40.0,
                        y=40.0 + (i * 20.0)
                    )
                netlist.add_component(actuator_connector)
                
                # Connect MOSFET driver circuit with gate resistors
                netlist.connect(f"ACTUATOR{i+1}_GPIO", "U1", gpio_pin.number)
                
                if gate_series_res:
                    # GPIO -> series resistor -> gate
                    netlist.connect(f"ACTUATOR{i+1}_GPIO", gate_res_ref, "1")
                    netlist.connect(f"ACTUATOR{i+1}_GATE", gate_res_ref, "2")
                    netlist.connect(f"ACTUATOR{i+1}_GATE", mosfet_ref, "1")  # Gate
                else:
                    # Direct connection if no resistor
                    netlist.connect(f"ACTUATOR{i+1}_GPIO", mosfet_ref, "1")  # Gate
                
                if gate_pulldown_res:
                    # Gate pulldown to GND
                    netlist.connect(f"ACTUATOR{i+1}_GATE", pulldown_ref, "1")
                    netlist.connect("GND", pulldown_ref, "2")
                
                netlist.connect("GND", mosfet_ref, "3")  # Source
                netlist.connect(f"ACTUATOR{i+1}_SWITCHED", mosfet_ref, "2")  # Drain
                netlist.connect(f"ACTUATOR{i+1}_SWITCHED", act_ref, "2")  # Load GND
                
                # Connect power based on voltage
                if actuator.supply_voltage == 5.0:
                    netlist.connect("VCC", act_ref, "1")  # Load +5V
                else:
                    netlist.connect("VIN_12V", act_ref, "1")  # Load +12V
                
                # Connect flyback diode (across actuator) for inductive loads
                if diode_comp and not use_jst:
                    if actuator.supply_voltage == 5.0:
                        netlist.connect("VCC", diode_ref, "2")  # Anode to +5V
                    else:
                        netlist.connect("VIN_12V", diode_ref, "2")  # Anode to +12V
                    netlist.connect(f"ACTUATOR{i+1}_SWITCHED", diode_ref, "1")  # Cathode to switched side
            
            elif actuator.driver_type == "relay":
                # Add relay driver circuit
                relay_comp = get_component("relay_12V")
                actuator_comp = get_component("linear_actuator_12V")
                
                if not relay_comp or not actuator_comp:
                    continue
                
                # Create relay
                relay_ref = f"K{component_counter.get('K', 1)}"
                component_counter['K'] = component_counter.get('K', 1) + 1
                
                relay = Component(
                    reference=relay_ref,
                    value="Relay_12V",
                    footprint=relay_comp.footprint,
                    symbol=relay_comp.symbol,
                    x=30.0,
                    y=40.0 + (i * 20.0)
                )
                netlist.add_component(relay)
                
                # Create actuator connector
                act_ref = f"J{component_counter['J']}"
                component_counter['J'] += 1
                
                actuator_connector = Component(
                    reference=act_ref,
                    value=f"Actuator_{i+1}",
                    footprint=actuator_comp.footprint,
                    symbol=actuator_comp.symbol,
                    x=40.0,
                    y=40.0 + (i * 20.0)
                )
                netlist.add_component(actuator_connector)
                
                # Connect relay
                netlist.connect(f"ACTUATOR{i+1}_CTRL", "U1", gpio_pin.number)
                netlist.connect(f"ACTUATOR{i+1}_CTRL", relay_ref, "1")  # Coil+
                netlist.connect("GND", relay_ref, "2")  # Coil-
                netlist.connect("VIN_12V", relay_ref, "3")  # COM
                netlist.connect(f"ACTUATOR{i+1}_SWITCHED", relay_ref, "4")  # NO
                netlist.connect(f"ACTUATOR{i+1}_SWITCHED", act_ref, "1")  # Actuator +
                netlist.connect("GND", act_ref, "2")  # Actuator -
        
        # Connect ESP32 power
        if spec.power_domains and any(d.voltage == 5.0 and d.role == "logic" for d in spec.power_domains):
            # Use 5V logic rail
            netlist.connect("VLOGIC_5V", "U1", "16")  # VIN
        else:
            # Use standard VCC
            netlist.connect("VCC", "U1", "1")  # 3V3 out
        
        netlist.connect("GND", "U1", "14")
        netlist.connect("GND", "U1", "17")
        
        return netlist
