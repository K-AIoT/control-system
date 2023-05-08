# devices.py
# from asyncua.common.node import Node
import paho.mqtt.client as mqtt
import mqttModule
import asyncio
from asyncua import Client, Node, ua
from typing import List, Optional, Dict, Tuple
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
    
    def __init__(self, bridge: Optional[MqttOpcuaBridge] = None, pubSubPairs: Optional[List[Tuple[str, str]]] = None):
        self._bridge = bridge
        self._pubSubPairs = pubSubPairs

        self._loop = asyncio.get_event_loop()
        self._loop.create_task(self.asyncInit())
    
    async def asyncInit(self):
        await self.setPubSubPairs(self._pubSubPairs)     

    # Setter Functions:
    async def setPubSubPairs(self, newPubSubPairs: Optional[List[Tuple[str, str]]] = None):       
        tempDict = {}
        formattedTempDict = {}
        if newPubSubPairs != None:
            for pub, sub in newPubSubPairs:    
                if "/" in pub: # If the MQTT topic is the publisher subscribe to MQTT topic and add a callback function for it
                    self._bridge.getMqttClient().message_callback_add(pub, self.mqttCallback)
                    self._bridge.getMqttClient().subscribe(pub)
                    # Convert the OPC UA UUID string to a node ID
                    nodeId = ua.NodeId(UUID(sub), 2, ua.NodeIdType.Guid)
                    node = self._bridge.getOpcuaClient().get_node(nodeId)
                    nodeName = (await node.read_browse_name()).Name                  
                    variantType = await node.read_data_type_as_variant_type()
                    nodeDict = {"node": node, "name": nodeName, "variantType": variantType}
                    if pub in tempDict:
                        if node not in tempDict[pub]:
                            tempDict[pub].append(nodeDict)
                    else:
                        tempDict[pub] = [nodeDict]

                elif "/" in sub: # If the MQTT topic is the subscriber convert the OPC UA UUID string to a node ID
                    nodeId = ua.NodeId(UUID(pub), 2, ua.NodeIdType.Guid)
                    node = self._bridge.getOpcuaClient().get_node(nodeId)
                    subscription = await self._bridge.getOpcuaClient().create_subscription(period=0, handler=opcuaCallback(self), publishing=True)
                    await subscription.subscribe_data_change(node)
                    if node in tempDict:
                        if sub not in tempDict[node]:
                            tempDict[node].append(sub)
                    else:
                        tempDict[node] = [sub] 
    
        #Convert all list keys and values to tuples
        for key, value in tempDict.items():
            if isinstance(key, list):
                key = tuple(key)
            elif isinstance(value, list):
                value = tuple(value)

            formattedTempDict[key] = value

        self._pubSubPairs = formattedTempDict

    def setBridge(self, newBridge):
        self._bridge = newBridge

    # Getter Functions:
    def getPubSubPairs(self):
        return self._pubSubPairs

    def getBridge(self):
        return self._bridge

    # MQTT Callback Function:

    def mqttCallback(self, client, userdata, message):
        try:
            print(f'Received Message: {str(message.payload.decode("utf-8"))} on topic {message.topic}')               
            opcuaNodes = self._pubSubPairs[message.topic]
            
            for node in opcuaNodes:

                print(f'Publishing message to OPC UA node: {node["name"]}')   
                
                match node["variantType"].name:
                    case "Float":
                        payloadValue = float(message.payload) 
                    case "String":
                        payloadValue = str(message.payload)
                    case "Boolean":
                        payloadValue = bool(message.payload)
                    case _:
                        print("Node is of an unknown data type so cannot be handled.")
                        return 
                    
                variantFormattedPayload = ua.DataValue(ua.Variant(payloadValue, node["variantType"]))
                self._loop.create_task(node["node"].write_value(variantFormattedPayload))
        except ValueError:
            print("Error: Could not convert payload to appropriate type")
            return
            
# OPC UA Callback Handler:
    
class opcuaCallback:

    def __init__(self, device : Device):
        self._device = device

    async def datachange_notification(self, node: Node, val, data: ua.DataChangeNotification):
        nodeName = await node.read_browse_name()
        print(f"New value from OPC UA server on node {nodeName.Name}: {val}")
        for mqttTopic in self._device.getPubSubPairs()[node]:
            mqttModule.mqttPublishData(self._device.getBridge().getMqttClient(), mqttTopic, val)
        
    async def event_notification(self, event: ua.EventNotificationList):
        print(f"Event: {event}")
       
        