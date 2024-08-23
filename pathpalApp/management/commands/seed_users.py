import json
import os
from django.core.management.base import BaseCommand
from ...serializers import UserSerializer
from ...utils.db_connection import MongoDBClient


class Command(BaseCommand):
    help = 'Seed the database with test users'
    
    def add_arguments(self, parser):
       
        parser.add_argument(
            '--file',
            type=str,
            help='The JSON file containing users data',
        )

    def handle(self, *args, **options):
        if options['file']:
            file_path = options['file_path']
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            file_path = os.path.join(base_dir, 'test_users.json')
            
        
        with open(file_path, 'r') as file:
            users_data = json.load(file)

        users_collection = MongoDBClient.get_collection('users')

        for user_data in users_data:
            existing_user = users_collection.find_one({"email": user_data['email']})
            if existing_user is None:
                serializer = UserSerializer(data=user_data)
                if serializer.is_valid():
                    users_collection.insert_one(serializer.validated_data)
                    self.stdout.write(self.style.SUCCESS(f"Successfully added user {user_data['name']}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Failed to add user {user_data['name']}: {serializer.errors}"))
            else:
                self.stdout.write(self.style.WARNING(f"User {user_data['name']} already exists, skipping"))