# devices.py

import asyncio
import bridge
from asyncua import Node, ua
from typing import List, Optional, Tuple, Type, ForwardRef
from uuid import UUID
import msgpack
import re

# Class that acts as an OPC UA callback handler, managing any OPC UA events and :
class OpcuaCallback:

    def __init__(self, device : ForwardRef('Device')):
        self._device = device # Keeps reference to its associated Device.

    def getDevice(self):
        return self._device
    
    async def datachange_notification(self, node: Node, val, data: ua.DataChangeNotification):
        nodeName = await node.read_browse_name() 
        print(f"OPC UA CHANGE ON NODE: {nodeName.Name}: {val}")
        for mqttTopic in self._device.getPubSubPairs()[node]: # Iterates through the MQTT topics stored in the device's set of publisher/subscriber pairs associated with the OPC UA node.
            self._device.getBridge().getMqttClient().publish(mqttTopic, payload=val, qos=1, retain=False) # Publishes the new value in the OPC UA server to each of the MQTT topics.
        
    async def event_notification(self, event: ua.EventNotificationList):
        print(f"Event: {event}")

class Device:
    
    def __init__(self, bridge: Optional[bridge.MqttOpcuaBridge] = None, pubSubPairs: Optional[List[Tuple[str, str]]] = None, opcuaCallback: Optional[Optional[Type[OpcuaCallback]]] = None):
        self._bridge = bridge
        self._pubSubPairs = pubSubPairs

        if opcuaCallback is None: # If there is no callback passed to the device upon initialisation create one and assign it to the device. Otherwise assign the one passed in initialisation.
            self._opcuaCallback = OpcuaCallback(self)
        else:
            self._opcuaCallback = opcuaCallback 

        self._loop = asyncio.get_event_loop() # Attains the current event loop
        self._loop.create_task(self.asyncInit())  # Creates a task within the event loop that runs 
    
    # Make __del__(self):
        #unsubscribes OPC UA node

    async def asyncInit(self): #POSSIBLY DELETE AND CALL SETPUBSUBPAIRS IN LOOP.CREATE_TASK IN INIT
        await self.setPubSubPairs(self._pubSubPairs)     

    # Setter Functions:
    async def setPubSubPairs(self, newPubSubPairs: Optional[List[Tuple[str, str]]] = None):       
        tempDict = {}
        formattedTempDict = {}
        if newPubSubPairs is not None:
            for pub, sub in newPubSubPairs:    
                if "/" in pub: # If the MQTT topic is the publisher, subscribe to MQTT topic and add a callback function for it
                    self._bridge.getMqttClient().message_callback_add(pub, self.mqttCallback)
                    self._bridge.getMqttClient().subscribe(pub)
                    # Convert the OPC UA UUID string to a node ID
                    nodeId = ua.NodeId(UUID(sub), 2, ua.NodeIdType.Guid)
                    node = self._bridge.getOpcuaClient().get_node(nodeId)
                    nodeName = (await node.read_browse_name()).Name                  
                    variantType = await node.read_data_type_as_variant_type()
                    nodeDict = {"node": node, "name": nodeName, "variantType": variantType}
                    if pub in tempDict: # Check if the MQTT topic is already listed in the temporary pubSub dictionary and if so, if the subscribing node is already associated with it. If it isn't, add it to the list of subscribing nodes for that MQTT topic. 
                        if node not in tempDict[pub]: #DOUBLE CHECK it actually finds as maybe should look for nodeDict
                            tempDict[pub].append(nodeDict)
                    else:   # If the MQTT topic isn't in the temporary dictionary, add it and the subscribing node as its first list entry.
                        tempDict[pub] = [nodeDict]

                elif "/" in sub: # If the MQTT topic is the subscriber 
                    nodeId = ua.NodeId(UUID(pub), 2, ua.NodeIdType.Guid) # Convert the OPC UA UUID string to a node ID
                    node = self._bridge.getOpcuaClient().get_node(nodeId) # Get the node for that nodeId
                    subscription = await self._bridge.getOpcuaClient().create_subscription(period=0, handler=self._opcuaCallback, publishing=True) # Create a subscription and assign the device's OPC UA handler to manage it.
                    
                    await subscription.subscribe_data_change(node) # Use the subscription to subscribe to any change in data value for the node.
                    if node in tempDict: # If the OPC UA node is already listed in the temporary dictionary, and the MQTT topic subscriber isn't already associated with it, append the MQTT topic to the node's list of subscribers.
                        if sub not in tempDict[node]:
                            tempDict[node].append(sub)
                    else:   # Otherwise create a new dictionary entry for the OPC UA node publisher and MQTT topic subscriber.
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

    # Typecasts the message payload appropriately based on the data type of the OPC UA node receiving it.
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
                return None

    # MQTT Callback Function:
    def mqttCallback(self, client, userdata, message):
        try:
            print(f'Received Message: {str(message.payload.decode("utf-8"))} on topic {message.topic}')               
            opcuaNodes = self._pubSubPairs[message.topic] # Get the set of subscribing nodes associated with the MQTT topic that received a message.
            
            for node in opcuaNodes:

                print(f'Publishing message to node: {node["name"]}')   
    
                payloadValue = self.typecastForNode(node, message.payload) 
                
                if payloadValue is not None:
                    variantFormattedPayload = ua.DataValue(ua.Variant(payloadValue, node["variantType"]))
                    self._loop.create_task(node["node"].write_value(variantFormattedPayload)) # Create a task in the current event loop that writes the correctly formatted message to each associated subscribing OPC UA node iterated through.

        except ValueError:
            print("Error: Could not convert payload to appropriate type")
            return
       
