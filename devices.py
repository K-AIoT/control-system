# devices.py

import paho.mqtt.client as mqtt
import mqttModule
import asyncio
from asyncua import Client, Node, ua
from typing import List, Optional, Dict, Tuple, Any
from uuid import UUID
import msgpack
import re


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
    
    # Make __del__(self):
        #unsubscribes OPC UA node

    async def asyncInit(self): #POSSIBLY DELETE AND CALL SETPUBSUBPAIRS IN LOOP.CREATE_TASK IN INIT
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
                    subscription = await self._bridge.getOpcuaClient().create_subscription(period=0, handler=OpcuaCallback(self), publishing=True)
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


    def typecastForNode(self, node, payload):
        match node["variantType"].name:
            case "Float":
                return float(payload) 
            case "String":
                return str(payload)
            case "Boolean":
                return bool(payload)
            case _:
                print("Node is of an unknown data type so cannot be handled.")
                return 

    # MQTT Callback Function:

    def mqttCallback(self, client, userdata, message):
        try:
            print(f'Received Message: {str(message.payload.decode("utf-8"))} on topic {message.topic}')               
            opcuaNodes = self._pubSubPairs[message.topic]
            
            for node in opcuaNodes:

                print(f'Publishing message to OPC UA node: {node["name"]}')   
    
                payloadValue = self.typecastForNode(node, message.payload)
                variantFormattedPayload = ua.DataValue(ua.Variant(payloadValue, node["variantType"]))
                
                self._loop.create_task(node["node"].write_value(variantFormattedPayload))
       
        except ValueError:
            print("Error: Could not convert payload to appropriate type")
            return
            
# OPC UA Callback Handler:
    
class OpcuaCallback:

    def __init__(self, device : Device):
        self._device = device

    async def datachange_notification(self, node: Node, val, data: ua.DataChangeNotification):
        nodeName = await node.read_browse_name()
        print(f"New value from OPC UA server on node {nodeName.Name}: {val}")
        for mqttTopic in self._device.getPubSubPairs()[node]:
            mqttModule.mqttPublishData(self._device.getBridge().getMqttClient(), mqttTopic, val)
        
    async def event_notification(self, event: ua.EventNotificationList):
        print(f"Event: {event}")
       
class Robot(Device):

    def __init__(self, bridge: Optional[MqttOpcuaBridge] = None, pubSubPairs: Optional[List[Tuple[str, str]]] = None):
        super().__init__(bridge, pubSubPairs)

    def mqttCallback(self, client, userdata, message):
        try:    
            opcuaNodes = self._pubSubPairs[message.topic] #tuple
            rosMsgDict = msgpack.unpackb(message.payload, raw=False) #dict

            # print(f'Received Message: {str(rosMsgDict)} on topic {message.topic}')
            print(f'Received ROS message on topic {message.topic}:')  
            for node in opcuaNodes:

                # keyPath = [x.lower() for x in re.split(r'(?=[A-Z])', node["name"])]
                keyPath = [x.lower() for x in re.split(r'(?=[A-Z])', "status_listStatus")]
                                       
                for searchTerm in keyPath: 
                    rosMsgDict = self.getRosDictionaryValue(rosMsgDict, searchTerm)
                    key, hit = searchTerm, rosMsgDict
  
                print(f'Message: {key} = {hit}\nPublishing to OPC UA node: {node["name"]}')

                payloadValue = super().typecastForNode(node, hit)                
                variantFormattedPayload = ua.DataValue(ua.Variant(payloadValue, node["variantType"]))
                self._loop.create_task(node["node"].write_value(variantFormattedPayload))

        except ValueError:
            print("Error: Could not convert payload to appropriate type")
            return

    def getRosDictionaryValue(self, msgToSearch, searchKey: str):
                
        if (isinstance(msgToSearch, list) and all(isinstance(item, dict) for item in msgToSearch)):
            for dictionary in msgToSearch:
                for key, entry in dictionary.items():          
                    if(key == searchKey):
                        return entry
                    if isinstance(entry, dict) or (isinstance(entry, list) and all(isinstance(item, dict) for item in entry)):
                        self.getRosDictionaryValue(entry, searchKey)
        
        elif isinstance(msgToSearch, dict):
            for key, entry in msgToSearch.items():         
                if(key == searchKey):
                    return entry
                if isinstance(entry, dict) or (isinstance(entry, list) and all(isinstance(item, dict) for item in entry)):
                    self.getRosDictionaryValue(entry, searchKey)

# goalStatusArray = {
#     'header': {
#         'seq': 0,
#         'stamp': {
#             'secs': 0,
#             'nsecs': 0
#         },
#         'frame_id': ''
#     },
#     'status_list': [
#         { 'goal_id': { 'id': '', 'stamp': { 'secs': 0, 'nsecs': 0 } }, 
#           'status': 0, 
#           'text': '' }
#     ]
# }

# poseStamped = {
#     'header': {
#         'seq': 0,
#         'stamp': {
#         'secs': 0,
#         'nsecs': 0
#         },
#         'frame_id': ''
#     },
#     'pose': {
#         'position': {
#         'x': 0.0,
#         'y': 0.0,
#         'z': 0.0
#         },
#         'orientation': {
#         'x': 0.0,
#         'y': 0.0,
#         'z': 0.0,
#         'w': 0.0
#         }
#     }
#     }










