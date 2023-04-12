import mqttModule
import time

mqttClient = mqttModule.makeClient("mqttClient")

while True:

    time.sleep(1)
