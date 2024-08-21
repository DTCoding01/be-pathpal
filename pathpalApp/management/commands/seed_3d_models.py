import os
from django.core.management.base import BaseCommand
from pymongo import MongoClient
from gridfs import GridFS
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
        fs = GridFS(db)

        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing 3D models...'))
            db.three_d_models.delete_many({})
            fs.delete()

        def upload_file_to_gridfs(file_path):
            with open(file_path, 'rb') as file_data:
                return fs.put(file_data, filename=os.path.basename(file_path))

        models_folder = 'test_3d_files'
        
        
        for filename in os.listdir(models_folder):
            if filename.endswith('.glb'):
                try:
                    name = os.path.splitext(filename)[0]
                    glb_file_path = os.path.join(models_folder, filename)
                    
                    glb_id = upload_file_to_gridfs(glb_file_path)
                    
                    
                    model = ThreeDModel(
                        name=name,
                        glb_id=glb_id,
                    )
                    
                    serialized_data = ThreeDModelSerializer(model).data
                    
                    result = db.three_d_models.insert_one(serialized_data)
                    self.stdout.write(self.style.SUCCESS(f"Inserted {name} with ID: {result.inserted_id}"))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing {filename}: {str(e)}"))
        
        client.close()
        self.stdout.write(self.style.SUCCESS('Successfully seeded 3D models'))