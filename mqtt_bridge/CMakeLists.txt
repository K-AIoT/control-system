cmake_minimum_required(VERSION 3.0.2)
project(mqtt_bridge)

find_package(catkin REQUIRED COMPONENTS message_generation std_msgs rospy)
catkin_python_setup()
#catkin_package()

add_message_files(
	FILES
	IntList.msg
)

generate_messages(
	DEPENDENCIES
	std_msgs
)

catkin_package(
	CATKIN_DEPENDS 
	message_runtime
)

install(PROGRAMS
   scripts/mqtt_bridge_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

install(DIRECTORY config
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

