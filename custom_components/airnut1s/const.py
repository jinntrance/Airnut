""" Constants """
# Base component constants
DOMAIN = "airnut1s"
VERSION = "3.0.7"
ATTRIBUTION = ""

# Configuration
ATTR_TEMPERATURE = "temperature"
ATTR_HUMIDITY = "humidity"
ATTR_PM25 = "pm25"
ATTR_CO2 = "co2"
ATTR_VOLUME = "volume"
ATTR_TIME = "time"
ATTR_BATTERY_CHARGING = "charge"
ATTR_BATTERY_LEVEL = "battery"

#Unit
MEASUREMENT_UNITE_DICT = {
    ATTR_TEMPERATURE: "°C",
    ATTR_HUMIDITY: "%",
    ATTR_PM25: "ug/m³",
    ATTR_CO2: "ppm",
    ATTR_BATTERY_CHARGING: "",
    ATTR_BATTERY_LEVEL: "%"
}

# Defaults
DEFAULT_SCAN_INTERVAL = 600
