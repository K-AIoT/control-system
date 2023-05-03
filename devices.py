# devices.py
import paho.mqtt.client as mqtt
import asyncio
from asyncua import Client, Node, ua
from typing import List, Optional
from uuid import UUID


class MqttOpcuaBridge:
    def __init__(self, opcuaClient: Client, mqttClient: mqtt.Client):
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


class Node:
    def __init__(self, uuidStrings: List[str], bridge: MqttOpcuaBridge):
        self._bridge = bridge
        self._uuidStrings = uuidStrings
        self._opcuaNodeIds = asyncio.create_task(self.setOpcuaNodeIds())

    async def setOpcuaNodeIds(self):
        nodeDict = {}
        for uuid in self._uuidStrings:
            nodeId = ua.NodeId(UUID(uuid), 2, ua.NodeIdType.Guid)
            node = self._bridge.getOpcuaClient().get_node(nodeId)
            browseName = await node.read_browse_name()
            nodeDict[browseName.to_string()] = nodeId
        return nodeDict

    def getOpcuaNodeIds(self):
        return self._opcuaNodeIds

# class Sensor(Node):

# # Class Attributes/Methods:
#     def __init__(self, opcuaClient, nodeIds, mqttClient, subscriptions): # Contains instance Attributes/Methods:
#         super().__init__(opcuaClient, nodeIds, mqttClient)
#         self._reading = None
#         self._mqttSubscriptions = subscriptions
#         self.subscribeAll()

#     def subscribeAll(self):
#         for topic in self._mqttSubscriptions:
#             self._mqttClient.message_callback_add(topic, self.sensorCallback)

#         for topic in self._mqttSubscriptions:
#             self._mqttClient.subscribe(topic)

#     # Setter Functions:
#     async def setReading(self, newReading):
#         self._reading = newReading

#     async def setMqttSubscriptions(self, subscriptions):
#         self._mqttSubscriptions = subscriptions

#     # Getter Functions:
#     async def getReading(self):
#         return self._reading

#     async def getMqttSubscriptions(self):
#         return self._mqttSubscriptions

#     # Callback Function:
#     def sensorCallback(self, client, userdata, message):
#         print("Received Sensor Message: ", str(message.payload.decode("utf-8")))
#         asyncio.run(self.setReading(message.payload.decode("utf-8")))
#         asyncio.run(self._opcuaClient.write_values(self._opcuaNodes[0], message.payload.decode("utf-8")))

#     # async def updateAttributeVal(self, subscriptions):
#     #     attributeVal = await asyncio.wait_for(toMonitor, None) # Wait for variable_name to change with no timeout (None)
#     #     node.write_value(attributeVal)