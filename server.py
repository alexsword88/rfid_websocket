import asyncio
import concurrent
from json.decoder import JSONDecodeError
import websockets
import json

USERS = set()


async def register(websocket):
    global USERS
    print("*** New Connection")
    USERS.add(websocket)


async def unregister(websocket):
    global USERS
    print("*** Connection Disconnected")
    USERS.remove(websocket)


async def broadcastEvent(websocket, message):
    global USERS
    if USERS:
        for user in USERS:
            if user != websocket:
                await user.send(message)


async def main(websocket, path):
    await register(websocket)
    try:
        async for message in websocket:
            msg = None
            try:
                msg = json.loads(message)
            except JSONDecodeError:
                continue
            print(msg)
            try:
                if msg["event"] == "onReadTag":
                    await broadcastEvent(websocket, message)
                elif msg["event"] == "triggerOn":
                    await broadcastEvent(websocket, message)
            except concurrent.futures.CancelledError:
                pass
    finally:
        await unregister(websocket)

asyncio.get_event_loop().run_until_complete(
    websockets.serve(main, 'localhost', 7749))
asyncio.get_event_loop().run_forever()
