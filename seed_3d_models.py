import os
from pymongo import MongoClient
from gridfs import GridFS
from decouple import config

from pathpalApp.models.three_d_models import ThreeDModel

MONGO_URI = config('MONGO_URI')
MONGO_DB_NAME = config('MONGO_DB_NAME')

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
fs = GridFS(db)

def upload_file_to_gridfs(file_path):
    with open(file_path, 'rb') as file_data:
        return fs.put(file_data, filename=os.path.basename(file_path))

def seed_3d_models():
    models_folder = 'test_3d_files'
    
    print("Current working directory:", os.getcwd())
    print("Full path of models folder:", os.path.abspath(models_folder))
    
    for filename in os.listdir(models_folder):
        if filename.endswith('.obj'):
            try:
                name = os.path.splitext(filename)[0]
                obj_file_path = os.path.join(models_folder, filename)
                mtl_file_path = os.path.join(models_folder, f"{name}.mtl")
                
                obj_id = upload_file_to_gridfs(obj_file_path)
                
                mtl_id = None
                if os.path.exists(mtl_file_path):
                    mtl_id = upload_file_to_gridfs(mtl_file_path)
                
                model = ThreeDModel(
                    name=name,
                    obj_id=obj_id,
                    mtl_id=mtl_id
                )
                
                result = db.three_d_models.insert_one(model.to_dict())
                print(f"Inserted {name} with ID: {result.inserted_id}")
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                

if __name__ == "__main__":
    seed_3d_models()
                    