import asyncio

import websockets

async def client():
    async with websockets.connect('ws://localhost:8000') as websocket:
        await websocket.send('message')
        await asyncio.sleep(0.5)


tasks = asyncio.gather(*[client() for i in range(5)])

asyncio.get_event_loop().run_until_complete(tasks)