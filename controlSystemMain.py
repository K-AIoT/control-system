import mqttModule
import time
from random import randrange

mqttClient = mqttModule.makeClient("mqttClient")
mqttPublishTopics = ["actuators/servo", "robot/intListToRos", "resistors/potmeter"]
inputData = [1, 2, 3]
while True:

    #inputData['data'] = not inputData['data']
    for i in range(len(inputData)):
        inputData[i] += 1

    for topic in mqttPublishTopics:
        mqttModule.mqttPublishData(mqttClient, topic, inputData)

    time.sleep(1)
