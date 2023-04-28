#devices.py

import asyncio


class OpcuaNode:

#Class Attributes/Methods:
    def __init__(self, nodeId):
        #Instance Attributes/Methods:
        self.__opcuaNodeId = nodeId
        __opcuaNodeId = None

    async def setOpcuaNodeId(self, nid):
        self.__opcuaNodeId = nid

    async def getOpcuaNodeId(self):
        return self.__opcuaNodeId


class Sensor(OpcuaNode):

#Class Attributes/Methods:
    def __init__(self, nodeId): #Contains instance Attributes/Methods:
        super().__init__(nodeId)
        __reading = None

    async def setReading(self, newReading):
        self.__reading = newReading

    async def getReading(self):
        return self.__reading


class Actuator(OpcuaNode):

#Class Attributes/Methods:
    def __init__(self, nodeId): #Contains instance Attributes/Methods:
        super().__init__(nodeId)
        __actuatorInput = None

    async def setInput(self, newInput):
        self.__actuatorInput = newInput

    async def getInput(self):
        return self.__actuatorInput