# main.py

import asyncio
import devices
import bridge
import mqttModule
from asyncua import Client

#MQTT Client Initialisation:
mqttBrokerIp = "192.168.1.22" #raspberry pi
mqttClient = mqttModule.makeClient("mqttClient", mqttBrokerIp)

#OPC UA Server Details:
opcuaServerUrl = "opc.tcp://10.64.233.49:4840"

async def main():
    print(f"Connecting to {opcuaServerUrl} ...")

    async with Client(url=opcuaServerUrl) as client: # Defines and initialises an OPC UA client and an associated asynchronous context block.
        nxtTechBridge = bridge.MqttOpcuaBridge(client, mqttClient) # Defines and initialises a bridge object to store the OPC UA and MQTT clients.
        
        dht22TempHumiditySensor = devices.Device(
            bridge = nxtTechBridge, 
            pubSubPairs = [ ("sensors/temperature", "3dbdca09-4b5c-b9ac-efd0-3184cdcceec3"),
                            ("sensors/humidity", "46d6d34e-622b-777a-744e-082d78f6e4c4")
        ])

        robot = devices.Robot(
            bridge = nxtTechBridge, 
            pubSubPairs = [ ("6fe4cadf-dfcf-7dbc-3a8b-3075c4098e8b", "robot/toGoal"),
                            # ("sensorsTest", "6fe4cadf-dfcf-7dbc-3a8b-3075c4098e8b"),
                            ("robot/goalStatusArrayToMqtt", "6fe4cadf-dfcf-7dbc-3a8b-3075c4098e8b")
        ])

        dht22DcMotor = devices.Device(
            bridge = nxtTechBridge, 
            pubSubPairs = [ ("62975aeb-ed5c-e4c0-c60f-035cc56ee09e", "dry/speed"),
                            ("dry/humidity", "5f7c3dab-348e-4886-0649-10f7423988ff"),
                            ("dry/temperature", "038e714d-5537-50e2-1967-3d79ffcf6db5")
        ])


        ultrasonicRangeLcd = devices.Device(
            bridge = nxtTechBridge, 
            pubSubPairs = [ ("LCD/distance", "9004fbb4-ed42-92ef-c571-4ce3a91e9812"),
                            ("3a75d7d0-0665-f5b8-eafd-2e61b0c3683a", "LCD/print")
        ])

        servo = devices.Device(
            bridge = nxtTechBridge, 
            pubSubPairs = [ ("b443ad4b-20dc-5ac7-3fdb-b74b784f3f7d", "actuators/servo/angles"),
                            ("actuators/servo/voltage", "938ffc9a-d230-b9f4-b82a-8b467b50195c")
        ])

        # robot = devices.Robot(
        #     bridge = nxtTechBridge, 
        #     pubSubPairs = [ ("robot/voltageToMqtt ", ""),
        #                     ("robot/fromCmdVel ", ""),
        #                     ("robot/fromStatus", ""),
        #                     ("", "robot/toGoal")
        # ])

        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())


        
