import asyncio
from base64 import b64encode

from pyDes import triple_des
import aiohttp
import websockets
import asyncio_redis


class Notifier:
    def __init__(self, config):
        self.config = config
        self.host, self.port = self.config.get('ws_server').split(':')
        self.db = self.config.get('db')
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
        self.r = await asyncio_redis.Connection.create(db=self.db)
        if websocket not in self.connections:
            # Client appends the account and the session to the headers for authentication purposes
            acc = websocket.request_headers.get('account')
            sess = websocket.request_headers.get('session')
            if not acc or not sess:
                await websocket.send("Auth failed!")
                return
            self.headers = {
                'account': acc,
                'session': sess,
            }
            if not await self._register(websocket):
                await websocket.send("Auth failed!")
                return
        account = self.connections.get(websocket)
        while True:
            notif = await self._fetch(account)
            try:
                print('Sending {}'.format(notif))
                await websocket.send(notif)
            except websockets.ConnectionClosed:  # Client dismissed
                await self._un_register(websocket)
                break

    async def _fetch(self, key):
        while True:
            value = await self.r.get(key)
            if not value:
                await asyncio.sleep(15)
                continue
            await self.r.delete([key])
            return value

    # Handle your own registration logic, either call an API or whatever
    async def _register(self, websocket):
        async with aiohttp.\
                ClientSession().\
                post('http://{}'.format(self.url), headers=await self._headers(self.headers)) as resp:
            r = await resp.json()
            if await self._ensure_validity(r):
                account = self.headers.get('account')
                self.connections[websocket] = account
                return True

    # Handle your own header authentication
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
        return True if bool(data.get('ok')) is True else False
