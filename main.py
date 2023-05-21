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
        #     pubSubPairs = [ ("robot/voltageToMqtt", "9cea813c-6199-26ed-abee-e7c93229ed6f"),    #voltage
        # ])

        robot = devices.Robot(
            bridge = nxtTechBridge, 
            pubSubPairs = [ ("robot/voltageToMqtt", "9cea813c-6199-26ed-abee-e7c93229ed6f"),    #voltage
                            ("robot/fromCmdVel", "56bd9ac6-9460-2822-61b9-660ae9186f04"),       #angularX
                            ("robot/fromCmdVel", "33ee6565-5a27-e7c0-2230-32c97f49b6e5"),       #angularY
                            ("robot/fromCmdVel", "80a434ff-e3ea-b250-305e-40613ed4f2b3"),       #angularZ
                            ("robot/fromCmdVel", "8c201322-e9d9-bef4-cb3b-92c710e98a22"),       #linearX
                            ("robot/fromCmdVel", "c8165fd4-0685-cb44-a0a9-8ea39ce1b29d"),       #linearY  
                            ("robot/fromCmdVel", "26739853-cfb5-63e1-4b17-592ec6eaa24e"),       #linearZ
                            ("robot/fromStatus", "cf9317b2-833d-b9c9-ab92-fd3031d6542b"),       #goal_idStatus
                            ("robot/fromGoal", "6d68d432-ebf1-bee3-0d99-28fbefc60bf7"),         #orientationW
                            ("robot/fromGoal", "acd4f401-e2c9-6173-ebe2-652d8a20fb3c"),         #orientationX
                            ("robot/fromGoal", "6004cbb2-54e0-389a-075e-032c8dde67fb"),         #orientationY
                            ("robot/fromGoal", "a5bb792c-008e-0d9b-a838-17fae76688f9"),         #orientationZ
                            ("robot/fromGoal", "6d334997-846a-45f3-2175-c77982cbded3"),         #positionX
                            ("robot/fromGoal", "395e04f6-8e50-cb3e-ddea-8bbb220b3471"),         #positionY
                            ("robot/fromGoal", "d94f18e8-305b-f21e-6fec-c8a3c58adecf"),         #positionZ
                            ("5b05e394-f794-3b52-e5a7-fe36049affa5", "robot/toGoal")            #position_id

        ])

        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())


        
