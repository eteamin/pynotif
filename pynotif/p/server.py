import asyncio
import asyncio.subprocess
import websockets

async def handler(websocket, path):
    while True:
        data = await websocket.recv()
        print('I received a message')
        player = await asyncio.create_subprocess_exec(
            'sleep', '5',
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL)
        await player.wait()
        print('Finished waiting')

server = websockets.serve(handler, '0.0.0.0', '8000')
asyncio.get_event_loop().run_until_complete(server)
asyncio.get_event_loop().run_forever()