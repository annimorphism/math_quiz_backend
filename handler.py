import json
from pprint import pprint
from typing import Dict
from fastapi import  WebSocket
from db import JsonDB
from maths_question_generator.arithmetic import Arithmetic
from starlette.websockets import WebSocketState


def custom_print(message: str):
    """
    Print a message with a custom prefix.
    """
    print("================[Message WS]=====================")
    print(message)
    print("================[X X X X X ]=====================")




def generate_random_question():
    a = Arithmetic(difficulty="hard")
    result = a.base()
    return result

def generate_and_add_question(db: JsonDB):
    """
    Generate a question and add it to the database.
    """
    quest = generate_random_question()
    db.add_question({
        "question": quest['question'],
        "answer": quest['answer']
    })
    return quest

class MessageHandler:
    def __init__(self):
        self.active_connections: Dict[WebSocket] = []
        self.current_question = 1
        self.db = JsonDB("db.json")

    
    def send_leaderboard(self):
        return self.db.get_leaderboard()

    def add_connection(self, websocket: WebSocket):
        self.active_connections.append(websocket)

    def send_leaderboard(self):
        return self.db.get_leaderboard()

    async def broadcast_json(self, message: str):

        for connection in self.active_connections: 
            print("Sending message to some client", connection)
            if connection.client_state == WebSocketState.CONNECTED:
                await connection.send_json(message)
            else:
                print("Removing connection. Not connected.")
                self.active_connections.remove(connection)

    async def broadcast_new_question(self):
        """
        Generate a new question and broadcast it to all the clients.
        Increment the current question id.
        """
        print("Generating new question")
        quest = generate_and_add_question(self.db)
        print("Increasing current question id")
        self.current_question += 1
        await self.broadcast_json({
            'type': 'newQuestion',
            'question': quest['question'],
            'question_id': self.current_question
        })
        
            

    async def handle_message(self, websocket: WebSocket, message: dict):

        custom_print(message)        
        name = message['name']
        type = message['type']


        if type == 'whoami':
            
            user = self.db.get_user_by_name(name)
            if user:
                await websocket.send_json({
                    'type': 'add_user',
                    'success': False,
                    'message': 'User already exists'
                })
            else:
                self.db.add_user({"name" : name})
                await websocket.send_json({
                    'type': 'add_user',
                    'success': True,
                    'message': 'User added'
                })

            LB = self.send_leaderboard()
            await self.broadcast_json({
                            'type': 'score',
                            'score': LB
                        })
                
            return

        if type == 'get_questions':
            questions = self.db.get_questions()
            if len(questions) == 0:
                quest = generate_and_add_question(self.db)
                await websocket.send_json({
                    'type': 'get_questions',
                    'question': quest['question'],
                    'question_id': self.current_question
                })
            else:
                for question in questions:
                    if question['id'] == self.current_question:
                        await websocket.send_json({
                            'type': 'get_questions',
                            'question': question['question'],
                            'question_id': self.current_question
                        })
                        # TODO : lets see what to do if the question is not found
                    # else:
                    #     """
                    #     If we did not found any question with id CURRENT_QUESTION, 
                    #     we generate a new one, add it to the database and 
                    #     increment CURRENT_QUESTION
                    #     """
                    #     quest = generate_and_add_question()
                    #     self.current_question += 1
                    #     await websocket.send_json({
                    #         'type': 'getCurrentQuestion',
                    #         'success': True,
                    #         'question': quest['question']
                    #     })
            return

        if type == 'answer':
            answer = message['answer']
            questions = self.db.get_questions()
            question_id  = message['question_id']

            # If the question id is not the same as the current question,
            # that means the client did not receive the broadcast of new 
            # question and is trying to answer the previous question.
            # Simply reject the answer and send the new question.
            if question_id != self.current_question:
                await websocket.send_json({
                    'type': 'oldQuestion',
                    'success': False,
                    'message': 'This question is already answered',
                    'question_id': question_id,
                    'id' : self.current_question
                })
                return

            for question in questions:
                if question['id'] == question_id:
                    if question['answer'] == answer:
                        await websocket.send_json({
                            'type': 'answer',
                            'success': True,
                            'message': 'Correct answer'
                        })
                        # increment the score of the user
                        self.db.increase_score(name)
                        LB = self.send_leaderboard()
                        await self.broadcast_json({
                            'type': 'score',
                            'score': LB
                        })
                        # broadcast the new question
                        await self.broadcast_new_question()
                    else:
                        await websocket.send_json({
                            'type': 'answer',
                            'success': False,
                            'message': 'Wrong answer'
                        })
                    
            return

        if type == 'getLeaderboard':
            users = self.db.get_users()
            leaderboard = sorted(users, key=lambda k: k['score'], reverse=True)
            await websocket.send_json({
                'type': 'getLeaderboard',
                'leaderboard': leaderboard
            })
            return

        print("EOF")
        print(message)
        return
            



        