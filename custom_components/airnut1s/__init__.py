"""Airnut1s Platform"""

import logging
import datetime
import json
import select
import voluptuous as vol
import threading
import time
import requests
from urllib import parse

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType

from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_SCAN_INTERVAL,
)

from .const import (
    DOMAIN,
    ATTR_TEMPERATURE,
    ATTR_HUMIDITY,
    ATTR_PM25,
    ATTR_CO2,
    ATTR_CH2O,
    ATTR_VOLUME,
    ATTR_TIME,
    ATTR_BATTERY_CHARGING,
    ATTR_BATTERY_LEVEL,
    ATTR_WEATHE,
    ATTR_WEATHE_TEMP,
    ATTR_WEATHE_WIND,
    ATTR_WEATHE_AQI,
    ATTR_WEATHE_PM25,
    ATTR_WEATHE_TOMORROW_STATUS,
    ATTR_WEATHE_TOMORROW_TEMP,
    ATTR_WEATHE_TOMORROW_WIND,

)

CONF_NIGHT_START_HOUR = "night_start_hour"
CONF_NIGHT_END_HOUR = "night_end_hour"
CONF_IS_NIGHT_UPDATE = "is_night_update"
HOST_IP = "0.0.0.0"
CONF_WEATHE_CODE = "weathe_code"

SCAN_INTERVAL = datetime.timedelta(seconds=600)
ZERO_TIME = datetime.datetime.fromtimestamp(0)

weathestate= 0
weathe_status = ""
weathe_temp = ""
weathe_wind = ""
weathe_aqi = ""
weathe_pm25 = ""
tomorrow = ""
weathe_tomorrow_status = ""
weathe_tomorrow_temp = ""
weathe_tomorrow_wind = ""
weathe_code = "北京"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_NIGHT_START_HOUR, default=ZERO_TIME): cv.datetime,
                vol.Optional(CONF_NIGHT_END_HOUR, default=ZERO_TIME): cv.datetime,
                vol.Optional(CONF_IS_NIGHT_UPDATE, default=True): cv.boolean,
                vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
                vol.Optional(CONF_WEATHE_CODE, default="北京"): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

_LOGGER = logging.getLogger(__name__)

ip_data_dict = {}
socket_ip_dict = {}

def setup(hass, config):
    global weathe_code
    """Set up platform using YAML."""
    night_start_hour = config[DOMAIN].get(CONF_NIGHT_START_HOUR)
    night_end_hour = config[DOMAIN].get(CONF_NIGHT_END_HOUR)
    is_night_update = config[DOMAIN].get(CONF_IS_NIGHT_UPDATE)
    scan_interval = config[DOMAIN].get(CONF_SCAN_INTERVAL)
    weathe_code = config[DOMAIN].get(CONF_WEATHE_CODE)

    run_weather = threading.Thread(target=airnut1s_weather)  #新建天气循环线程
    run_weather.start()

    server = Airnut1sSocketServer(night_start_hour, night_end_hour, is_night_update, scan_interval, weathe_code, config)

    hass.data[DOMAIN] = {
        'server': server
    }
    return True

def airnut1s_weather():
    global weathestate
    global weathe_status
    global weathe_temp
    global weathe_wind
    global weathe_aqi
    global weathe_pm25
    global weathe_tomorrow_status
    global weathe_tomorrow_temp
    global weathe_tomorrow_wind
    global weathe_code
    errcount = 0
    wet_dataA={"晴":0,"阴":1,"多云":1,"雨":3,"阵雨":3,"雷阵雨":3,"雷阵雨伴有冰雹":3,"雨夹雪":6,"小雨":3,"中雨":3,"大雨":3,"暴雨":3,"大暴雨":3,"特大暴雨":3,"阵雪":5,"小雪":5,"中雪":5,"大雪":5,"暴雪":5,"雾":2,"冻雨":6,"沙尘暴":2,"小雨转中雨":3,"中雨转大雨":3,"大雨转暴雨":3,"暴雨转大暴雨":3,"大暴雨转特大暴雨":3,"小雪转中雪":5,"中雪转大雪":5,"大雪转暴雪":5,"浮沉":2,"扬沙":2,"强沙尘暴":2,"霾":2}
    header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36'}
    #_LOGGER.warning("1S weathe_code %s", weathe_code )
    while True:
        datayesorno = False
        try:
            res = requests.get('https://api.help.bj.cn/apis/weather2d/?id='+ parse.quote(str(weathe_code)),headers=header)
