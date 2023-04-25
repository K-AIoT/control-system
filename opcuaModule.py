import asyncio
import logging

from asyncua import ua, Server
from asyncua.common.methods import uamethod

async def main():
    #Server setup
    opcuaServer = Server()
    await opcuaServer.init()
    opcuaServer.set_endpoint('opc.tcp://10.64.233.49:4840')
    opcuaServer.set_server_name("NxTTech IDE Server")