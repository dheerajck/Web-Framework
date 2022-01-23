#!/usr/bin/env python

import asyncio
import websockets
from ast import literal_eval


def message_format_and_authentication(message_dict):
    chat_auth_code = "2fcfdcedfb6290fa404c8a06e366a35555f4392293c6435ff326aa06f2ebd755"
    message_auth_code_from_client = message_dict["chat_auth_code"]
    if chat_auth_code == message_auth_code_from_client:
        # print("matched")
        user = message_dict["username"]
        message = message_dict["message"]
        final_message = f"{user}: {message}"
        return final_message
    else:
        False


connected = set()
connection_path = {}


async def server_handler(websocket, path):
    # connected.add(websocket)
    if path in connection_path:
        available_connections = connection_path[path]
        available_connections.add(websocket)
        connection_path[path] = available_connections
    else:
        connection_path[path] = {websocket}

    print(path)
    try:
        async for message in websocket:
            # print(message)
            message_dict = literal_eval(message)

            user_message = message_format_and_authentication(message_dict)
            # print(user_message)
            # user_message = True
            if user_message:
                # print(message_dict, type(message_dict))
                for conn in connection_path[path]:
                    # if conn != websocket:
                    # always show message of a user to him so he ccan verify message sending to others is succesfull
                    # if 1:
                    await conn.send(user_message)
                    # print(message)
                    # print(f'{message}')
                    # await conn.send(user_message)
                    # await conn.send(f'Got a new MSG FOR YOU: {message}')
            else:
                available_connections = connection_path[path]
                available_connections.remove(websocket)
                connection_path[path] = available_connections
                # connected.remove(websocket)
    except Exception as e:
        print(f"Error occured, error details {e}")
    finally:
        # Unregister.
        # if websocket in connected:
        #     connected.remove(websocket)
        if websocket in connection_path[path]:
            available_connections = connection_path[path]
            available_connections.remove(websocket)
            connection_path[path] = available_connections


async def main():
    print("Started")
    async with websockets.serve(server_handler, "localhost", 5000):
        await asyncio.Future()  # run forever


asyncio.run(main())
