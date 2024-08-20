import os
import gridfs
from bson import ObjectId
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import pytest
from pymongo import MongoClient
from django.conf import settings
from pathpalApp.models.three_d_models import ThreeDModel

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
        "obj_file_path": "test_3d_files/test_cube.obj",
        "mtl_file_path": "test_3d_files/test_cube.mtl"
    }

@pytest.fixture
def setup_model(db_connection, sample_3d_model_data):
    db, fs, collection = db_connection

    with open(sample_3d_model_data['obj_file_path'], 'rb') as obj_file:
        obj_id = fs.put(obj_file, filename=os.path.basename(sample_3d_model_data['obj_file_path']))

    with open(sample_3d_model_data['mtl_file_path'], 'rb') as mtl_file:
        mtl_id = fs.put(mtl_file, filename=os.path.basename(sample_3d_model_data['mtl_file_path']))

    model = ThreeDModel(
        name=sample_3d_model_data['name'],
        obj_id=obj_id,
        mtl_id=mtl_id
    )

    collection.insert_one(model.to_dict())
    
    # Yielding the setup data to use in tests
    yield {
        'db': db,
        'fs': fs,
        'collection': collection,
        'obj_id': obj_id,
        'mtl_id': mtl_id,
        'model': model
    }

    # Teardown code to run after each test
    collection.delete_many({})

def test_insert_3d_model(db_connection, sample_3d_model_data):
    db, fs, collection = db_connection

    with open(sample_3d_model_data['obj_file_path'], 'rb') as obj_file:
        obj_id = fs.put(obj_file, filename=os.path.basename(sample_3d_model_data['obj_file_path']))

    with open(sample_3d_model_data['mtl_file_path'], 'rb') as mtl_file:
        mtl_id = fs.put(mtl_file, filename=os.path.basename(sample_3d_model_data['mtl_file_path']))

    model = ThreeDModel(
        name=sample_3d_model_data['name'],
        obj_id=str(obj_id), 
        mtl_id=str(mtl_id) if mtl_id else None 
    )

    result = collection.insert_one(model.to_dict())
    inserted_id = result.inserted_id

    assert inserted_id is not None
    inserted_model = collection.find_one({"_id": inserted_id})
    assert inserted_model is not None
    assert inserted_model['name'] == sample_3d_model_data['name']
    assert inserted_model['obj_file'] == str(obj_id)  
    assert inserted_model['mtl_file'] == str(mtl_id) if mtl_id else None 

    assert fs.exists(ObjectId(str(obj_id)))
    assert fs.exists(ObjectId(str(mtl_id))) if mtl_id else True


def test_retrieve_3d_model(db_connection, sample_3d_model_data):
    db, fs, collection = db_connection

    with open(sample_3d_model_data['obj_file_path'], 'rb') as obj_file:
        obj_id = fs.put(obj_file, filename=os.path.basename(sample_3d_model_data['obj_file_path']))

    with open(sample_3d_model_data['mtl_file_path'], 'rb') as mtl_file:
        mtl_id = fs.put(mtl_file, filename=os.path.basename(sample_3d_model_data['mtl_file_path']))

    model = ThreeDModel(
        name=sample_3d_model_data['name'],
        obj_id=str(obj_id),  
        mtl_id=str(mtl_id) if mtl_id else None 
    )
    collection.insert_one(model.to_dict())

    retrieved_model = collection.find_one({"name": sample_3d_model_data['name']})
    assert retrieved_model is not None

    obj_file = fs.get(ObjectId(retrieved_model['obj_file']))  
    mtl_file = fs.get(ObjectId(retrieved_model['mtl_file'])) if retrieved_model['mtl_file'] else None

    assert obj_file is not None
    if mtl_file:
        assert mtl_file is not None
    assert obj_file.filename == os.path.basename(sample_3d_model_data['obj_file_path'])
    assert mtl_file.filename == os.path.basename(sample_3d_model_data['mtl_file_path']) if mtl_file else True
