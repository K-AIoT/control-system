import paho.mqtt.client as mqtt
import time

mqttBrokerIp = "172.29.69.158"
mqttClientSubscriptions = ["sensors/temperature","sensors/humidity", "sensors/temperature2"]

#Function that creates an MQTT client, defines its callback functions and connects it to the broker via its IP address.
def makeClient(clientName):
    client = mqtt.Client(clientName)
    client.on_connect = on_connect
    client.on_message = on_message
    client.message_callback_add("sensors/temperature", tempSensorCallback)
    client.on_disconnect = on_disconnect
    client.connect(mqttBrokerIp)
    client.loop_start()                                                                                         
    return client   

#Message callback function, to handle any messages on subscribed topics that don't have a specific callback function.
def on_message(client, userdata, message):
    print("Received message: ", str(message.payload.decode("utf-8")))

#Callback function that executes when client receives CONNACK from broker in response to connect request.
def on_connect(client, userdata, flags, rc):
    for topic in mqttClientSubscriptions:
        client.subscribe(topic, 1)

#Callback function that executes when client sends disconnect request to broker.
def on_disconnect(client, userdata, rc):
    print("Disconnected: ", str(rc))
    client.loop_stop()

#Message callback function, specifically to handle any messages on topics that match "sensors/temperature" (Including with wildcard use).
def tempSensorCallback(client, userdata, message):
    print("Received Temp Message: ", str(message.payload.decode("utf-8")))

mqttClient = makeClient("mqttClient")

while True:

    time.sleep(1)


        