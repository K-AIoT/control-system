import asyncio
import json
import paho.mqtt.client as mqtt

class MQTTListener:
    def __init__(self, topic, client):
        self.topic = topic
        self.client = client
        self.message = None
        self.client.subscribe(self.topic)
        self.client.on_message = self.on_message

    def on_message(self, client, userdata, message):
        self.message = json.loads(message.payload.decode())

    async def get_message(self):
        while True:
            if self.message is not None:
                message = self.message
                self.message = None
                return message
            await asyncio.sleep(0.1)

class MyMQTTListener(MQTTListener):
    def __init__(self, topic, client):
        super().__init__(topic, client)
        # additional initialization for MyMQTTListener

class AnotherMQTTListener(MQTTListener):
    def __init__(self, topic, client):
        super().__init__(topic, client)
        # additional initialization for AnotherMQTTListener

async def listen_to_topics():
    client = mqtt.Client()
    client.connect("mqtt.example.com")

    listeners = [
        MyMQTTListener("topic1", client),
        AnotherMQTTListener("topic2", client),
        # add more listeners here
    ]

    await asyncio.gather(*[listener.get_message() for listener in listeners])

asyncio.run(listen_to_topics())