class Robot(Device): # A child class of the Device class, specifically for representing a device operating with ROS.

    def __init__(self, bridge: Optional[bridge.MqttOpcuaBridge] = None, pubSubPairs: Optional[List[Tuple[str, str]]] = None):
        super().__init__(bridge, pubSubPairs, RosOpcuaCallback(self))

    def mqttCallback(self, client, userdata, message):
        try:    
            opcuaNodes = self._pubSubPairs[message.topic] 
            rosMsgDict = msgpack.unpackb(message.payload, raw=False) 

            print(f'Received ROS message on topic {message.topic}:')  
            for node in opcuaNodes:

                keyPath = [x.lower() for x in re.split(r'(?=[A-Z])', "status_listStatus")] # Takes the OPC UA node name and splits it into a list of parts, each representing a subdictionary within the corresponding ROS message. Makes it possible to differentiate between two keys of the same name but within different parts of a message. Separator is a uppercase letter since ROS messages use '-' within names and NxTTech will not accept any other special characters in node names.
                                    
                for searchTerm in keyPath: # Finds the value key pair in the ROS message dictionary received.
                    rosMsgDict = self.getRosDictionaryValue(rosMsgDict, searchTerm)
                    key, hit = searchTerm, rosMsgDict

                print(f'Message: {key} = {hit}\nPublishing to node: {node["name"]}')

                payloadValue = super().typecastForNode(node, hit)                
                variantFormattedPayload = ua.DataValue(ua.Variant(payloadValue, node["variantType"]))
                #DOUBLE CHECK BELOW, should self._loop work?
                self._loop.create_task(node["node"].write_value(variantFormattedPayload)) # Create a task in the current event loop that writes the correctly formatted message to each associated subscribing OPC UA node iterated through.
        
        except ValueError:
            print("Error: Could not convert payload to appropriate type")
            return

    def getRosDictionaryValue(self, msgToSearch, searchKey: str):
                
        if (isinstance(msgToSearch, list) and all(isinstance(item, dict) for item in msgToSearch)): # Checks if the message being searched is a list of dictionaries.
            for dictionary in msgToSearch:
                for key, entry in dictionary.items():          
                    if(key == searchKey):
                        return entry
                    if isinstance(entry, dict) or (isinstance(entry, list) and all(isinstance(item, dict) for item in entry)): # Checks if the entry being iterated through is a dictionary or a list of dictionaries.
                        self.getRosDictionaryValue(entry, searchKey) # Recursively calls itself to search through the entry list/dictionary.
        
        elif isinstance(msgToSearch, dict):
            for key, entry in msgToSearch.items():         
                if(key == searchKey):
                    return entry
                if isinstance(entry, dict) or (isinstance(entry, list) and all(isinstance(item, dict) for item in entry)): # Checks if the entry being iterated through is a dictionary or a list of dictionaries.
                    self.getRosDictionaryValue(entry, searchKey) # Recursively calls itself to search through the entry list/dictionary.

class RosOpcuaCallback(OpcuaCallback):

    def __init__(self, robot : Robot):
        super().__init__(robot)

    async def datachange_notification(self, node: Node, val, data: ua.DataChangeNotification): # Callback function that handles changes in data for the given OPC UA node.
        try:    
            nodeName = await node.read_browse_name()
            print(f"OPC UA CHANGE ON NODE: {nodeName.Name}: {val}")
            for mqttTopic in self._device.getPubSubPairs()[node]: # For each of the MQTT topics associated with the OPC UA node whose value changed, publish a pre-determined ROS message for a sensor location based on the value received.
                match val:
                    case 0:
                        messagePayload = {'header': {'seq': 0, 'stamp': {'secs': 1683119373, 'nsecs': 994051246}, 'frame_id': 'map'}, 'pose': {'position': {'x': -1.399324893951416, 'y': 0.36991798877716064, 'z': 0.0}, 'orientation': {'x': 0.0, 'y': 0.0, 'z': 0.9893189277112782, 'w': 0.1457671405777269}}}
                    case 1:
                        messagePayload = {'header': {'seq': 0, 'stamp': {'secs': 0, 'nsecs': 0}, 'frame_id': 'map'}, 'pose': {'position': {'x': 1.0, 'y': 0.0, 'z': 0.0}, 'orientation': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 0.0}}}
                    case 2:
                        messagePayload = {'header': {'seq': 0, 'stamp': {'secs': 0, 'nsecs': 0}, 'frame_id': 'map'}, 'pose': {'position': {'x': 1.0, 'y': 1.0, 'z': 0.0}, 'orientation': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 0.0}}}
                    case 3:
                        messagePayload = {'header': {'seq': 0, 'stamp': {'secs': 1683119373, 'nsecs': 994051246}, 'frame_id': 'map'}, 'pose': {'position': {'x': -1.2823765779, 'y': -0.891584396362, 'z': 0.00218486785889}, 'orientation': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0}}}
                print(f'Publishing message: {messagePayload} to MQTT topic {mqttTopic}')
                
                super().getDevice().getBridge().getMqttClient().publish(mqttTopic, payload = msgpack.packb(messagePayload), qos=1, retain=False)#

        except UnboundLocalError:
            print("Received value isn't associated with a location.")
            return