from django.core.management.base import BaseCommand
from ...serializers import UserSerializer
from ...utils.db_connection import MongoDBClient
import json
import os

class Command(BaseCommand):
    help = 'Seed the database with test users'
    
    def handle(self, *args, **kwargs): 
        # Load the JSON data from the file
        file_path = os.path.join(os.path.dirname(__file__), '../../../test_users.json')
        file_path = os.path.abspath(file_path)
        with open(file_path, 'r') as file: 
            users_data = json.load(file)
        
        # Get the MongoDB collection using the MongoDBClient
        users_collection = MongoDBClient.get_collection('users')

        # Loop over the users data and insert into MongoDB
        for user_data in users_data: 
            # Serialize the data using UserSerializer
            serializer = UserSerializer(data=user_data)
            if serializer.is_valid():
                # Insert the serialized data into MongoDB
                users_collection.insert_one(serializer.validated_data)
                self.stdout.write(self.style.SUCCESS(f"Successfully added user {user_data['name']}"))
            else:
                self.stdout.write(self.style.ERROR(f"Failed to add user {user_data['name']}: {serializer.errors}"))
