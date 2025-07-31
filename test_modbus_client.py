#!/usr/bin/env python3
"""
Test client for Haier Modbus Server
This script tests the basic functionality of the ESP32 Modbus server
controlling a Haier air conditioner.
"""

import time
import sys
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ModbusException

# Configuration
ESP32_IP = "192.168.1.100"  # Change to your ESP32 IP
MODBUS_PORT = 502
DEVICE_ADDRESS = 0x1F  # 31 in decimal

class HaierModbusClient:
    def __init__(self, host, port=502, device_addr=0x1F):
        self.host = host
        self.port = port
        self.device_addr = device_addr
        self.client = None
        
    def connect(self):
        """Connect to the Modbus server"""
        try:
            self.client = ModbusTcpClient(self.host, port=self.port)
            if self.client.connect():
                print(f"✓ Connected to Modbus server at {self.host}:{self.port}")
                return True
            else:
                print(f"✗ Failed to connect to {self.host}:{self.port}")
                return False
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the Modbus server"""
        if self.client:
            self.client.close()
            print("✓ Disconnected from Modbus server")
    
    def read_coil(self, address):
        """Read a coil register"""
        try:
            result = self.client.read_coils(address, 1, unit=self.device_addr)
            if result.isError():
                print(f"✗ Error reading coil {address:#04x}: {result}")
                return None
            return result.bits[0]
        except Exception as e:
            print(f"✗ Exception reading coil {address:#04x}: {e}")
            return None
    
    def write_coil(self, address, value):
        """Write to a coil register"""
        try:
            result = self.client.write_coil(address, value, unit=self.device_addr)
            if result.isError():
                print(f"✗ Error writing coil {address:#04x}: {result}")
                return False
            return True
        except Exception as e:
            print(f"✗ Exception writing coil {address:#04x}: {e}")
            return False
    
    def read_holding_register(self, address):
        """Read a holding register"""
        try:
            result = self.client.read_holding_registers(address, 1, unit=self.device_addr)
            if result.isError():
                print(f"✗ Error reading register {address:#04x}: {result}")
                return None
            return result.registers[0]
        except Exception as e:
            print(f"✗ Exception reading register {address:#04x}: {e}")
            return None
    
    def write_holding_register(self, address, value):
        """Write to a holding register"""
        try:
            result = self.client.write_register(address, value, unit=self.device_addr)
            if result.isError():
                print(f"✗ Error writing register {address:#04x}: {result}")
                return False
            return True
        except Exception as e:
            print(f"✗ Exception writing register {address:#04x}: {e}")
            return False

def test_basic_connectivity(client):
    """Test basic Modbus connectivity"""
    print("\n" + "="*50)
    print("TESTING BASIC CONNECTIVITY")
    print("="*50)
    
    # Test reading AC status
    print("Testing AC status read...")
    status = client.read_coil(0x0001)
    if status is not None:
        print(f"✓ AC Status: {'ON' if status else 'OFF'}")
    else:
        print("✗ Failed to read AC status")
        return False
    
    # Test reading current temperature
    print("Testing temperature read...")
    temp_raw = client.read_holding_register(0x0103)
    if temp_raw is not None:
        temperature = temp_raw / 100.0
        print(f"✓ Current Temperature: {temperature:.2f}°C")
    else:
        print("✗ Failed to read current temperature")
        return False
    
    return True

def test_ac_control(client):
    """Test air conditioner control functions"""
    print("\n" + "="*50)
    print("TESTING AC CONTROL")
    print("="*50)
    
    # Test turning AC on
    print("Testing AC power on...")
    if client.write_coil(0x0001, True):
        time.sleep(1)
        status = client.read_coil(0x0001)
        if status:
            print("✓ AC turned ON successfully")
        else:
            print("✗ AC power on failed - status still OFF")
    else:
        print("✗ Failed to send AC power on command")
        return False
    
    # Test setting mode to cooling
    print("Testing mode change to COOL...")
    if client.write_holding_register(0x0101, 2):  # 2 = Cool mode
        time.sleep(1)
        mode = client.read_holding_register(0x0101)
        if mode == 2:
            print("✓ Mode set to COOL successfully")
        else:
            print(f"✗ Mode change failed - current mode: {mode}")
    else:
        print("✗ Failed to send mode change command")
    
    # Test setting target temperature
    print("Testing target temperature setting...")
    target_temp = 22.0  # 22°C
    target_raw = int(target_temp * 100)  # Convert to 0.01°C scale
    if client.write_holding_register(0x0105, target_raw):
        time.sleep(1)
        temp_raw = client.read_holding_register(0x0105)
        if temp_raw is not None:
            actual_temp = temp_raw / 100.0
            print(f"✓ Target temperature set to {actual_temp:.1f}°C")
        else:
            print("✗ Failed to read back target temperature")
    else:
        print("✗ Failed to set target temperature")
    
    # Test fan speed setting
    print("Testing fan speed setting...")
    if client.write_holding_register(0x0107, 2):  # 2 = Medium speed
        time.sleep(1)
        fan_speed = client.read_holding_register(0x0107)
        fan_names = {0: "Auto", 1: "Low", 2: "Medium", 3: "High"}
        if fan_speed in fan_names:
            print(f"✓ Fan speed set to {fan_names[fan_speed]}")
        else:
            print(f"✗ Unexpected fan speed value: {fan_speed}")
    else:
        print("✗ Failed to set fan speed")
    
    return True

def test_display_control(client):
    """Test display and additional features"""
    print("\n" + "="*50)
    print("TESTING DISPLAY CONTROL")
    print("="*50)
    
    # Test display control
    print("Testing display off...")
    if client.write_coil(0x0002, False):
        time.sleep(1)
        display_state = client.read_coil(0x0002)
        print(f"✓ Display state: {'ON' if display_state else 'OFF'}")
    else:
        print("✗ Failed to control display")
    
    print("Testing display on...")
    if client.write_coil(0x0002, True):
        time.sleep(1)
        display_state = client.read_coil(0x0002)
        print(f"✓ Display state: {'ON' if display_state else 'OFF'}")
    else:
        print("✗ Failed to control display")
    
    return True

def test_status_monitoring(client):
    """Test status monitoring capabilities"""
    print("\n" + "="*50)
    print("TESTING STATUS MONITORING")
    print("="*50)
    
    # Read all status registers
    registers = {
        0x0102: "Active Mode",
        0x0103: "Current Temperature (×100)",
        0x0105: "Target Temperature (×100)",
        0x0106: "Thermostat State",
        0x0107: "Fan Speed",
        0x0109: "Horizontal Vanes",
        0x010A: "Vertical Vanes"
    }
    
    for addr, name in registers.items():
        value = client.read_holding_register(addr)
        if value is not None:
            if "Temperature" in name:
                temp = value / 100.0
                print(f"✓ {name}: {temp:.2f}°C")
            else:
                print(f"✓ {name}: {value}")
        else:
            print(f"✗ Failed to read {name}")
    
    return True

def run_comprehensive_test():
    """Run comprehensive test suite"""
    print("Haier Modbus Server Test Client")
    print("="*50)
    print(f"Target: {ESP32_IP}:{MODBUS_PORT}")
    print(f"Device Address: {DEVICE_ADDRESS:#04x}")
    
    # Create client and connect
    client = HaierModbusClient(ESP32_IP, MODBUS_PORT, DEVICE_ADDRESS)
    
    if not client.connect():
        print("Failed to connect to Modbus server")
        return False
    
    try:
        # Run test suite
        tests = [
            test_basic_connectivity,
            test_ac_control,
            test_display_control,
            test_status_monitoring
        ]
        
        passed = 0
        for test_func in tests:
            try:
                if test_func(client):
                    passed += 1
                    print(f"✓ {test_func.__name__} PASSED")
                else:
                    print(f"✗ {test_func.__name__} FAILED")
            except Exception as e:
                print(f"✗ {test_func.__name__} EXCEPTION: {e}")
        
        print("\n" + "="*50)
        print(f"TEST RESULTS: {passed}/{len(tests)} tests passed")
        print("="*50)
        
        return passed == len(tests)
        
    finally:
        client.disconnect()

def interactive_mode():
    """Interactive mode for manual testing"""
    print("\nInteractive Mode")
    print("Available commands:")
    print("  read_coil <addr>")
    print("  write_coil <addr> <value>")
    print("  read_holding <addr>")
    print("  write_holding <addr> <value>")
    print("  status")
    print("  quit")
    
    client = HaierModbusClient(ESP32_IP, MODBUS_PORT, DEVICE_ADDRESS)
    
    if not client.connect():
        return
    
    try:
        while True:
            try:
                cmd = input("\n> ").strip().split()
                if not cmd:
                    continue
                
                if cmd[0] == "quit":
                    break
                elif cmd[0] == "read_coil" and len(cmd) == 2:
                    addr = int(cmd[1], 0)
                    value = client.read_coil(addr)
                    print(f"Coil {addr:#04x}: {value}")
                elif cmd[0] == "write_coil" and len(cmd) == 3:
                    addr = int(cmd[1], 0)
                    value = bool(int(cmd[2]))
                    result = client.write_coil(addr, value)
                    print(f"Write coil {addr:#04x}: {'OK' if result else 'FAILED'}")
                elif cmd[0] == "read_holding" and len(cmd) == 2:
                    addr = int(cmd[1], 0)
                    value = client.read_holding_register(addr)
                    print(f"Holding {addr:#04x}: {value}")
                elif cmd[0] == "write_holding" and len(cmd) == 3:
                    addr = int(cmd[1], 0)
                    value = int(cmd[2])
                    result = client.write_holding_register(addr, value)
                    print(f"Write holding {addr:#04x}: {'OK' if result else 'FAILED'}")
                elif cmd[0] == "status":
                    test_status_monitoring(client)
                else:
                    print("Invalid command")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                
    finally:
        client.disconnect()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_mode()
    else:
        run_comprehensive_test() 