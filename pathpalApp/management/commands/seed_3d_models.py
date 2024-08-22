import os
from django.core.management.base import BaseCommand
from pymongo import MongoClient
from django.conf import settings
from pathpalApp.models.three_d_models import ThreeDModel
from pathpalApp.serializers import ThreeDModelSerializer

class Command(BaseCommand):
    help = 'Seed the database with 3D models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing 3D models before seeding',
        )

    def handle(self, *args, **options):
        client = MongoClient(settings.MONGO_URI)
        db = client[settings.MONGO_DB_NAME]


        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing 3D models...'))
            db.three_d_models.delete_many({})
        
        if options['file']:
            json_file_path = options['file']
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_file_path = os.path.join(base_dir, 'pathpalApp','three_d_models.json')

        try:
            with open(json_file_path,'r') as file:
                models_data=json.load(file)
            for model_data in models_data:
                try:
                    model=ThreeDModel.from_dict(model_data)
                    serialized_data=ThreeDModelSerializer(model).data
                    result=db.three_d_models.insert_one(serialized_data)
                    self.stdout.write(self.style.SUCCESS(f'Inserted{model.name}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error inserting model{model.name}'))
        except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error reading json file'))
        
        client.close()
        self.stdout.write(self.style.SUCCESS('Successfully seeded 3D models'))