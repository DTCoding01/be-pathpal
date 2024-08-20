from pymongo import MongoClient
from django.conf import settings
from ..utils.db_connection import get_collection

class User: 
    def __init__(self, name, email, step_details, pet_details, collected_items):
        self.name = name
        self.email = email
        self.step_details = {
                'step_goal': step_details['step_goal'],
                'total_steps': 0,
                'todays_steps': 0, 
                             }
        self.pet_details = {
            'selected_pet': pet_details['selected_pet'],
            'selected_hat': '',
            'selected_toy': '',
                            }
        self.collected_items = collected_items if collected_items else []
        
        # insert new user into db and store id on class object
    def insert(self):
        collection, client = get_collection('users')
        result = collection.insert_one(self.__dict__)
        self._id = result.inserted_id
        client.close()
        return self._id
        
        # return a list of all users
    @staticmethod
    def get_all_users():
        collection, client = get_collection('users')
        users = list(collection.find())
        client.close()
        return users