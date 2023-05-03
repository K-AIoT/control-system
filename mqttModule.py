# mqttModule.py

import paho.mqtt.client as mqtt
import msgpack
import json

# mqttBrokerIp = "192.168.50.74" #local home
mqttBrokerIp = "172.29.76.226" #local eduroam
# mqttBrokerIp = "192.168.1.22" #raspberry pi

mqttClientSubscriptions = ["robot/fromGoal", "robot/toCmd_vel", "robot/intListToMqtt", "robot/boolToMqtt", "sensors/temperature", "sensors/humidity", "sensors/temperature2", "resistors/potmeter", "robot/fromCmd_vel"] #Make empty list here, and add function to add subscriptions that can be called from main file.

# Function that creates an MQTT client, defines its callback functions and connects it to the broker via its IP address.
def makeClient(clientName):
    client = mqtt.Client(client_id=clientName, protocol=mqtt.MQTTv311, transport="tcp")
    client.on_connect = on_connect
    client.on_message = on_message
    # client.message_callback_add("resistors/potmeter", resistorsPotmeterCallback)
    client.message_callback_add("robot/intListToMqtt", rosCallback)
    client.message_callback_add("robot/boolToMqtt", rosCallback)
    client.message_callback_add("robot/fromGoal", rosCallback)
    client.on_disconnect = on_disconnect
    client.connect(mqttBrokerIp)
    client.loop_start()                                                                                         
    return client   

# Message callback function, to handle any messages on subscribed topics that don't have a specific callback function.
def on_message(client, userdata, message):
    pass
    #print("Received ROS Message: ", str(msgpack.unpackb(message.payload, raw=False)))
    # print("Unrecognised Message Type Received: ", print(message.payload))

# Callback function that executes when client receives CONNACK from broker in response to connect request.
def on_connect(client, userdata, flags, rc):
    for topic in mqttClientSubscriptions:
        client.subscribe(topic, 1)  

# Callback function that executes when client sends disconnect request to broker.
def on_disconnect(client, userdata, rc):
    print("Disconnected: ", str(rc))
    client.loop_stop()

# # Message callback function, specifically to handle any messages on topics that match "sensors/potemeter" (Including with wildcard use).
# def resistorsPotmeterCallback(client, userdata, message):
#     data = json.loads(message.payload.decode("utf8"))
#     print("Received Potmeter Message: ", str(data))   
#     client.publish("actuators/servo", message.payload)  #Publishes messages received directly to actuators/servo topic

# Message callback function, specifically to handle any messages on topics related to ROS.
def rosCallback(client, userdata, message):
    print("Received ROS Message: ", str(msgpack.unpackb(message.payload, raw=False)))   # Decodes MessagePack-encoded string into Python dictionary. 
                                                                                        # raw=False indicates decode string values as Unicode strings not binary 
                                                                                        # strings.
# Publishes data to MQTT topics and distinguishes between normal topics and those for communication with the robot. 
def mqttPublishData(client, topic, data):
        if type(data) is not dict:
            data = {'data': data} # Converts to dictionary.
            
        if topic.startswith("robot/"):  # Checks first if the topic will be used to communicate with the robot and then if its format is compatible with the ROS topic, 
                                        # i.e. if it's a dictionary.
            encodedData = msgpack.packb(data)   # Encodes the data.
            client.publish(topic, payload=encodedData, qos=1, retain=False) 
        else:
            client.publish(topic, payload=json.dumps(data), qos=1, retain=False) # Will cause error if data isn't a string, bytearray, int, float or None. So fixed by 
                                                                                 # encoding payload using JSON. 


        