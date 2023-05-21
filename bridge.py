# bridge.py

import paho.mqtt.client as mqtt
from asyncua import Client
from typing import Optional

# Class that acts as a bridge for an OPC UA and MQTT client pair. 
class MqttOpcuaBridge: 
    def __init__(self, opcuaClient: Optional[Client] = None, mqttClient: Optional[mqtt.Client] = None):
        self._mqttClient = mqttClient
        self._opcuaClient = opcuaClient

    # Getter Functions:
    def getOpcuaClient(self):
        return self._opcuaClient

    def getMqttClient(self):
        return self._mqttClient
    
    # Setter Functions:
    def setOpcuaClient(self, newClient):
        self._opcuaClient = newClient

    def setMqttClient(self, newClient):
        self._mqttClient = newClient