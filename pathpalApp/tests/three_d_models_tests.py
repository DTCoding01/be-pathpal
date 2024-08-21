import os
import gridfs
from bson import ObjectId
from rest_framework.test import APIClient
import pytest
from pymongo import MongoClient
from django.conf import settings
from pathpalApp.models.three_d_models import ThreeDModel
from pathpalApp.serializers import ThreeDModelSerializer

@pytest.fixture(scope="function")
def db_connection():
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    fs = gridfs.GridFS(db)
    collection = db['three_d_models']
    yield db, fs, collection
    client.close()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def sample_3d_model_data():
    return {
        "name": "test_cube",
        "glb_file_path": "test_3d_files/test_cube.glb",
    }

@pytest.fixture
def setup_model(db_connection, sample_3d_model_data):
    db, fs, collection = db_connection

    with open(sample_3d_model_data['glb_file_path'], 'rb') as glb_file:
        glb_id = fs.put(glb_file, filename=os.path.basename(sample_3d_model_data['glb_file_path']))


    model = ThreeDModel(
        name=sample_3d_model_data['name'],
        glb_id=glb_id,
    )
    
    serialized_data = ThreeDModelSerializer(model).data

    collection.insert_one(serialized_data)
    
    yield {
        'db': db,
        'fs': fs,
        'collection': collection,
        'glb_id': glb_id,
        'model': model
    }

    collection.delete_many({})

def test_insert_3d_model(db_connection, sample_3d_model_data):
    db, fs, collection = db_connection

    with open(sample_3d_model_data['glb_file_path'], 'rb') as glb_file:
        glb_id = fs.put(glb_file, filename=os.path.basename(sample_3d_model_data['glb_file_path']))


    model = ThreeDModel(
        name=sample_3d_model_data['name'],
        glb_id=str(glb_id), 
    )
    
    serialized_data = ThreeDModelSerializer(model).data

    result = collection.insert_one(serialized_data)
    inserted_id = result.inserted_id

    assert inserted_id is not None
    inserted_model = collection.find_one({"_id": inserted_id})
    assert inserted_model is not None
    assert inserted_model['name'] == sample_3d_model_data['name']
    assert inserted_model['glb_id'] == str(glb_id)  

    assert fs.exists(ObjectId(str(glb_id)))

