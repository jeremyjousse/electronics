# TODO : do not power on the sensors and motors if no power is needed

# TODO : battery level
# 
# https://kitronik.co.uk/blogs/resources/raspberry-pi-pico-battery-voltmeter-in-python
# https://peppe8o.com/raspberry-pi-pico-battery-checker/
# https://electrocredible.com/power-raspberry-pi-pico-with-batteries/

# TODO Look at Phew
# https://pypi.org/project/micropython-phew/

import dht
import machine
import network
import ntptime
import secrets
import utime
import socket
import uasyncio as asyncio
import ujson
import urequests
import uselect
import sys



# start the local server to get json data and action panel
START_SERVER = True

# send API call to Home Assistant
SEND_DATA_TO_HOME_ASSISTANT = False

# minimum level of water before stop watering and sending an alert
MIN_WATER_LEVEL = 13000

# minimum moisture level that triggers watering
MIN_MOISTURE_LEVEL = 21000

# sleep time between two waterings
SLEEP_TIME_BETWEEN_WATERINGS = 30 * 60

CSV_DATA_FILE = "data.csv"

CSV_DATA_FIELDS = ["date_time", "moisture", "temperature", "humidity", "water_lever"]

HTML_RESPONSE = """<!DOCTYPE html>
<html>
    <head> <title>Pico W</title> </head>
    <body> <h1>Pico W</h1>
        <p>YOP</p>
    </body>
</html>
"""

# yellow cable
dht_sensor = dht.DHT11(machine.Pin(21, machine.Pin.OUT, machine.Pin.PULL_DOWN))

# orange cable
water_lever_sensor = machine.ADC(machine.Pin(26, machine.Pin.IN))

# purple cable
moisture_sensor = machine.ADC(machine.Pin(27,machine.Pin.IN))


water_pump =machine.Pin(16, mode=machine.Pin.OUT, value=0)

green_led = machine.Pin(13, machine.Pin.OUT, value=0)
orange_led = machine.Pin(14, machine.Pin.OUT, value=0)
red_led = machine.Pin(15, machine.Pin.OUT, value=0)

power_pin = machine.Pin(0, machine.Pin.OUT, value=0)

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.SSID, secrets.PASSWORD)
    sleep_time = 0
    while wlan.isconnected() == False:
        sleep_time+=1
        print('Waiting WIFI connection: ', sleep_time)
        utime.sleep(1)
    print('Connection OK')
    print(wlan.ifconfig())
    green_led.value(1)
    red_led.value(1)
    return wlan.ifconfig()[0]

if START_SERVER == True:
    network_ip_address = wifi_connect()
    # ntptime.settime()

# set GMT+1
utime.localtime()

def measure_io(moisture_sensor, dht_sensor, water_lever_sensor):
    power_pin.value(1)
    utime.sleep(5)
    loc_time = utime.localtime()
    year, month, day, hour, min, sec, _, _ = (loc_time)
    date_time = "{}-{}-{} {}:{}:{}".format(year, month, day, hour, min, sec)
    
    dht_sensor.measure()

    # TODO add last watering
    # last_watering_date_time
    # plus add a global variable

    # TODO add battery level

    measured_data = {
        'date_time': date_time,
        'moisture': 0.0,
        'temperature': 0.0,
        'humidity': 0.0,
        'water_lever': 0.0,
    }

    moisture = moisture_sensor.read_u16()
    measured_data['moisture'] = moisture
    call_home_assistant_api("sensor.watering_system_moisture", moisture)

    temperature = dht_sensor.temperature()
    measured_data['temperature'] = temperature
    call_home_assistant_api("sensor.watering_system_temperature", temperature)

    humidity = dht_sensor.humidity()
    measured_data['humidity'] = humidity
    call_home_assistant_api("sensor.watering_system_humidity", humidity)

    water_level = water_lever_sensor.read_u16()
    measured_data['water_lever'] = water_level
    call_home_assistant_api("sensor.watering_system_water_level", water_level)

    power_pin.value(0)
    return measured_data

def call_home_assistant_api(resource, value):

    if resource == "sensor.watering_system_water_level":
        attributes = {
            "unit_of_measurement": "cm",
            "icon": "mdi:watering-can",
            "friendly_name": "Watering system water level"
        }
    elif resource == "sensor.watering_system_humidity":
        attributes = {
            "unit_of_measurement": "%",
            "icon": "mdi:watering-percent",
            "friendly_name": "Watering system humidity"
        }
    elif resource == "sensor.watering_system_temperature":
        attributes = {
            "unit_of_measurement": "°C",
            "icon": "mdi:temperature-celsius",
            "friendly_name": "Watering system temperature"
        }
    else:
        attributes = {
            "unit_of_measurement": "%",
            "icon": "mdi:watering-percent",
            "friendly_name": "Watering system moisture"
        } 

    data = ujson.dumps({ 'state': value, 'entry.id': resource, 'attributes': attributes}).encode('utf8')
    headers =  {'content-type': 'application/json; charset=utf-8', 'Authorization': 'Bearer {}'.format(secrets.HOME_ASSISTANT_TOKEN)}
    request_url = "{}:{}/api/states/{}".format(secrets.HOME_ASSISTANT_URL, secrets.HOME_ASSISTANT_PORT, resource)
    response = urequests.post(request_url, headers = headers, data = data,  timeout = 10).json()
    print(type(response))

