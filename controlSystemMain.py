import mqttModule
import msgpack
import time
from random import randrange

mqttClient = mqttModule.makeClient("mqttClient")
mqttPublishTopics = ["robot/fromBuzzer", "robot/ToMoveBaseSimple/Goal", "actuators/servo", "robot/intListToRos", "resistors/potmeter"]
# inputData = [1, 2, 3] # For intList test
# inputData = {'data': False} # For Bool test
# inputData = 
inputData = {'linear' : {'x': 0.2, 'y' : 0.0, 'z' : 0.0}, 'angular' : {'x': 0.0, 'y' : 0.0, 'z' : 0.0}} #For twist message test


while True:

#Used with robot/boolToRos test:
    # inputData['data'] = not inputData['data']

    # mqttModule.mqttPublishData(mqttClient, "robot/toBuzzer" , inputData)

    # time.sleep(1)

#Used with robot/intListToRos test:
    # for i in range(len(inputData)):
    #     inputData[i] += 1

    # for topic in mqttPublishTopics:
    #     mqttModule.mqttPublishData(mqttClient, topic, inputData)

#Used with robot/cmd_vel test:
    # for key in inputData['linear']:
    #     inputData['linear'][key] = -inputData['linear'][key]

    # mqttModule.mqttPublishData(mqttClient, "robot/toVelRaw", inputData)

    # time.sleep(0.01)

#Used with robot/ToMoveBaseSimple/Goal test:   
    
    poseStamped = {'header': {'seq': 0, 'stamp': {'secs': 1683119373, 'nsecs': 994051246}, 'frame_id': 'map'}, 'pose': {'position': {'x': -1.399324893951416, 'y': 0.36991798877716064, 'z': 0.0}, 'orientation': {'x': 0.0, 'y': 0.0, 'z': 0.9893189277112782, 'w': 0.1457671405777269}}}

    packedPoseStamped = msgpack.packb(poseStamped)

    mqttClient.publish("robot/toGoal", packedPoseStamped)  

    time.sleep(6)

# header: seq: 0 stamp: secs: 0 nsecs: 0 frame_id: world