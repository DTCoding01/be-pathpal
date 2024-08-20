from django.core.management.base import BaseCommand
from ...models.user_models import User
import json
import os

class Command(BaseCommand):
    help = 'Seed the database with test users'
    
    def handle(self, *args, **kwargs): 
        
        file_path = os.path.join(os.path.dirname(__file__), '../../../test_users.json')
        file_path = os.path.abspath(file_path)
        with open(file_path, 'r') as file: 
            users_data = json.load(file)
            
        for user_data in users_data: 
            user = User(
                name=user_data['name'],
                email=user_data['email'],
                step_details={'step_goal': user_data['step_goal']},
                pet_details={'selected_pet': user_data['selected_pet']},
                collected_items=user_data.get('collected_items', [])
            )
            user.insert()
            self.stdout.write(self.style.SUCCESS(f"Successfully added user {user.name}"))