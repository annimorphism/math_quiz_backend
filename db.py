import json


"""
This class is used to manage the database

"users" : [
    {"id": 1, "name": "John", "score": 0},
]

"questions" : [
    {"id": 1, "question": "6 + 6 / 2", "answer": "9", "solved" : false, "user_id": 1},
]

"leaderboard" : [ 
    {"id": 1, "user_id": 1, "score": 0},
]

"""


class JsonDB:

    def __init__(self, path):
        self.path = path
        # create file if it doesn't exist
        with open(self.path, 'a') as f:
            self.write({
                'users': [],
                'questions': []
            })
            pass

    def read(self):
        with open(self.path, 'r') as f:
            return json.load(f)

    def write(self, data):
        with open(self.path, 'w') as f:
            json.dump(data, f, indent=4)

    def get(self, key):
        return self.read().get(key)

    def set(self, key, value):
        data = self.read()
        data[key] = value
        self.write(data)

    def delete(self, key):
        data = self.read()
        del data[key]
        self.write(data)

    
    def add_user(self, user: str):
        """Add a user to the database"""
        data = self.read()
        new_user = {
            'id': len(data["users"]) + 1,
            'name': user["name"],
            'score': 0
        }
        data['users'].append(new_user)
        self.write(data)


    def get_users(self):
        """Get all the users"""
        data = self.read()
        return data['users']
    
    def get_user_by_name(self, user_name: str):
        """Get a user by name"""
        data = self.read()
        for user in data['users']:
            if user['name'] == user_name:
                return user
        return None

    def get_questions(self):
        """Get all the questions"""
        data = self.read()
        return data['questions']

    def get_question_by_id(self, question_id: int):
        """Get a question by id"""
        data = self.read()
        for question in data['questions']:
            if question['id'] == question_id:
                return question
        return None
    
    def add_question(self, question: str):
        """Add a question to the database"""
        data = self.read()
        new_question = {
            'id': len(data['questions']) + 1,
            'question': question['question'],
            'answer': question['answer'],
        }
        data['questions'].append(new_question)
        self.write(data)
    
    def get_leaderboard(self):
        """Get the leaderboard"""
        data =  self.get_users()
        return sorted(data, key=lambda k: k['score'], reverse=True)

    def increase_score(self, user_name: str):
        """Increase the score of a user"""
        data = self.read()
        for user in data['users']:
            if user['name'] == user_name:
                user['score'] += 10
        self.write(data)
    



