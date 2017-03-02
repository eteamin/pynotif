import asyncio
import json

import aiohttp
import websockets
from redis import StrictRedis


class Notifier:
    def __init__(self, host, port, db, server_url, config):
        self.host = host
        self.port = port
        self.db = db
        self.r = StrictRedis(host=self.host, port=self.port, db=self.db)
        self.url = server_url
        self.config = config
        self.connections = {}  # Key: client_id, Value = websocket
        self.pending_notifs = {}  # In case client has dismissed for a while
        self._setup()

    def _setup(self):
        start_server = websockets.serve(self._handler, self.host, self.port)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_server)
        loop.run_forever()

    async def _handler(self, websocket, path):
        if websocket in self.connections:
            while True:
                try:
                    await websocket.send(await self._fetch(websocket))
                except websockets.ConnectionClosed:  # Client dismissed
                    break
        elif await self._register(websocket):
            while True:
                try:
                    await websocket.send(await self._fetch(websocket))
                except websockets.ConnectionClosed:  # Client dismissed
                    self._un_register(websocket)
                    break

    async def _fetch(self, key):
        return self.r.get(key)

    async def _register(self, websocket):
        data = await websocket.recv()
        async with aiohttp.ClientSession().post('http://{}'.format(self.url), data=data) as resp:
            r = await resp.text()
            if self._ensure_validity(r):
                account = r.get('account')
                self.connections.add(websocket)
                return True

    async def _un_register(self, websocket):
        # self.connections.remove(websocket)
        pass

    async def _headers(self):
        pass

    async def _ensure_validity(self, data):
        try:
            payload = json.dumps(data)
            return True if payload.get('ok') is True and payload.get('account') else False
        except json.JSONDecodeError:
            return False




