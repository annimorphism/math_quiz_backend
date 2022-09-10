from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI, WebSocket, Request, HTTPException
from db import JsonDB
import uvicorn
import json
from fastapi.middleware.cors import CORSMiddleware

from handler import MessageHandler
import starlette


app = FastAPI()
message_manager = MessageHandler()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
)


@app.get("/leaderboard")
async def get_score():
    return message_manager.send_leaderboard()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    try:
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            json_data = json.loads(data)
            
            # try:
            #     json_data = json.loads(data)
            #     name = json_data['name']

            # except KeyError:
            #     await websocket.send_json({
            #         "error": "Invalid request",
            #         "message": "Please provide a name and type"
            #     })
            #     return

            # except json.JSONDecodeError:
            #     await websocket.send_json({
            #         "error": "Invalid request",
            #         "message": "Please provide a valid JSON"
            #     })
            #     return

            # if not name:
            #     await websocket.send_json({
            #         "type": "error",
            #         "message": "Please enter a name"
            #     })
            #     return

            
            message_manager.add_connection(websocket)
            await message_manager.handle_message(websocket, json_data)

    except starlette.websockets.WebSocketDisconnect:
        print("Error: Websocket connection disconnected")




# Run the server directly from the main file
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, log_level="info")