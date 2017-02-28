import asyncio

import aiohttp
import websockets
import asyncio_redis


class Notifier:
    def __init__(self, host, port, db, server_url, config):
        self.host = host
        self.port = port
        self.db = db
        self.url = server_url
        self.config = config
        self.r = yield from asyncio_redis.Connection.create(host=self.host, port=self.port, db=self.db)
        self.connections = {}  # Key: client_id, Value = websocket
        self.pending_notifs = {}  # In case client has dismissed for a while
        self._make_server()

    def _make_server(self):
        start_server = websockets.serve(self._handler, self.host, self.port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def _handler(self, websocket, path):
        if websocket in self.connections:
            while True:
                try:
                    websocket.send(await self._fetch(websocket))
                except websockets.ConnectionClosed:  # Client dismissed
                    break
        elif self._register(websocket):
            while True:
                try:
                    websocket.send(await self._fetch(websocket))
                except websockets.ConnectionClosed:  # Client dismissed
                    self._un_register(websocket)
                    break

    async def _fetch(self, key):
        return await self.r.get(key)

    async def _register(self, websocket):
        data = websocket.recv()
        async with aiohttp.ClientSession().get(self.url) as resp:
            valid = await resp.json()['ok']
            if valid:
                self.connections.add(websocket)
                return True

    async def _un_register(self, websocket):
        self.connections.remove(websocket)


    async def _headers(self):
        pass

