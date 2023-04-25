    import asyncio

    from asyncua import Client

    opcuaServerUrl = "opc.tcp://10.64.233.49:4840"

    namespaceUri = "http://opcfoundation.org/UA/"

    # async def updateAttributeVal(node, attributeName):
    #     attributeVal = await asyncio.wait_for(attributeName, None) #Wait for variable_name to change with no timeout (None)
    #     node.write_value(attributeVal)

    async def opcuaMain():

        print(f"Connecting to {opcuaServerUrl} ...")

        async with Client(url=opcuaServerUrl) as client:
            # Find the namespace index
            nsidx = await client.get_namespace_index(namespaceUri)
            
            # Get the variable node for read / write
            var = await client.nodes.root.get_child(
                ["0:Objects", f"{nsidx}:actuatorInput"]
            )
            value = await var.read_value()
            print(value)

            #new_value = value - 50
            
            #await var.write_value(new_value)

            # Calling a method
            #res = await client.nodes.objects.call_method(f"{nsidx}:ServerMethod", 5)
            

    if __name__ == "__main__":
        asyncio.run(opcuaMain())