def calculate_moisture(raw_moisture):
    # 64927 = 0%
    # 65311 = 100%
    return 0

# def send_data_to_home_assistant(measured_data):
#     # HOME_ASSISTANT_URL
#     # HOME_ASSISTANT_TOKEN
    
def calculate_water_lever(raw_water_level):
    # 16852 = max - h = 8cm
    # 16339 = 2 - h 4.5cm
    return 0

def write_data_to_log_file(data_file, measured_data):
    with open(data_file, 'a') as csv_file:
        for index, csv_field in enumerate(CSV_DATA_FIELDS):
            csv_file.write(str(measured_data[csv_field]))
            if index != len(CSV_DATA_FIELDS) - 1:
                csv_file.write(";")
            else:
                csv_file.write(("\r\n"))
        
def read_last_data_line_from_log_file(data_file):
    with open(data_file, 'r') as csv_file:
        last_line = csv_file.readlines()[-1]
        data_dict = last_line.split(";")

        measured_data = {}
        for index, data in enumerate(data_dict):
            measured_data[CSV_DATA_FIELDS[index]] = data.strip()
            print(CSV_DATA_FIELDS[index], ": ",data)
        return measured_data

def read_all_data_from_log_file(data_file):
    # return Path(data_file).read_text()
    with open(data_file, 'r') as csv_file:
        return csv_file.read().replace("\r\n","<br>")
        # lines = csv_file.readlines()
        # return "\n\r".join(lines)

class Server:

    def __init__(self, host='0.0.0.0', port=80, backlog=5, timeout=20):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.timeout = timeout

    async def run(self):
        print('Awaiting client connection.')
        self.cid = 0
        self.server = await asyncio.start_server(self.run_client, self.host, self.port, self.backlog)
        while True:
            await asyncio.sleep(100)

    async def run_client(self, reader, writer):
        data = await reader.read(100)
        message = data.decode()

        request_dict = self.parse_request(message)
        
        if request_dict.get("method") == "GET" and request_dict.get("path") == "/all":
            message = self.get_all_measures()
            message_type = "text"
        elif request_dict.get("method") == "GET" and request_dict.get("path") == "/command":    
            message = self.get_command_panel()
            message_type = "text"
        else:
            message = self.get_last_measure()
            message_type = "json"

        # TODO log all API calls

        # print(f"Received {message!r} from {addr!r}")

        
        writer.write("HTTP/1.1 200 OK\n".encode())
        if message_type == "json" :
            writer.write("Content-Type: application/json\n".encode())
        else:
            writer.write("Content-Type: text/html; charset=utf-8\n".encode())
        writer.write('Connection: close\n\n')

        if message_type == "json" :
            writer.write(ujson.dumps(message))
        else:
            writer.write(message)
        reader.close()
        await asyncio.sleep(1)
        await reader.wait_closed()
        await asyncio.sleep(0.2)
        await writer.drain()
        await asyncio.sleep(0.2)
        writer.close()
        await asyncio.sleep(0.2)
        await writer.wait_closed()

    def parse_request(self, request: str):
        print(request)
        request_lines = iter(request.rstrip().splitlines())

        method, dir_, _ = next(request_lines).split()

        req_dict = {
            'method': method,
            'path': "" if dir_ == "/" else dir_,
        }

        print(req_dict)

        return req_dict

    def get_last_measure(self):
        print("get_last_measure")
        return read_last_data_line_from_log_file(CSV_DATA_FILE)

    def get_all_measures(self):
        print("get_all_measure")
        return read_all_data_from_log_file(CSV_DATA_FILE)

    def get_watering_list(self):
        print("get_watering_list")

    def get_command_panel(self):
        print("get_command_panel")
        # TODO load from template file
        html = """<html><body><h1>Watering system command panel</h1></body></html>"""
        return html

    async def close(self):
        print('Closing server')
        self.server.close()
        await self.server.wait_closed()
        print('Server closed.')

if START_SERVER == True:
    server = Server(network_ip_address)

async def main():
    print("running main")
    while True:
        data = measure_io(moisture_sensor, dht_sensor, water_lever_sensor)
        print(data)
        write_data_to_log_file(CSV_DATA_FILE, data)
        await asyncio.sleep(10 * 60)
        # await asyncio.sleep(30 * 1)

try:
    loop = asyncio.new_event_loop()
    if START_SERVER == True:
        loop.create_task(server.run())
    loop.create_task(main())
    loop.run_forever()

except KeyboardInterrupt:
    print('Interrupted')  # This mechanism doesn't work on Unix build.
finally:
    asyncio.run(server.close())
    _ = asyncio.new_event_loop()
    loop.close()
    loop.stop()