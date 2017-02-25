import asyncio

import aiohttp
import websockets
import asyncio_redis


class Notifier:
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
        self.r = yield from asyncio_redis.Connection.create(host=self.host, port=self.port, db=self.db)
        self.connections = set()
        self._make_server()

    def _make_server(self):
        start_server = websockets.serve(self.handler, self.host, self.port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def handler(self, websocket, path):
        if websocket in self.connections:
            while True:
                try:
                    websocket.send(await self._fetch(websocket))
                except websockets.ConnectionClosed:  # Client dismissed
                    break
        else:
            self._register(websocket)

    async def _fetch(self, key):
        return await self.r.get(key)

    async def _register(self, websocket):
        async with aiohttp.ClientSession().post('') as resp:
            valid = await resp.json()['ok']
            if valid:
                self.connections.add(websocket)
                return True

    async def _un_register(self, websocket):
        pass


