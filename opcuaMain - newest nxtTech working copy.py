import asyncio

from asyncua import Client, ua
from asyncua.ua import AccessLevelType
from uuid import UUID

url = "opc.tcp://10.64.233.49:4840"
namespace = "http://se.com/EcostruxureSystemExpert"


async def main():

    print(f"Connecting to {url} ...")
    async with Client(url=url) as client:
        # Find the namespace index
        nsidx = await client.get_namespace_index(namespace)
        print(f"Namespace Index for '{namespace}': {nsidx}")

        # nodeId = ua.NodeId(UUID("e0003595-e3e6-98f4-e46e-a2cccd71d8cb"), 2, ua.NodeIdType.Guid)
        nodeId = "ns=2;g={038e714d-5537-50e2-1967-3d79ffcf6db5}"
        node = client.get_node(nodeId)
        value = await node.read_value()

        print(f"Value of MyVariable ({node}): {value}")
 
        # try:
        # # Attempt a write operation
        #     await node.write_value(123)
        #     print("Write privileges are available for the node.")
        # except Exception as e:
        #     print(f"Write privileges are not available for the node. Error: {e}")
        
        newVal = ua.DataValue(ua.Variant(50.0, ua.VariantType.Float))
        
        await node.write_value(newVal)


if __name__ == "__main__":
    asyncio.run(main())