import mqttModule
import devices
import time
from geometry_msgs.msg import Twist
from random import randrange

mqttClient = mqttModule.makeClient("mqttClient")
mqttPublishTopics = ["actuators/servo", "robot/intListToRos", "resistors/potmeter"]
# inputData = [1, 2, 3]

twist_msg = Twist()
twist_msg.linear.x = 0.2
twist_msg.linear.y = 0.0
twist_msg.linear.z = 0.0
twist_msg.angular.x = 0.0
twist_msg.angular.y = 0.0
twist_msg.angular.z = 0.0

while True:

    #inputData['data'] = not inputData['data']

    # for i in range(len(inputData)):
    #     inputData[i] += 1

    # for topic in mqttPublishTopics:
    #     mqttModule.mqttPublishData(mqttClient, topic, inputData)

    # for key in inputData['linear']:
    #     inputData['linear'][key] = -inputData['linear'][key]


    twist_data = {
        'linear': {'x': twist_msg.linear.x, 'y': twist_msg.linear.y, 'z': twist_msg.linear.z},
        'angular': {'x': twist_msg.angular.x, 'y': twist_msg.angular.y, 'z': twist_msg.angular.z}}
    
    packed_twist_data = msgpack.packb(twist_data)

    mqttClient.publish("robot/cmd_vel", packed_twist_data)

    # mqttModule.mqttPublishData(mqttClient, "robot/toCmd_vel", inputData)
    

    time.sleep(0.005)
