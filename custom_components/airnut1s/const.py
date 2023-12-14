""" Constants """
# Base component constants
DOMAIN = "airnut1s"
VERSION = "3.0.9"
ATTRIBUTION = ""

# Configuration
ATTR_TEMPERATURE = "temperature"
ATTR_HUMIDITY = "humidity"
ATTR_PM25 = "pm25"
ATTR_CO2 = "co2"
ATTR_CH2O = "ch2o"
ATTR_VOLUME = "volume"
ATTR_TIME = "time"
ATTR_BATTERY_CHARGING = "charge"
ATTR_BATTERY_LEVEL = "battery"
ATTR_WEATHE = "weathe"
ATTR_WEATHE_TEMP = "weathe_temp"
ATTR_WEATHE_WIND = "weathe_wind"
ATTR_WEATHE_AQI = "weathe_aqi"
ATTR_WEATHE_PM25 = "weathe_pm25"
ATTR_WEATHE_TOMORROW_STATUS = "weathe_tomorrow_status"
ATTR_WEATHE_TOMORROW_TEMP = "weathe_tomorrow_temp"
ATTR_WEATHE_TOMORROW_WIND = "weathe_tomorrow_wind"

#Unit
MEASUREMENT_UNITE_DICT = {
    ATTR_TEMPERATURE: "°C",
    ATTR_HUMIDITY: "%",
    ATTR_PM25: "ug/m³",
    ATTR_CO2: "ppm",
    ATTR_CH2O: "ug/m³",
    ATTR_BATTERY_CHARGING: "",
    ATTR_BATTERY_LEVEL: "%",
    ATTR_WEATHE: "",
    ATTR_WEATHE_TEMP: "",
    ATTR_WEATHE_WIND: "",
    ATTR_WEATHE_AQI: "",
    ATTR_WEATHE_PM25: "",
    ATTR_WEATHE_TOMORROW_STATUS: "",
    ATTR_WEATHE_TOMORROW_TEMP: "",
    ATTR_WEATHE_TOMORROW_WIND: "",
}

# Defaults
DEFAULT_SCAN_INTERVAL = 600
