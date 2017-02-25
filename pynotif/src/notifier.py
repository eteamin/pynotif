import asyncio
import websockets

import asyncio_redis

class Notifier:
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
        self.r = yield from asyncio_redis.Connection.create(host=self.host, port=self.port, db=self.db)
        self.connections = {}
        self.make_server()

    def make_server(self):
        start_server = websockets.serve(self.handler, self.host, self.port)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def handler(self, websocket, path):
        name = await websocket.recv()
        print("< {}".format(name))

        greeting = "Hello {}!".format(name)
        await websocket.send(greeting)
        print("> {}".format(greeting))

    async def _fetch(self, key):
        return await self.r.get(key)

    async def _register(self, websocket):
        pass

    async def _un_register(self, websocket):
        pass


