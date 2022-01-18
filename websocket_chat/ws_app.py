#!/usr/bin/env python

import asyncio
import websockets

connected = set()


async def server_handler(websocket):
    connected.add(websocket)
    try:
        async for message in websocket:
            for conn in connected:
                if conn != websocket:
                    await conn.send(f'Got a new MSG FOR YOU: {message}')
    except Exception as e:
        print(f"Error occured, error details {e}")
    finally:
        # Unregister.
        connected.remove(websocket)


async def main():
    print("Started")
    async with websockets.serve(server_handler, "localhost", 5000):
        await asyncio.Future()  # run forever


asyncio.run(main())
