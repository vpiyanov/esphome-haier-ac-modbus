# Haier Air Conditioner Modbus Server Configuration

This ESPHome configuration creates a Modbus server that controls a Haier air conditioner using the haier-esphome library. The device acts as a bridge between Modbus TCP/RTU clients and the Haier air conditioner's proprietary protocol.

## Features

- **Modbus Server**: Acts as a Modbus server device with address 0x1F
- **Haier Integration**: Controls Haier air conditioners using the SMARTAIR2 protocol
- **Full Climate Control**: Temperature, mode, fan speed, swing control
- **Display Control**: Control display backlight (health mode and beeper require HON protocol)
- **Real-time Monitoring**: Temperature sensors and status indicators
- **Home Assistant Integration**: Full API integration with Home Assistant

## Hardware Requirements

### ESP32 Development Board
- ESP32-DevKitC or compatible
- Minimum 2MB flash memory
- WiFi capability

### Wiring Connections

#### Haier Air Conditioner Connection
- **TX Pin**: GPIO17 → Connect to Haier RX
- **RX Pin**: GPIO16 → Connect to Haier TX
- **Ground**: GND → Connect to Haier GND
- **Power**: Use appropriate voltage converter if needed

#### Modbus Connection
- **TX Pin**: GPIO18 → Connect to Modbus A/A+ (or D+)
- **RX Pin**: GPIO19 → Connect to Modbus B/B- (or D-)
- **Ground**: GND → Connect to Modbus ground
- **RS485 Converter**: Use MAX485 or similar for RS485 networks

### Optional Components
- **Status LED**: GPIO2 (built-in LED on most ESP32 boards)
- **Flow Control Pin**: Can be added for RS485 networks

## Software Setup

### 1. Clone haier-esphome Library
```bash
git clone https://github.com/paveldn/haier-esphome.git
```

### 2. Update Configuration Paths
Edit the `external_components` section in the YAML file to point to your haier-esphome installation:
```yaml
external_components:
  - source: 
      type: local
      path: /path/to/haier-esphome/components
    components: [ haier ]
```

### 3. Configure WiFi Credentials
Create a `secrets.yaml` file:
```yaml
wifi_ssid: "YourWiFiNetwork"
wifi_password: "YourWiFiPassword"
```

### 4. Update Security Keys
Replace the placeholder keys in the configuration:
- `YOUR_ENCRYPTION_KEY_HERE`: Generate with `esphome run config.yaml`
- `YOUR_OTA_PASSWORD_HERE`: Set a secure password for OTA updates

### 5. Protocol Selection
The configuration uses SMARTAIR2 protocol by default. If you have a newer Haier unit that supports HON protocol:
```yaml
climate:
  - platform: haier
    protocol: HON  # Change from SMARTAIR2 to HON
    # Additional HON features become available:
    # - Beeper control
    # - Health mode
    # - Self-cleaning functions
```

## Modbus Register Mapping

The configuration implements the ONOKOM-AIR-HR-1-MB-B register mapping:

### Coil Registers (Function Codes 01, 05, 15)
| Address | Name | Access | Description |
|---------|------|--------|-------------|
| 0x0001 | Active | R/W | AC On/Off state (0=Off, 1=On) |
| 0x0002 | Screen Light | R/W | Display backlight (0=Off, 1=On) |
| 0x0005 | Beeper | R/W | Sound notifications (0=Off, 1=On) |

### Holding Registers (Function Codes 03, 06, 16)
| Address | Name | Access | Unit | Description |
|---------|------|--------|------|-------------|
| 0x0101 | Mode | R/W | - | 1=Heat, 2=Cool, 3=Auto, 4=Dry, 5=Fan |
| 0x0102 | Active Mode | R | - | Current active mode (0=Off, 1-5=Modes) |
| 0x0103 | Indoor Temperature | R | 0.01°C | Current room temperature |
| 0x0105 | Target Temperature | R/W | 0.01°C | Setpoint temperature (16-32°C) |
| 0x0106 | Thermostat State | R | - | 0=Idle, 1=Heating, 2=Cooling |
| 0x0107 | Fan Speed | R/W | - | 0=Auto, 1=Low, 2=Medium, 3=High |
| 0x0109 | Horizontal Vanes | R/W | - | 1=Swing, 2-8=Fixed positions |
| 0x010A | Vertical Vanes | R/W | - | 0=Stop, 1=Swing, 2-6=Positions |
| 0x0114 | Temperature Correction | R/W | 0.1°C | Temperature offset (-3.0 to +3.0°C) |