#             res = requests.get('https://api.help.bj.cn/apis/weather/?id='+str(weathe_code),headers=header)
            #print('https://api.help.bj.cn/apis/weather/?id='+str(weathe_code))
            res.encoding='utf-8'
            if res.status_code==200:
                jsonData = res.json()
                jsonwt = jsonData['weather']
                datayesorno = True
                #_LOGGER.warning("1S res %s", res.json())
                #print(jsonData)
        except:
            continue
        if datayesorno:
            print(jsonData['weather'])
            weathe_status = jsonData['weather']
            weathe_temp = jsonData['temp']
            weathe_wind = jsonData['wind']
            weathe_aqi = jsonData['aqi']
            weathe_pm25 = jsonData['pm25']
            tomorrow = jsonData.get("tomorrow")
            weathe_tomorrow_status = tomorrow['weather']
            weathe_tomorrow_temp = tomorrow['temp']
            weathe_tomorrow_wind = tomorrow['wind']
            try:
                weathestate = wet_dataA[jsonData['weather']]
            except:
                continue
            errcount = 0
            time.sleep(600)
        else:
            errcount = errcount + 1
            if errcount >= 3:
                errcount = 0
                #print(res.text())
                time.sleep(600)
            else:
                time.sleep(30)

def get_time():
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

def get_time_unix():
    return int((datetime.datetime.now() + datetime.timedelta(hours=8)).timestamp())

async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry):
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    hass.config_entries.async_forward_entry_unload(entry, "sensor")

    await hass.async_add_executor_job(hass.data[DOMAIN]['server'].unload)

    return True

