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
        dht22Sensor = devices.Device(bridge = myBridge, pubSubPairs = [ 
            ("sensors/temperature", "3dbdca09-4b5c-b9ac-efd0-3184cdcceec3"),
            ("7347f3a9-455f-a8e5-f0b6-c8d2520eec5f", "sensors/temperatureThreshold"),
            ("sensors/humidity", "46d6d34e-622b-777a-744e-082d78f6e4c4"),
            ("18b95a2b-2c42-2c19-e488-56e7bcd0f2d2", "sensors/humidityThreshold") 
        ])

        robot = devices.Robot(bridge = myBridge, pubSubPairs = [ 
            ("robot/goalStatusArrayToMqtt", "6fe4cadf-dfcf-7dbc-3a8b-3075c4098e8b")
            # ("robot/twistToMqtt", "6fe4cadf-dfcf-7dbc-3a8b-3075c4098e8b")
        ])

        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())





# Two ways to get a node:
# Method 1:
#         nsidx = await client.get_namespace_index(namespaceUri)
#         temperatureNode = client.get_node("ns=2;g={3dbdca09-4b5c-b9ac-efd0-3184cdcceec3}") 
# Method 2:  
#         uuid_str = '3dbdca09-4b5c-b9ac-efd0-3184cdcceec3'
#         uuid = UUID(uuid_str)
#         node_id = ua.NodeId(uuid, 2, ua.NodeIdType.Guid)
#         newTemperatureNode = client.get_node(node_id)

        