## Usage Examples

### Python Modbus Client
```python
from pymodbus.client.sync import ModbusTcpClient

# Connect to ESP32 Modbus server
client = ModbusTcpClient('192.168.1.100', port=502)

# Turn on AC
client.write_coil(0x0001, True, unit=0x1F)

# Set to cooling mode
client.write_register(0x0101, 2, unit=0x1F)

# Set target temperature to 22°C (2200 = 22.00°C)
client.write_register(0x0105, 2200, unit=0x1F)

# Read current temperature
result = client.read_holding_registers(0x0103, 1, unit=0x1F)
temp = result.registers[0] / 100.0  # Convert to °C

client.close()
```

### Home Assistant Configuration
```yaml
# configuration.yaml
modbus:
  - type: tcp
    host: 192.168.1.100  # ESP32 IP address
    port: 502
    
    climates:
      - name: "Haier AC"
        address: 31  # 0x1F in decimal
        input_type: holding
        count: 1
        max_temp: 32
        min_temp: 16
        temp_step: 1
        precision: 1
        
    switches:
      - name: "AC Power"
        address: 1
        slave: 31
        write_type: coil
        
    sensors:
      - name: "AC Current Temperature"
        address: 259  # 0x0103 in decimal
        slave: 31
        input_type: holding
        scale: 0.01
        precision: 2
        unit_of_measurement: "°C"
```

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check UART wiring and baud rates
   - Verify Haier protocol compatibility
   - Check power supply voltage levels

2. **Modbus Communication Errors**
   - Verify Modbus client configuration
   - Check network connectivity
   - Ensure correct device address (0x1F)

3. **Temperature Reading Issues**
   - Verify temperature scaling (0.01°C resolution)
   - Check for sensor calibration needs
   - Ensure AC is powered on

### Debug Logging
Enable debug logging in the configuration:
```yaml
logger:
  level: DEBUG
  logs:
    modbus: DEBUG
    haier: DEBUG
```

### Testing Connectivity
Use a Modbus client tool to test register access:
```bash
# Install modbus tools
pip install pymodbus

# Test connection
modpoll -t 3 -r 259 -c 1 -1 192.168.1.100  # Read temperature
modpoll -t 1 -r 1 -c 1 -1 192.168.1.100    # Read AC state
```

## Advanced Configuration

### Multiple AC Units
To control multiple AC units, create separate UART interfaces and climate components:
```yaml
uart:
  - id: haier_uart_1
    tx_pin: GPIO17
    rx_pin: GPIO16
  - id: haier_uart_2  
    tx_pin: GPIO21
    rx_pin: GPIO22

climate:
  - platform: haier
    id: haier_ac_1
    uart_id: haier_uart_1
  - platform: haier
    id: haier_ac_2
    uart_id: haier_uart_2
```

### Custom Register Mapping
Add custom registers for extended functionality:
```yaml
modbus_controller:
  - modbus_id: modbus_server
    address: 0x1F
    server_registers:
      - address: 0x0200  # Custom register
        value_type: U_WORD
        read_lambda: |-
          return custom_value;
        write_lambda: |-
          custom_value = x;
          return true;
```

### Integration with Home Automation
The device provides REST API endpoints for direct control:
```bash
# Turn on AC via REST API
curl -X POST http://192.168.1.100/switch/haier_display_switch/turn_on

# Get current temperature
curl http://192.168.1.100/sensor/haier_current_temperature
```

## License and Support

This configuration is based on:
- [ESPHome](https://esphome.io/) - Open source home automation platform
- [haier-esphome](https://github.com/paveldn/haier-esphome) - Haier climate component
- [ONOKOM AIR HR-1-MB-B](https://github.com/wirenboard/wb-mqtt-serial) - Modbus register specification

For support:
- ESPHome Community Forum
- Haier-ESPHome GitHub Issues  
- Home Assistant Community 