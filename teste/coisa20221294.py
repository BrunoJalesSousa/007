from counterfit_connection import CounterFitConnection
CounterFitConnection.init('127.0.0.1', 5000)

import time
import counterfit_shims_serial
import pynmea2
import json
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse
from counterfit_shims_grove.grove_led import GroveLed

connection_string = 'HostName=20221294hub.azure-devices.net;DeviceId=device20221294;SharedAccessKey=yEm01fdV4W4LgaAPOrIwksRvwoUaJpoKBRtkVEPerVs='

serial = counterfit_shims_serial.Serial('/dev/ttyAMA0')

device_client = IoTHubDeviceClient.create_from_connection_string(connection_string)


led_verde = GroveLed(2)  
led_vermelho = GroveLed(3)  

print('Connecting')
device_client.connect()
print('Connected')

def send_gps_data(line):
    msg = pynmea2.parse(line)
    if msg.sentence_type == 'GGA':
        lat = pynmea2.dm_to_sd(msg.lat)
        valor_longitude = pynmea2.dm_to_sd(msg.lon)

        if msg.lat_dir == 'S':
            lat = lat * -1

        if msg.lon_dir == 'W':
            valor_longitude = valor_longitude * -1

        
        message_json = {'longitude': valor_longitude}
        print("Sending longitude", message_json)
        message = Message(json.dumps(message_json))
        device_client.send_message(message)

def handle_method_request(request):
    print("Direct method received - ", request.name)
    
    if request.name == "LED_verde_on":
        led_verde.on()
        led_vermelho.off()
    elif request.name == "LED_vermelho_on":
        led_vermelho.on()
        led_verde.off()

    method_response = MethodResponse.create_from_method_request(request, 200)
    device_client.send_method_response(method_response)

device_client.on_method_request_received = handle_method_request

while True:
    line = serial.readline().decode('utf-8')

    while len(line) > 0:
        send_gps_data(line)
        line = serial.readline().decode('utf-8')

    time.sleep(15)

