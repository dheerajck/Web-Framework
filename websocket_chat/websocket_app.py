#!/usr/bin/env python

import asyncio
import websockets
from ast import literal_eval


def message_format_and_authentication(message_dict):
    # Use a random secret token in the webapp chat view and here
    chat_auth_code = "2fcfdcedfb6290fa404c8a06e366a35555f4392293c6435ff326aa06f2ebd755"
    message_auth_code_from_client = message_dict["chat_auth_code"]
    if chat_auth_code == message_auth_code_from_client:
        user = message_dict["username"]
        message = message_dict["message"]
        final_message = f"{user}: {message}"
        return final_message
    else:
        False


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
    print(connection_path)
    try:
        async for message in websocket:

            message_dict = literal_eval(message)
            user_message = message_format_and_authentication(message_dict)

            if user_message:

                for conn in set(connection_path[path]):
                    if conn.open:
                        await conn.send(user_message)

                    else:
                        tp = connection_path[path]
                        tp.remove(conn)
                        connection_path[path] = tp

            else:
                available_connections = connection_path[path]
                available_connections.remove(websocket)
                connection_path[path] = available_connections
                # connected.remove(websocket)
    except Exception as e:
        print(f"Error occured, error details {e}")
    finally:
        # Unregister.
        if websocket in connection_path[path]:
            available_connections = connection_path[path]
            available_connections.remove(websocket)
            connection_path[path] = available_connections


async def main():
    print("Started")
    async with websockets.serve(server_handler, "localhost", 5000):
        await asyncio.Future()  # run forever


asyncio.run(main())
