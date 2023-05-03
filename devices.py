# devices.py
import paho.mqtt.client as mqtt
import asyncio
from asyncua import Client, Node, ua
from typing import List, Optional, Dict, Callable
from uuid import UUID


class MqttOpcuaBridge:
    def __init__(self, opcuaClient: Optional[Client] = None, mqttClient: Optional[mqtt.Client] = None):
        self._mqttClient = mqttClient
        self._opcuaClient = opcuaClient

    def getOpcuaClient(self):
        return self._opcuaClient

    def getMqttClient(self):
        return self._mqttClient

    def setOpcuaClient(self, newClient):
        self._opcuaClient = newClient

    def setMqttClient(self, newClient):
        self._mqttClient = newClient


class Device:
    @staticmethod
    def createCallback(callbackName : str):
        def callbackName(client, userdata, message):
            print(f'Received Message: {str(message.payload.decode("utf-8"))} on topic {message.topic}')               

        return callbackName

    # def __init__(self, uuidStrings: Optional[List[str]] = None, bridge: Optional[MqttOpcuaBridge] = None, mqttSubs: Optional[List[str]] = None):
    def __init__(self, bridge: Optional[MqttOpcuaBridge] = None, pubSubPairs: Optional[Dict[str, str]] = None):
        self._bridge = bridge
        self._pubSubPairs = pubSubPairs
        #self._callback = Device.createCallback()
        self.setPubSubPairs(self._pubSubPairs)
        
        # self._opcuaNodeIds = asyncio.create_task(self.setOpcuaNodeIds())

    # Setter Functions:
    def setPubSubPairs(self, newPubSubPairs: Optional[Dict[str, str]] = None):       
        tempDict = {}
        if newPubSubPairs != None:
        # for pub, sub in self._pubSubPairs.items():
            for pub, sub in newPubSubPairs.items():    
                if "/" in pub: # If the MQTT topic is the publisher
                    # Subscribe to MQTT topic and add a callback function for it
                    callback = Device.createCallback(pub + "Callback")
                    self._bridge.getMqttClient().message_callback_add(pub, callback)
                    self._bridge.getMqttClient().subscribe(pub)
                    # Convert the OPC UA UUID string to a node ID
                    nodeId = ua.NodeId(UUID(sub), 2, ua.NodeIdType.Guid)
                    node = self._bridge.getOpcuaClient().get_node(nodeId)
                    nodeTuple = (nodeId, node)
                    tempDict[nodeTuple] = pub # Place nodeId string with new nodeId/node tuple in temporary dictionary which will replace _pubSubPairs dictionary. Keep MQTT topic the same.
                elif "/" in sub: # If the MQTT topic is the subscriber
                    # Convert the OPC UA UUID string to a node ID
                    nodeId = ua.NodeId(UUID(pub), 2, ua.NodeIdType.Guid)
                    node = self._bridge.getOpcuaClient().get_node(nodeId)
                    nodeTuple = (nodeId, node)
                    tempDict[sub] = nodeTuple # Place nodeId string with new nodeId/node tuple in temporary dictionary which will replace _pubSubPairs dictionary. Keep MQTT topic the same.
        self._pubSubPairs = tempDict

    def setBridge(self, newBridge):
        self._bridge = newBridge

    # Getter Functions:
    def getPubSubPairs(self):
        return self._pubSubPairs

    def getBridge(self):
        return self._bridge

    # # Callback Function:
    # def deviceCallback(self, client, userdata, message):
    #     print(f'Received Message: {str(message.payload.decode("utf-8"))} on topic {message.topic}')
        
        # asyncio.run(self.setReading(message.payload.decode("utf-8")))
        # match message.topic:
        #     case self._pubSubPairs:

        # asyncio.run(self._bridge.getOpcuaClient().write_values(self._opcuaNodes[0], message.payload.decode("utf-8")))


    # async def updateAttributeVal(self, subscriptions):
    #     attributeVal = await asyncio.wait_for(toMonitor, None) # Wait for variable_name to change with no timeout (None)
    #     node.write_value(attributeVal)