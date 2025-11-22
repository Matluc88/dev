"""
Template system for generating different circuit types
"""

from .netlist import Netlist, Component, Net


class TemplateFactory:
    """Factory for creating circuit templates"""
    
    @staticmethod
    def create_from_config(config: dict) -> Netlist:
        """Create a netlist from a configuration dictionary"""
        tipo = config.get("tipo", "generic")
        
        if tipo == "nodo_cancello":
            return TemplateFactory.create_gate_controller(config)
        else:
            raise ValueError(f"Unknown circuit type: {tipo}")
    
    @staticmethod
    def create_gate_controller(config: dict) -> Netlist:
        """
        Create a gate controller circuit
        Config example: {
            "tipo": "nodo_cancello",
            "servo": 2,
            "led": ["rosso", "verde"],
            "sensore": "IR"
        }
        """
        netlist = Netlist(name="Gate_Controller")
        
        num_servos = config.get("servo", 2)
        leds = config.get("led", ["rosso", "verde"])
        sensore = config.get("sensore", "IR")
        
        esp32 = Component(
            reference="U1",
            value="ESP32-DevKitC",
            footprint="Module:ESP32-DevKitC",
            symbol="MCU_Module:ESP32-DevKitC",
            x=100.0,
            y=100.0
        )
        netlist.add_component(esp32)
        
        for i in range(num_servos):
            servo = Component(
                reference=f"J{i+1}",
                value=f"Servo_SG90_{i+1}",
                footprint="Connector:PinHeader_1x03_P2.54mm_Vertical",
                symbol="Connector:Servo_Connector",
                x=50.0,
                y=50.0 + (i * 20.0)
            )
            netlist.add_component(servo)
            
            netlist.connect("VCC", f"J{i+1}", "1")
            netlist.connect("GND", f"J{i+1}", "2")
            netlist.connect(f"SERVO{i+1}_PWM", f"J{i+1}", "3")
            netlist.connect(f"SERVO{i+1}_PWM", "U1", str(18 + i))
        
        for i, color in enumerate(leds):
            led = Component(
                reference=f"D{i+1}",
                value=f"LED_{color}",
                footprint="LED_THT:LED_D5.0mm",
                symbol="Device:LED",
                x=150.0,
                y=50.0 + (i * 15.0)
            )
            netlist.add_component(led)
            
            resistor = Component(
                reference=f"R{i+1}",
                value="330",
                footprint="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal",
                symbol="Device:R",
                x=170.0,
                y=50.0 + (i * 15.0)
            )
            netlist.add_component(resistor)
            
            netlist.connect(f"LED{i+1}_ANODE", f"D{i+1}", "2")
            netlist.connect(f"LED{i+1}_ANODE", f"R{i+1}", "1")
            netlist.connect(f"LED{i+1}_GPIO", f"R{i+1}", "2")
            netlist.connect(f"LED{i+1}_GPIO", "U1", str(2 + i))
            netlist.connect("GND", f"D{i+1}", "1")
        
        if sensore == "IR":
            ir_sensor = Component(
                reference="U2",
                value="IR_Sensor",
                footprint="Sensor:Sensor_IR_HC-SR501",
                symbol="Sensor:IR_Sensor",
                x=50.0,
                y=150.0
            )
            netlist.add_component(ir_sensor)
            
            netlist.connect("VCC", "U2", "1")
            netlist.connect("GND", "U2", "2")
            netlist.connect("IR_OUT", "U2", "3")
            netlist.connect("IR_OUT", "U1", "4")
        
        netlist.connect("VCC", "U1", "1")
        netlist.connect("GND", "U1", "14")
        netlist.connect("GND", "U1", "17")
        
        return netlist


class ESP32Template:
    """Template for ESP32-based circuits"""
    
    ESP32_PINS = {
        "3V3": "1",
        "EN": "2",
        "VP": "3",
        "VN": "4",
        "IO34": "5",
        "IO35": "6",
        "IO32": "7",
        "IO33": "8",
        "IO25": "9",
        "IO26": "10",
        "IO27": "11",
        "IO14": "12",
        "IO12": "13",
        "GND_L": "14",
        "IO13": "15",
        "VIN": "16",
        "GND_R": "17",
        "IO23": "18",
        "IO22": "19",
        "TX0": "20",
        "RX0": "21",
        "IO21": "22",
        "IO19": "23",
        "IO18": "24",
        "IO5": "25",
        "IO17": "26",
        "IO16": "27",
        "IO4": "28",
        "IO0": "29",
        "IO2": "30",
        "IO15": "31",
    }
    
    @staticmethod
    def get_pin_number(pin_name: str) -> str:
        """Get the pin number for a given pin name"""
        return ESP32Template.ESP32_PINS.get(pin_name, "0")
