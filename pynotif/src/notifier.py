import asyncio
import websockets


class Notifier:
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
        self.make_server()

    def make_server(self):
        start_server = websockets.serve(self.hello, self.host, self.port)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def hello(self, websocket, path):
        name = await websocket.recv()
        print("< {}".format(name))

        greeting = "Hello {}!".format(name)
        await websocket.send(greeting)
        print("> {}".format(greeting))

