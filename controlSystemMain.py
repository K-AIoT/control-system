import mqttModule
import time
from random import randrange

mqttClient = mqttModule.makeClient("mqttClient")
#mqttPublishTopics = ["actuators/servo"]

while True:

    #inputData = randrange(30.0)

    #for topic in mqttPublishTopics:
        #mqttModule.mqttPublishData(mqttClient, topic, inputData)

    time.sleep(1)
