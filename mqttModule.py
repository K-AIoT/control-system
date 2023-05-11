# mqttModule.py

import paho.mqtt.client as mqtt

# Function that creates an MQTT client, defines its callback functions and connects it to the broker via its IP address.
def makeClient(clientName, mqttBrokerIp):
    client = mqtt.Client(client_id=clientName, protocol=mqtt.MQTTv311, transport="tcp")
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.connect(mqttBrokerIp)
    client.loop_start()                                                                                         
    return client   

# Message callback function, to handle any messages on subscribed topics that don't have a specific callback function.
def on_message(client, userdata, message):
    print(f'Received MQTT message on topic {message.topic} with no associated destination.')

# Callback function that executes when client sends disconnect request to broker.
def on_disconnect(client, userdata, rc):
    print("Disconnected: ", str(rc))
    client.loop_stop()
                                                                               


        