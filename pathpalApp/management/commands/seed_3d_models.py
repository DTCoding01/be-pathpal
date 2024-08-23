import os
import json
from django.core.management.base import BaseCommand
from pymongo import MongoClient
from django.conf import settings
from pathpalApp.serializers import ThreeDModelSerializer

class Command(BaseCommand):
    help = 'Seed the database with 3D models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing 3D models before seeding',
        )
        parser.add_argument(
            '--file',
            type=str,
            help='The JSON file containing 3D models data',
        )

    def handle(self, *args, **options):
        client = MongoClient(settings.MONGO_URI)
        db = client[settings.MONGO_DB_NAME]

        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing 3D models...'))
            db.three_d_models.delete_many({})

        json_file_path = options.get('file')
        if not json_file_path:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            json_file_path = os.path.join(base_dir, 'three_d_models.json')
        
        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)
                models_data = data.get('models', [])

            for model_data in models_data:
                try:
                    serializer = ThreeDModelSerializer(data=model_data)
                    if serializer.is_valid():
                        serialized_data = serializer.validated_data
                        result = db.three_d_models.insert_one(serialized_data)
                        self.stdout.write(self.style.SUCCESS(f'Inserted {model_data["name"]} with ID: {result.inserted_id}'))
                    else:
                        self.stdout.write(self.style.ERROR(f'Validation failed for model {model_data.get("name", "unknown")}: {serializer.errors}'))
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error inserting model: {str(e)}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading JSON file: {str(e)}'))

        client.close()
        self.stdout.write(self.style.SUCCESS('Successfully seeded 3D models'))
