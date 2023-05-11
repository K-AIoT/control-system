from asyncua import Client
import asyncio

opcuaServerUrl = "opc.tcp://10.64.233.49:4840"

async def my_async_function(opcuaServerUrl):
    while True:
        try:
            client = Client(url=opcuaServerUrl)
            await client.connect()

            async def my_disconnected_callback(client: Client):
                print("Disconnected from server, attempting to reconnect...")
                while True:
                    try:
                        await client.connect()
                        print("Reconnected to server")
                        break
                    except ConnectionError:
                        print("Could not connect to server, retrying in 5 seconds...")
                        await asyncio.sleep(5)

            client.on_disconnected = my_disconnected_callback

            print("Connected to server")
            while True:
                await asyncio.sleep(1)

            await client.disconnect()
            break
        except ConnectionError:
            print("Could not connect to server, retrying in 5 seconds...")
            await asyncio.sleep(5)