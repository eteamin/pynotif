import asyncio
from base64 import b64encode

from pyDes import triple_des
import aiohttp
import websockets
from redis import StrictRedis


class Notifier:
    def __init__(self, config):
        self.config = config
        self.host, self.port = self.config.get('ws_server').split(':')
        self.db = self.config.get('db')
        self.r = StrictRedis(db=self.db)
        self.url = self.config.get('http_server')
        self.connections = {}  # Key: client_id, Value = websocket
        self.pending_notifs = {}  # In case client has dismissed for a while

    def serve(self):
        start_server = websockets.serve(self._handler, self.host, self.port)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_server)
        loop.run_forever()

    # noinspection PyUnusedLocal
    async def _handler(self, websocket, path):
        if websocket not in self.connections:
            headers = {
                'account': websocket.request_headers.get('account'),
                'session': websocket.request_headers.get('session'),
            }
            if not await self._register(websocket, headers):
                return
        print("new valid conn")
        account = self.connections.get(websocket)
        while True:
            notif = await self._fetch(account)
            try:
                await websocket.send(notif)
            except websockets.ConnectionClosed:  # Client dismissed
                await self._un_register(websocket)
                break

    async def _fetch(self, key):
        return self.r.get(key)

    async def _register(self, websocket, headers):
        async with aiohttp.ClientSession().post('http://{}'.format(self.url), headers=await self._headers(headers)) as resp:
            r = await resp.json()
            if await self._ensure_validity(r):
                account = r.get('account')
                self.connections[websocket] = account
                return True

    async def _headers(self, headers):
        return {
            'session': headers.get('session'),
            'account': headers.get('account'),
            'token': str(b64encode(
                bytes(
                    triple_des(self.config.get('auth_secret_key')).encrypt(self.config.get('auth_message'), padmode=2)
                )
            ))
        }

    async def _un_register(self, websocket):
        del self.connections[websocket]

    @staticmethod
    async def _ensure_validity(data):
        return True if bool(data.get('ok')) is True and data.get('account') else False
