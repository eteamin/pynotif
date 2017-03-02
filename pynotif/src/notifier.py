import asyncio
import json

import aiohttp
import websockets
from redis import StrictRedis

from . import AsyncListOfTupleIteration


class Notifier:
    def __init__(self, ws_server, db, http_server_url, config):
        self.host, self.port = ws_server.split(':')
        self.db = db
        self.r = StrictRedis(host=self.host, port=self.port, db=self.db)
        self.url = http_server_url
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
    # noinspection PyUnusedLocal
    async def _handler(self, websocket, path):
        if websocket not in self.connections:
            if not await self._register(websocket):
                return
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
            if await self._ensure_validity(r):
                account = r.get('account')
                self.connections[account] = websocket
                return True

    async def _un_register(self, websocket):
        key = None
        async for k, v in AsyncListOfTupleIteration(self.connections.items()):
            if v == websocket:
                key = k
        del self.connections[key]

    async def _headers(self):
        pass

    @staticmethod
    async def _ensure_validity(data):
        try:
            payload = json.dumps(data)
            return True if payload.get('ok') is True and payload.get('account') else False
        except json.JSONDecodeError:
            return False
