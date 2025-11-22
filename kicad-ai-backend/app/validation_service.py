"""
Validation service for circuit specifications
Checks electrical feasibility, pin availability, power budget, etc.
"""

from app.models import CircuitSpec, ValidationResult, ComponentPin, PinRole
from app.component_catalog import get_component, find_available_pwm_pins, find_available_gpio_pins
from typing import Dict, List, Tuple


class ValidationService:
    def __init__(self):
        self.used_pins = []
        self.pin_assignments = {}
        self.total_current_ma = 0
        
    def validate_circuit(self, spec: CircuitSpec) -> ValidationResult:
        """
        Validate the circuit specification
        Returns ValidationResult with errors, warnings, and pin assignments
        """
        errors = []
        warnings = []
        self.used_pins = []
        self.pin_assignments = {}
        self.total_current_ma = 0
        
        esp32 = get_component(spec.esp32_model)
        if not esp32:
            errors.append(f"Modello ESP32 '{spec.esp32_model}' non trovato nel catalogo")
            return ValidationResult(valid=False, errors=errors)
        
        # Validate actuators (servos need PWM pins)
        for i, actuator in enumerate(spec.actuators):
            if actuator.kind == "servo":
                for j in range(actuator.count):
                    pin = self._assign_pwm_pin(esp32, f"Servo {i+1}-{j+1}")
                    if not pin:
                        errors.append(f"Pin PWM insufficienti per servo {i+1}-{j+1}")
                    else:
                        servo = get_component("SG90_servo")
                        if servo:
                            self.total_current_ma += servo.typical_current_ma
        
        # Validate sensors (need GPIO pins)
        for i, sensor in enumerate(spec.sensors):
            for j in range(sensor.count):
                if sensor.kind == "IR":
                    pin = self._assign_gpio_pin(esp32, f"Sensore IR {i+1}-{j+1}")
                    if not pin:
                        errors.append(f"Pin GPIO insufficienti per sensore IR {i+1}-{j+1}")
                    else:
                        ir_sensor = get_component("IR_sensor")
                        if ir_sensor:
                            self.total_current_ma += ir_sensor.typical_current_ma
                
                elif sensor.kind == "ultrasuoni" or sensor.kind == "ultrasonic":
                    trig_pin = self._assign_gpio_pin(esp32, f"Sensore ultrasuoni {i+1}-{j+1} TRIG")
                    echo_pin = self._assign_gpio_pin(esp32, f"Sensore ultrasuoni {i+1}-{j+1} ECHO")
                    if not trig_pin or not echo_pin:
                        errors.append(f"Pin GPIO insufficienti per sensore ultrasuoni {i+1}-{j+1}")
                    else:
                        ultrasonic = get_component("ultrasonic_sensor")
                        if ultrasonic:
                            self.total_current_ma += ultrasonic.typical_current_ma
        
        # Validate LEDs (need GPIO pins)
        for i, led in enumerate(spec.status_leds):
            if led.color == "bicolore":
                # Bicolor LED needs 2 GPIO pins
                red_pin = self._assign_gpio_pin(esp32, f"LED bicolore RED")
                green_pin = self._assign_gpio_pin(esp32, f"LED bicolore GREEN")
                if not red_pin or not green_pin:
                    errors.append(f"Pin GPIO insufficienti per LED bicolore")
                else:
                    bicolor_comp = get_component("LED_bicolor")
                    if bicolor_comp:
                        self.total_current_ma += bicolor_comp.typical_current_ma
            else:
                pin = self._assign_gpio_pin(esp32, f"LED {led.color}")
                if not pin:
                    errors.append(f"Pin GPIO insufficienti per LED {led.color}")
                else:
                    led_comp = get_component("LED_5mm")
                    if led_comp:
                        self.total_current_ma += led_comp.typical_current_ma
        
        # Validate high-power actuators (need GPIO for control + driver)
        for i, actuator in enumerate(spec.high_power_actuators):
            pin = self._assign_gpio_pin(esp32, f"Attuatore {actuator.kind} controllo")
            if not pin:
                errors.append(f"Pin GPIO insufficienti per controllo attuatore {actuator.kind}")
            
            # Add driver current to budget
            if actuator.driver_type == "mosfet":
                # MOSFET uses negligible current from GPIO
                pass
            elif actuator.driver_type == "relay":
                relay_comp = get_component("relay_12V")
                if relay_comp:
                    self.total_current_ma += relay_comp.typical_current_ma
        
        # Add ESP32 base current
        self.total_current_ma += esp32.typical_current_ma
        
        # Validate power domains
        if spec.power_domains:
            for domain in spec.power_domains:
                if domain.role == "actuator":
                    # Check actuator power budget
                    actuator_current = sum(a.max_current_ma for a in spec.high_power_actuators)
                    if actuator_current > domain.max_current_ma:
                        errors.append(
                            f"Consumo attuatori ({actuator_current}mA) supera il budget del dominio {domain.name} ({domain.max_current_ma}mA)"
                        )
                        warnings.append(
                            f"Considera un alimentatore più potente per il dominio {domain.name} (almeno {int(actuator_current * 1.2)}mA con margine 20%)"
                        )
        
        # Check power budget
        if self.total_current_ma > spec.power.max_current_ma:
            errors.append(
                f"Consumo totale stimato ({self.total_current_ma}mA) supera il budget di potenza ({spec.power.max_current_ma}mA)"
            )
            warnings.append(
                f"Considera un alimentatore più potente (almeno {int(self.total_current_ma * 1.2)}mA con margine 20%)"
            )
        elif self.total_current_ma > spec.power.max_current_ma * 0.8:
            warnings.append(
                f"Consumo totale ({self.total_current_ma}mA) è vicino al limite ({spec.power.max_current_ma}mA). "
                f"Margine: {spec.power.max_current_ma - self.total_current_ma}mA"
            )
        
        # Check board space (rough estimate)
        total_connectors = sum(a.count for a in spec.actuators) + sum(s.count for s in spec.sensors)
        board_perimeter_mm = 2 * (spec.board_size.width_mm + spec.board_size.height_mm)
        available_edge_mm = board_perimeter_mm - 40  # 10mm margin on each corner
        required_space_mm = total_connectors * 12  # ~12mm per connector with spacing
        
        if required_space_mm > available_edge_mm:
            warnings.append(
                f"Molti connettori ({total_connectors}) per una scheda {spec.board_size.width_mm}x{spec.board_size.height_mm}mm. "
                f"Potrebbero essere troppo vicini."
            )
        
        # Validation summary
        valid = len(errors) == 0
        
        return ValidationResult(
            valid=valid,
            errors=errors,
            warnings=warnings,
            pin_assignments=self.pin_assignments,
            power_budget_ma=self.total_current_ma
        )
    
    def _assign_pwm_pin(self, esp32, label: str) -> ComponentPin:
        """Assign an available PWM pin"""
        available_pins = find_available_pwm_pins(esp32.id, self.used_pins)
        if not available_pins:
            return None
        
        pin = available_pins[0]
        self.used_pins.append(pin.number)
        self.pin_assignments[label] = f"{pin.name} (pin {pin.number})"
        return pin
    
    def _assign_gpio_pin(self, esp32, label: str) -> ComponentPin:
        """Assign an available GPIO pin"""
        available_pins = find_available_gpio_pins(esp32.id, self.used_pins)
        if not available_pins:
            return None
        
        pin = available_pins[0]
        self.used_pins.append(pin.number)
        self.pin_assignments[label] = f"{pin.name} (pin {pin.number})"
        return pin
    
    def get_pin_assignments(self) -> Dict[str, str]:
        """Get the pin assignments made during validation"""
        return self.pin_assignments
    
    def get_power_budget(self) -> int:
        """Get the total power budget in mA"""
        return self.total_current_ma
