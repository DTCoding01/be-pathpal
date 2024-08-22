import pytest
from pymongo import MongoClient
from django.conf import settings
from pathpalApp.models.three_d_models import ThreeDModel
from pathpalApp.serializers import ThreeDModelSerializer
from rest_framework.test import APIClient

@pytest.fixture(scope="function")
def db_connection():
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    collection = db['three_d_models']
    yield db, collection
    client.close()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def sample_3d_model_data():
    return {
        "name": "test_cube",
        "file_name": "test_cube.glb",
        "category": "test_category",
        "description": "A test cube model",
    }

@pytest.fixture
def setup_model(db_connection, sample_3d_model_data):
    db, collection = db_connection

    model = ThreeDModel(
        name=sample_3d_model_data['name'],
        file_name=sample_3d_model_data['file_name'],
        category=sample_3d_model_data['category'],
        description=sample_3d_model_data['description'],
    )
    
    serialized_data = ThreeDModelSerializer(model).data
    collection.insert_one(serialized_data)
    
    yield {
        'db': db,
        'collection': collection,
        'model': model,
    }

    collection.delete_many({})

def test_insert_3d_model(db_connection, sample_3d_model_data):
    db, collection = db_connection

    model = ThreeDModel(
        name=sample_3d_model_data['name'],
        file_name=sample_3d_model_data['file_name'], 
        category=sample_3d_model_data['category'],
        description=sample_3d_model_data['description'],
    )
    
    serialized_data = ThreeDModelSerializer(model).data
    result = collection.insert_one(serialized_data)
    inserted_id = result.inserted_id

    assert inserted_id is not None

    inserted_model = collection.find_one({"_id": inserted_id})
    assert inserted_model is not None
    assert inserted_model['name'] == sample_3d_model_data['name']
    assert inserted_model['file_name'] == sample_3d_model_data['file_name']  
    assert inserted_model['category'] == sample_3d_model_data['category']
    assert inserted_model['description'] == sample_3d_model_data['description']
