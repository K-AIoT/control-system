# main.py
import asyncio
import devices
import mqttModule
from asyncua import Client, Node, ua

mqttClient = mqttModule.makeClient("mqttClient")

opcuaServerUrl = "opc.tcp://10.64.233.49:4840"
namespaceUri = "http://se.com/EcostruxureSystemExpert"

async def main():
    print(f"Connecting to {opcuaServerUrl} ...")

    async with Client(url=opcuaServerUrl) as client:

        myBridge = devices.MqttOpcuaBridge(client, mqttClient)
        myNode = devices.Device(myBridge, {"3dbdca09-4b5c-b9ac-efd0-3184cdcceec3" : "sensors/humidity", "sensors/temperature" : "7347f3a9-455f-a8e5-f0b6-c8d2520eec5f", "sensors/temperature2" : "d1581787-f061-a231-fc00-569b624f14b6"})
        
        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())

# # main.py

# import asyncio
# import devices
# import mqttModule
# from asyncua import Client, Node, ua

# mqttClient = mqttModule.makeClient("mqttClient")

# opcuaServerUrl = "opc.tcp://10.64.233.49:4840"
# namespaceUri = "http://se.com/EcostruxureSystemExpert"

# async def main():
#     print(f"Connecting to {opcuaServerUrl} ...")

#     async with Client(url=opcuaServerUrl) as client:

#         myBridge = devices.MqttOpcuaBridge(client, mqttClient)

#         myNode = devices.Node(["3dbdca09-4b5c-b9ac-efd0-3184cdcceec3","7347f3a9-455f-a8e5-f0b6-c8d2520eec5f"], myBridge)

#         await asyncio.gather(myNode.setOpcuaNodeIds())

#         nodeIds = await myNode.getOpcuaNodeIds()

#         print(nodeIds)
        

# if __name__ == "__main__":
#     asyncio.run(main())
    

# async def main():
#     print(f"Connecting to {opcuaServerUrl} ...")

#     async with Client(url=opcuaServerUrl) as client:

#         nsidx = await client.get_namespace_index(namespaceUri)

#         temperatureNode = client.get_node("ns=2;g={3dbdca09-4b5c-b9ac-efd0-3184cdcceec3}") #alternative way to get the same node as temperatureNode
        
#         name = await temperatureNode.read_browse_name()

#         print(name.to_string())
    
#         #Alternative way to get node
#         uuid_str = '3dbdca09-4b5c-b9ac-efd0-3184cdcceec3'
#         uuid = UUID(uuid_str)
#         node_id = ua.NodeId(uuid, 2, ua.NodeIdType.Guid)

#         newNode = client.get_node(node_id)

#         newName = await newNode.read_browse_name()

#         print(newName)
        