class Airnut1sSocketServer:

    def __init__(self, night_start_hour, night_end_hour, is_night_update, scan_interval, weathe_code, config):
        self._lastUpdateTime = ZERO_TIME
        self._night_start_hour = night_start_hour.strftime("%H%M%S")
        self._night_end_hour = night_end_hour.strftime("%H%M%S")
        self._is_night_update = is_night_update
        self._scan_interval = scan_interval

        self._weathe_code = weathe_code
        self._config = config

        self._socketServer = socket(AF_INET, SOCK_STREAM)
        self._socketServer.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        try:
            # port for Airnut 1s
            self._socketServer.bind((HOST_IP, 10511))
            # port for Airnut 2
            self._socketServer.bind((HOST_IP, 10512))
            self._socketServer.listen(5)
        except OSError as e:
            _LOGGER.error("server got %s", e)
            pass

        global socket_ip_dict
        socket_ip_dict[self._socketServer] = HOST_IP

        _LOGGER.debug("socket Server loaded")
        self.update()

    def get_state(self):
        return "new"

    def object_to_json_data(self, object):
        return json.dumps(object).encode('utf-8')

    def json_string_to_object(self, data):
        try:
            return json.loads(data)
        except:
            return None

    def update(self):
        global socket_ip_dict

        read_sockets, write_sockets, error_sockets = select.select(socket_ip_dict.keys(), [], [], 0)

        self.deal_error_sockets(error_sockets)
        self.deal_read_sockets(read_sockets)

        now_time = datetime.datetime.now()
        if now_time - self._lastUpdateTime < self._scan_interval:
            return True

        self._lastUpdateTime = now_time

        now_time_str = datetime.datetime.now().strftime("%H%M%S")
        if ((self._is_night_update is False) and
            (self._night_start_hour < now_time_str or self._night_end_hour > now_time_str)):
            return True

        self.deal_write_sockets(socket_ip_dict.keys())

        return True

    def deal_error_sockets(self, error_sockets):
        global socket_ip_dict
        for sock in error_sockets:
            del socket_ip_dict[sock]

    def deal_read_sockets(self, read_sockets):
        volume_msg = {"sendback_appserver": 100000007,"param": {"volume": 0,"socket_id": 100000007,"check_key": "s_set_volume19085"},"volume": 0,"p": "set_volume","type": "control","check_key": "s_set_volume19085"}
        check_msg = {"sendback_appserver": 100000007,"param": {"socket_id": 100000007,"type": 1,"check_key": "s_get19085"},"p": "get","type": "control","check_key": "s_get19085"}

        global weathestate
        weathe_msg = {"common": {"code": 0, "protocol": "get_weather"}, "param": {"weather": "weathercode", "time": get_time_unix()}}
        weathe_msg=json.dumps(weathe_msg)
        weathe_msg=weathe_msg.replace("weathercode",str(weathestate))
        weathe_msg=json.loads(weathe_msg)

        global ip_data_dict
        for sock in read_sockets:
            if sock == self._socketServer:
                _LOGGER.info("going to accept new connection")
                try:
                    sockfd, (host, _) = sock.accept()
                    socket_ip_dict[sockfd] = host
                    _LOGGER.info("Client (%s) connected", socket_ip_dict[sockfd])
                    try:
                        sockfd.send(self.object_to_json_data(volume_msg))
                        sockfd.send(self.object_to_json_data(check_msg))
                    except OSError as e:
                        _LOGGER.error("Client error 1 %s", e)
                        sockfd.shutdown(2)
                        sockfd.close()
                        del socket_ip_dict[sockfd]
                        continue

                except OSError:
                    _LOGGER.warning("Client accept failed")
                    continue
            else:
                originData = None
                try:
                    originData = sock.recv(1024)
                    _LOGGER.debug("Receive originData %s", originData)
                except OSError as e:
                    _LOGGER.warning("Processing Client error 2 %s", e)
                    continue
                if originData:
                    datas = originData.decode('utf-8').split("\n\r")
                    for singleData in datas:
                        jsonData = self.json_string_to_object(singleData)
                        if (jsonData is not None and
                            jsonData["p"] == "log_in"):
                            sock.send(self.object_to_json_data({"type": "client", "socket_id": 18567, "result": 0, "p": "log_in"}))
                        if (jsonData is not None and
                            jsonData["p"] == "post"):
                            ip_data_dict[socket_ip_dict[sock]] = {
                                ATTR_PM25: int(jsonData["param"]["indoor"]["pm25"]),
                                ATTR_TEMPERATURE: format(float(jsonData["param"]["indoor"]["t"]), '.1f'),
                                ATTR_HUMIDITY: format(float(jsonData["param"]["indoor"]["h"]), '.1f'),
                                ATTR_CO2: int(jsonData["param"]["indoor"]["co2"]),
                                ATTR_CH2O: int(jsonData["param"]["indoor"]["hcho"]),
                                ATTR_BATTERY_CHARGING: "off" if int(jsonData["param"]["indoor"]["charge"]) == 0 else 'on',
                                ATTR_BATTERY_LEVEL: int(jsonData["param"]["indoor"]["soc"]),
                                ATTR_TIME: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                ATTR_WEATHE: weathe_status,
                                ATTR_WEATHE_TEMP: weathe_temp,
                                ATTR_WEATHE_WIND: weathe_wind,
                                ATTR_WEATHE_AQI: weathe_aqi,
                                ATTR_WEATHE_PM25: weathe_pm25,
                                ATTR_WEATHE_TOMORROW_STATUS: weathe_tomorrow_status,
                                ATTR_WEATHE_TOMORROW_TEMP: weathe_tomorrow_temp,
                                ATTR_WEATHE_TOMORROW_WIND: weathe_tomorrow_wind,
                            }
                            _LOGGER.debug("ip_data_dict %s", ip_data_dict)

    def deal_write_sockets(self, write_sockets):
        global socket_ip_dict
        global weathestate
        check_msg = {"sendback_appserver": 100000007,"param": {"socket_id": 100000007,"type": 1,"check_key": "s_get19085"},"p": "get","type": "control","check_key": "s_get19085"}
        for sock in write_sockets:
            if sock == self._socketServer:
                continue
            try:
                sock.send(self.object_to_json_data(check_msg))
            except:
                del socket_ip_dict[sock]


    def get_data(self, ip):
        try:
            global ip_data_dict
            return ip_data_dict[ip]
        except:
            return {}

    def unload(self):
        """Signal shutdown of sock."""
        _LOGGER.info("Airnut1sSensor Sock close")
        self._socketServer.shutdown(2)
        self._socketServer.close()
