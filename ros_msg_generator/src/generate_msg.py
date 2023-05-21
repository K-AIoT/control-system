#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from actionlib_msgs.msg import GoalStatus, GoalStatusArray
import random

def generate_twist():
    twist = Twist()
    twist.linear.x = random.uniform(-1.0,1.0)
    twist.linear.y = random.uniform(-1.0,1.0)
    twist.linear.z = random.uniform(-1.0,1.0)
    twist.angular.x = random.uniform(-1.0,1.0)
    twist.angular.y = random.uniform(-1.0,1.0)
    twist.angular.z = random.uniform(-1.0,1.0)

    return twist

def generate_goal_status_array():
    status_array = GoalStatusArray()

    for i in range(1):
        goal_status = GoalStatus()
        goal_status.goal_id.id = str(i)
        goal_status.status = random.choice([0,1,2,3])
        status_array.status_list.append(goal_status)
    return status_array

def publish_random_messages():
    rospy.init_node('random_messages_publisher', anonymous = True)
    twist_pub = rospy.Publisher('robot/twistToMqtt', Twist, queue_size = 10)
    status_array_pub = rospy.Publisher('robot/goalStatusArrayToMqtt', GoalStatusArray, queue_size = 10)
    rate = rospy.Rate(0.1)
    while not rospy.is_shutdown():
        twist = generate_twist()
        status_array = generate_goal_status_array()
        twist_pub.publish(twist)
        status_array_pub.publish(status_array)
        rate.sleep()

if __name__ == '__main__':
    try:
        publish_random_messages()
    except rospy.ROSInterruptException:
         pass



