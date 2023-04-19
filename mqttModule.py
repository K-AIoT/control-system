import paho.mqtt.client as mqtt

mqttBrokerIp = "172.29.69.158"

mqttClientSubscriptions = ["ping", "sensors/temperature", "sensors/humidity", "sensors/temperature2", "resistors/potmeter"] #Make empty list here, and add function to add subscriptions that can be called from main file.

#Function that creates an MQTT client, defines its callback functions and connects it to the broker via its IP address.
def makeClient(clientName):
    client = mqtt.Client(client_id=clientName, protocol=mqtt.MQTTv311, transport="tcp")
    client.on_connect = on_connect
    client.on_message = on_message
    client.message_callback_add("sensors/temperature", sensorsTemperatureCallback)
    client.message_callback_add("sensors/temperature2", sensorsTemperature2Callback)
    client.message_callback_add("sensors/humidity", sensorsHumidityCallback)
    client.message_callback_add("resistors/potmeter", resistorsPotmeterCallback)
    client.on_disconnect = on_disconnect
    client.connect(mqttBrokerIp)
    client.loop_start()                                                                                         
    return client   

#Message callback function, to handle any messages on subscribed topics that don't have a specific callback function.
def on_message(client, userdata, message):
    print("Received Message: ", str(message.payload.decode("utf-8")))

#Callback function that executes when client receives CONNACK from broker in response to connect request.
def on_connect(client, userdata, flags, rc):
    for topic in mqttClientSubscriptions:
        client.subscribe(topic, 1)  

#Callback function that executes when client sends disconnect request to broker.
def on_disconnect(client, userdata, rc):
    print("Disconnected: ", str(rc))
    client.loop_stop()

#Message callback function, specifically to handle any messages on topics that match "sensors/temperature" (Including with wildcard use).
def sensorsTemperatureCallback(client, userdata, message):
    print("Received Temp Message: ", str(message.payload.decode("utf-8")))
    #client.publish("actuators/servo", message.payload)  #Publishes messages received directly to actuators/servo topic

#Message callback function, specifically to handle any messages on topics that match "sensors/temperature2" (Including with wildcard use).
def sensorsTemperature2Callback(client, userdata, message):
    print("Received Temp2 Message: ", str(message.payload.decode("utf-8"))) 

#Message callback function, specifically to handle any messages on topics that match "sensors/humidity" (Including with wildcard use).
def sensorsHumidityCallback(client, userdata, message):
    print("Received Humidity Message: ", str(message.payload.decode("utf-8")))  

#Message callback function, specifically to handle any messages on topics that match "sensors/potemeter" (Including with wildcard use).
def resistorsPotmeterCallback(client, userdata, message):
    print("Received Potmeter Message: ", str(message.payload.decode("utf-8")))  
    client.publish("actuators/servo", message.payload)  #Publishes messages received directly to actuators/servo topic

def mqttPublishData(client, topic, data):
    client.publish(topic, payload=data, qos=1, retain=False)