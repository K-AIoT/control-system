#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist, PoseStamped
from actionlib_msgs.msg import GoalStatus, GoalStatusArray
from std_msgs.msg import Float32
import random

def generate_twist():
    twist = Twist()
    twist.linear.x = random.uniform(-1.0, 1.0)
    twist.linear.y = random.uniform(-1.0, 1.0)
    twist.linear.z = random.uniform(-1.0, 1.0)
    twist.angular.x = random.uniform(-1.0, 1.0)
    twist.angular.y = random.uniform(-1.0, 1.0)
    twist.angular.z = random.uniform(-1.0, 1.0)

    return twist

def generate_goal_status_array():
    status_array = GoalStatusArray()

    for i in range(1):
        goal_status = GoalStatus()
        goal_status.goal_id.id = str(i)
        goal_status.status = random.choice([0, 1, 2, 3])
        status_array.status_list.append(goal_status)

    return status_array

def generate_pose_stamped():
    pose_stamped = PoseStamped()
    pose_stamped.header.stamp = rospy.Time.now()
    pose_stamped.header.frame_id = "map"
    pose_stamped.pose.position.x = random.uniform(-1.0, 1.0)
    pose_stamped.pose.position.y = random.uniform(-1.0, 1.0)
    pose_stamped.pose.position.z = random.uniform(-1.0, 1.0)
    pose_stamped.pose.orientation.x = random.uniform(-1.0, 1.0)
    pose_stamped.pose.orientation.y = random.uniform(-1.0, 1.0)
    pose_stamped.pose.orientation.z = random.uniform(-1.0, 1.0)
    pose_stamped.pose.orientation.w = random.uniform(-1.0, 1.0)

    return pose_stamped

def generate_float32():
    float32_msg = Float32()
    float32_msg.data = random.uniform(-1.0, 1.0)

    return float32_msg

def publish_random_messages():
    rospy.init_node('random_messages_publisher', anonymous=True)
    twist_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    status_array_pub = rospy.Publisher('/move_base/status', GoalStatusArray, queue_size=10)
    pose_pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=10)
    float32_pub = rospy.Publisher('/voltage', Float32, queue_size=10)
    rate = rospy.Rate(0.1)

    while not rospy.is_shutdown():
        twist = generate_twist()
        status_array = generate_goal_status_array()
        pose_stamped = generate_pose_stamped()
        float32_msg = generate_float32()

        twist_pub.publish(twist)
        status_array_pub.publish(status_array)
        pose_pub.publish(pose_stamped)
        float32_pub.publish(float32_msg)

        rate.sleep()

if __name__ == '__main__':
    try:
        publish_random_messages()
    except rospy.ROSInterruptException:
        pass

