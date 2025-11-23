"""
Component catalog with ESP32, sensors, actuators, and other common components
"""

from app.models import Component, ComponentPin, ComponentCategory, PinRole


COMPONENT_CATALOG = {
    "ESP32-DevKitC": Component(
        id="ESP32-DevKitC",
        category=ComponentCategory.MCU,
        name="ESP32-DevKitC",
        symbol="MCU_Module:ESP32-DevKitC",
        footprint="Module:ESP32-DevKitC",
        description="ESP32 Development Board with WiFi and Bluetooth",
        width_mm=27.9,
        height_mm=54.4,
        typical_current_ma=80,
        pins=[
            ComponentPin(number="1", name="3V3", role=PinRole.POWER_OUT, voltage_min=3.3, voltage_max=3.3, current_ma=500),
            ComponentPin(number="2", name="EN", role=PinRole.GPIO),
            ComponentPin(number="3", name="VP", role=PinRole.GPIO),
            ComponentPin(number="4", name="VN", role=PinRole.GPIO),
            ComponentPin(number="5", name="IO34", role=PinRole.GPIO),
            ComponentPin(number="6", name="IO35", role=PinRole.GPIO),
            ComponentPin(number="7", name="IO32", role=PinRole.GPIO, supports_pwm=True),
            ComponentPin(number="8", name="IO33", role=PinRole.GPIO, supports_pwm=True),
            ComponentPin(number="9", name="IO25", role=PinRole.GPIO, supports_pwm=True),
            ComponentPin(number="10", name="IO26", role=PinRole.GPIO, supports_pwm=True),
            ComponentPin(number="11", name="IO27", role=PinRole.GPIO, supports_pwm=True),
            ComponentPin(number="12", name="IO14", role=PinRole.GPIO, supports_pwm=True),
            ComponentPin(number="13", name="IO12", role=PinRole.GPIO, supports_pwm=True),
            ComponentPin(number="14", name="GND", role=PinRole.GROUND),
            ComponentPin(number="15", name="IO13", role=PinRole.GPIO, supports_pwm=True),
            ComponentPin(number="16", name="VIN", role=PinRole.POWER_IN, voltage_min=4.5, voltage_max=12.0),
            ComponentPin(number="17", name="GND", role=PinRole.GROUND),
            ComponentPin(number="18", name="IO23", role=PinRole.GPIO, supports_pwm=True),
            ComponentPin(number="19", name="IO22", role=PinRole.GPIO, supports_i2c=True),
            ComponentPin(number="20", name="TX0", role=PinRole.GPIO),
            ComponentPin(number="21", name="RX0", role=PinRole.GPIO),
            ComponentPin(number="22", name="IO21", role=PinRole.GPIO, supports_i2c=True),
            ComponentPin(number="23", name="IO19", role=PinRole.GPIO, supports_spi=True),
            ComponentPin(number="24", name="IO18", role=PinRole.GPIO, supports_pwm=True, supports_spi=True),
            ComponentPin(number="25", name="IO5", role=PinRole.GPIO, supports_pwm=True, supports_spi=True),
            ComponentPin(number="26", name="IO17", role=PinRole.GPIO),
            ComponentPin(number="27", name="IO16", role=PinRole.GPIO),
            ComponentPin(number="28", name="IO4", role=PinRole.GPIO, supports_pwm=True),
            ComponentPin(number="29", name="IO0", role=PinRole.GPIO),
            ComponentPin(number="30", name="IO2", role=PinRole.GPIO, supports_pwm=True),
            ComponentPin(number="31", name="IO15", role=PinRole.GPIO, supports_pwm=True),
        ]
    ),
    
    "SG90_servo": Component(
        id="SG90_servo",
        category=ComponentCategory.ACTUATOR,
        name="Servo SG90",
        symbol="Connector:Servo_Connector",
        footprint="Connector:PinHeader_1x03_P2.54mm_Vertical",
        description="Micro servo motor SG90",
        width_mm=10.0,
        height_mm=7.5,
        typical_current_ma=500,
        pins=[
            ComponentPin(number="1", name="VCC", role=PinRole.POWER_IN, voltage_min=4.8, voltage_max=6.0, current_ma=500),
            ComponentPin(number="2", name="GND", role=PinRole.GROUND),
            ComponentPin(number="3", name="PWM", role=PinRole.SIGNAL_IN),
        ]
    ),
    
    "IR_sensor": Component(
        id="IR_sensor",
        category=ComponentCategory.SENSOR,
        name="IR Proximity Sensor",
        symbol="Sensor:IR_Sensor",
        footprint="Sensor:Sensor_IR_HC-SR501",
        description="Infrared proximity sensor",
        width_mm=10.0,
        height_mm=10.0,
        typical_current_ma=20,
        pins=[
            ComponentPin(number="1", name="VCC", role=PinRole.POWER_IN, voltage_min=3.3, voltage_max=5.0, current_ma=20),
            ComponentPin(number="2", name="GND", role=PinRole.GROUND),
            ComponentPin(number="3", name="OUT", role=PinRole.SIGNAL_OUT),
        ]
    ),
    
    "ultrasonic_sensor": Component(
        id="ultrasonic_sensor",
        category=ComponentCategory.SENSOR,
        name="Ultrasonic Distance Sensor HC-SR04",
        symbol="Sensor:HC-SR04",
        footprint="Sensor:HC-SR04",
        description="Ultrasonic distance sensor",
        width_mm=10.0,
        height_mm=10.0,
        typical_current_ma=15,
        pins=[
            ComponentPin(number="1", name="VCC", role=PinRole.POWER_IN, voltage_min=5.0, voltage_max=5.0, current_ma=15),
            ComponentPin(number="2", name="TRIG", role=PinRole.SIGNAL_IN),
            ComponentPin(number="3", name="ECHO", role=PinRole.SIGNAL_OUT),
            ComponentPin(number="4", name="GND", role=PinRole.GROUND),
        ]
    ),
    
    "LED_5mm": Component(
        id="LED_5mm",
        category=ComponentCategory.LED,
        name="LED 5mm",
        symbol="Device:LED",
        footprint="LED_THT:LED_D5.0mm",
        description="Standard 5mm LED",
        width_mm=5.0,
        height_mm=5.0,
        typical_current_ma=20,
        pins=[
            ComponentPin(number="1", name="K", role=PinRole.GROUND),
            ComponentPin(number="2", name="A", role=PinRole.SIGNAL_IN, current_ma=20),
        ]
    ),
    
    "resistor_330": Component(
        id="resistor_330",
        category=ComponentCategory.RESISTOR,
        name="Resistor 330Ω",
        symbol="Device:R",
        footprint="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal",
        description="330 Ohm resistor for LED current limiting",
        width_mm=10.16,
        height_mm=2.5,
        typical_current_ma=0,
        pins=[
            ComponentPin(number="1", name="~", role=PinRole.SIGNAL_IN),
            ComponentPin(number="2", name="~", role=PinRole.SIGNAL_OUT),
        ]
    ),
    
    "IRLZ44N_mosfet": Component(
        id="IRLZ44N_mosfet",
        category=ComponentCategory.ACTUATOR,
        name="IRLZ44N N-Channel MOSFET",
        symbol="Device:Q_NMOS_GDS",
        footprint="Package_TO_SOT_THT:TO-220-3_Vertical",
        description="Logic-level N-channel MOSFET, 55V 47A",
        width_mm=10.0,
        height_mm=15.0,
        typical_current_ma=0,
        pins=[
            ComponentPin(number="1", name="G", role=PinRole.SIGNAL_IN),
            ComponentPin(number="2", name="D", role=PinRole.POWER_OUT),
            ComponentPin(number="3", name="S", role=PinRole.GROUND),
        ]
    ),
    
    "relay_12V": Component(
        id="relay_12V",
        category=ComponentCategory.ACTUATOR,
        name="Relay 12V SPDT",
        symbol="Relay:Relay_SPDT",
        footprint="Relay_THT:Relay_SPDT_Finder_40.52",
        description="12V SPDT relay, 10A contacts",
        width_mm=20.0,
        height_mm=15.0,
        typical_current_ma=80,
        pins=[
            ComponentPin(number="1", name="COIL+", role=PinRole.POWER_IN, voltage_min=12.0, voltage_max=12.0, current_ma=80),
            ComponentPin(number="2", name="COIL-", role=PinRole.GROUND),
            ComponentPin(number="3", name="COM", role=PinRole.SIGNAL_IN),
            ComponentPin(number="4", name="NO", role=PinRole.SIGNAL_OUT),
            ComponentPin(number="5", name="NC", role=PinRole.SIGNAL_OUT),
        ]
    ),
    
    "linear_actuator_12V": Component(
        id="linear_actuator_12V",
        category=ComponentCategory.ACTUATOR,
        name="Linear Actuator 12V",
        symbol="Motor:Motor_DC",
        footprint="Connector:PinHeader_1x02_P2.54mm_Vertical",
        description="12V linear actuator, 18cm stroke, 2A max",
        width_mm=10.0,
        height_mm=10.0,
        typical_current_ma=2000,
        pins=[
            ComponentPin(number="1", name="+", role=PinRole.POWER_IN, voltage_min=12.0, voltage_max=12.0, current_ma=2000),
            ComponentPin(number="2", name="-", role=PinRole.GROUND),
        ]
    ),
    
    "terminal_block_2pin": Component(
        id="terminal_block_2pin",
        category=ComponentCategory.CONNECTOR,
        name="Terminal Block 2-pin",
        symbol="Connector:Screw_Terminal_01x02",
        footprint="TerminalBlock:TerminalBlock_bornier-2_P5.08mm",
        description="2-pin screw terminal block, 5.08mm pitch",
        width_mm=10.16,
        height_mm=8.5,
        typical_current_ma=0,
        pins=[
            ComponentPin(number="1", name="Pin_1", role=PinRole.POWER_IN),
            ComponentPin(number="2", name="Pin_2", role=PinRole.GROUND),
        ]
    ),
    
    "LM7805_regulator": Component(
        id="LM7805_regulator",
        category=ComponentCategory.CONNECTOR,
        name="LM7805 5V Regulator",
        symbol="Regulator_Linear:L7805",
        footprint="Package_TO_SOT_THT:TO-220-3_Vertical",
        description="5V 1.5A linear voltage regulator",
        width_mm=10.0,
        height_mm=15.0,
        typical_current_ma=5,
        pins=[
            ComponentPin(number="1", name="VIN", role=PinRole.POWER_IN, voltage_min=7.0, voltage_max=35.0),
            ComponentPin(number="2", name="GND", role=PinRole.GROUND),
            ComponentPin(number="3", name="VOUT", role=PinRole.POWER_OUT, voltage_min=5.0, voltage_max=5.0, current_ma=1500),
        ]
    ),
    
    "diode_1N4007": Component(
        id="diode_1N4007",
        category=ComponentCategory.CONNECTOR,
        name="1N4007 Diode",
        symbol="Device:D",
        footprint="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal",
        description="1A 1000V rectifier diode (flyback protection)",
        width_mm=10.16,
        height_mm=2.5,
        typical_current_ma=0,
        pins=[
            ComponentPin(number="1", name="K", role=PinRole.GROUND),
            ComponentPin(number="2", name="A", role=PinRole.SIGNAL_IN),
        ]
    ),
    
    "LED_bicolor": Component(
        id="LED_bicolor",
        category=ComponentCategory.LED,
        name="LED Bicolor Red/Green",
        symbol="Device:LED_Dual_2pin",
        footprint="LED_THT:LED_D5.0mm-3",
        description="Bicolor LED red/green common cathode",
        width_mm=5.0,
        height_mm=5.0,
        typical_current_ma=40,
        pins=[
            ComponentPin(number="1", name="RED", role=PinRole.SIGNAL_IN, current_ma=20),
            ComponentPin(number="2", name="K", role=PinRole.GROUND),
            ComponentPin(number="3", name="GREEN", role=PinRole.SIGNAL_IN, current_ma=20),
        ]
    ),
    
    "MAX9814_microphone": Component(
        id="MAX9814_microphone",
        category=ComponentCategory.SENSOR,
        name="MAX9814 Microphone Module",
        symbol="Sensor:Microphone",
        footprint="Connector:PinHeader_1x03_P2.54mm_Vertical",
        description="MAX9814 microphone amplifier module with AGC and analog output",
        width_mm=10.0,
        height_mm=10.0,
        typical_current_ma=3,
        pins=[
            ComponentPin(number="1", name="VCC", role=PinRole.POWER_IN, voltage_min=3.3, voltage_max=5.0, current_ma=3),
            ComponentPin(number="2", name="GND", role=PinRole.GROUND),
            ComponentPin(number="3", name="OUT", role=PinRole.SIGNAL_OUT),
        ]
    ),
    
    "LED_strip_5V": Component(
        id="LED_strip_5V",
        category=ComponentCategory.LED,
        name="LED Strip RGB 5V",
        symbol="Device:LED_Strip",
        footprint="Connector:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
        description="RGB LED Strip 5V, 500mm length, requires external 5V power",
        width_mm=10.0,
        height_mm=5.0,
        typical_current_ma=3000,
        pins=[
            ComponentPin(number="1", name="+5V", role=PinRole.POWER_IN, voltage_min=5.0, voltage_max=5.0, current_ma=3000),
            ComponentPin(number="2", name="GND", role=PinRole.GROUND),
        ]
    ),
    
    "resistor_220": Component(
        id="resistor_220",
        category=ComponentCategory.RESISTOR,
        name="Resistor 220Ω",
        symbol="Device:R",
        footprint="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal",
        description="220 Ohm resistor for MOSFET gate series",
        width_mm=10.16,
        height_mm=2.5,
        typical_current_ma=0,
        pins=[
            ComponentPin(number="1", name="~", role=PinRole.SIGNAL_IN),
            ComponentPin(number="2", name="~", role=PinRole.SIGNAL_OUT),
        ]
    ),
    
    "resistor_100k": Component(
        id="resistor_100k",
        category=ComponentCategory.RESISTOR,
        name="Resistor 100kΩ",
        symbol="Device:R",
        footprint="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal",
        description="100k Ohm resistor for MOSFET gate pulldown",
        width_mm=10.16,
        height_mm=2.5,
        typical_current_ma=0,
        pins=[
            ComponentPin(number="1", name="~", role=PinRole.SIGNAL_IN),
            ComponentPin(number="2", name="~", role=PinRole.SIGNAL_OUT),
        ]
    ),
    
    "capacitor_100nF": Component(
        id="capacitor_100nF",
        category=ComponentCategory.RESISTOR,
        name="Capacitor 100nF",
        symbol="Device:C",
        footprint="Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
        description="100nF ceramic capacitor for bypass/decoupling",
        width_mm=5.0,
        height_mm=2.5,
        typical_current_ma=0,
        pins=[
            ComponentPin(number="1", name="~", role=PinRole.SIGNAL_IN),
            ComponentPin(number="2", name="~", role=PinRole.GROUND),
        ]
    ),
    
    "capacitor_470uF": Component(
        id="capacitor_470uF",
        category=ComponentCategory.RESISTOR,
        name="Capacitor 470µF",
        symbol="Device:CP",
        footprint="Capacitor_THT:CP_Radial_D8.0mm_P3.50mm",
        description="470µF electrolytic capacitor for power supply filtering",
        width_mm=8.0,
        height_mm=11.5,
        typical_current_ma=0,
        pins=[
            ComponentPin(number="1", name="+", role=PinRole.POWER_IN),
            ComponentPin(number="2", name="-", role=PinRole.GROUND),
        ]
    ),
    
    "capacitor_1000uF": Component(
        id="capacitor_1000uF",
        category=ComponentCategory.RESISTOR,
        name="Capacitor 1000µF",
        symbol="Device:CP",
        footprint="Capacitor_THT:CP_Radial_D10.0mm_P5.00mm",
        description="1000µF electrolytic capacitor for power supply filtering",
        width_mm=10.0,
        height_mm=12.5,
        typical_current_ma=0,
        pins=[
            ComponentPin(number="1", name="+", role=PinRole.POWER_IN),
            ComponentPin(number="2", name="-", role=PinRole.GROUND),
        ]
    ),
    
    "JST_XH_2pin": Component(
        id="JST_XH_2pin",
        category=ComponentCategory.CONNECTOR,
        name="JST-XH 2-pin Connector",
        symbol="Connector:Conn_01x02_Pin",
        footprint="Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
        description="JST-XH 2-pin connector for LED strip output",
        width_mm=5.0,
        height_mm=7.0,
        typical_current_ma=0,
        pins=[
            ComponentPin(number="1", name="Pin_1", role=PinRole.POWER_OUT),
            ComponentPin(number="2", name="Pin_2", role=PinRole.GROUND),
        ]
    ),
    
    "JST_XH_3pin": Component(
        id="JST_XH_3pin",
        category=ComponentCategory.CONNECTOR,
        name="JST-XH 3-pin Connector",
        symbol="Connector:Conn_01x03_Pin",
        footprint="Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical",
        description="JST-XH 3-pin connector for microphone input",
        width_mm=7.5,
        height_mm=7.0,
        typical_current_ma=0,
        pins=[
            ComponentPin(number="1", name="Pin_1", role=PinRole.POWER_IN),
            ComponentPin(number="2", name="Pin_2", role=PinRole.GROUND),
            ComponentPin(number="3", name="Pin_3", role=PinRole.SIGNAL_IN),
        ]
    ),
}


def get_component(component_id: str) -> Component:
    """Get component from catalog by ID"""
    return COMPONENT_CATALOG.get(component_id)


def get_components_by_category(category: ComponentCategory) -> list[Component]:
    """Get all components of a specific category"""
    return [comp for comp in COMPONENT_CATALOG.values() if comp.category == category]


def find_available_pwm_pins(esp32_model: str, exclude_pins: list[str] = None) -> list[ComponentPin]:
    """Find available PWM-capable pins on ESP32"""
    if exclude_pins is None:
        exclude_pins = []
    
    esp32 = get_component(esp32_model)
    if not esp32:
        return []
    
    return [pin for pin in esp32.pins 
            if pin.supports_pwm and pin.number not in exclude_pins and pin.role == PinRole.GPIO]


def find_available_gpio_pins(esp32_model: str, exclude_pins: list[str] = None) -> list[ComponentPin]:
    """Find available GPIO pins on ESP32"""
    if exclude_pins is None:
        exclude_pins = []
    
    esp32 = get_component(esp32_model)
    if not esp32:
        return []
    
    return [pin for pin in esp32.pins 
            if pin.number not in exclude_pins and pin.role == PinRole.GPIO]
