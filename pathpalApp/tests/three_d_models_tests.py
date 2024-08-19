import os
import pytest
from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.conf import settings

from pathpalApp.models.three_d_models import ThreeDModel
from decouple import config

@pytest.fixture(scope="module")
def db_connection():
    client = MongoClient(config('MONGO_URI'))
    db = client[config('MONGO_DB_NAME') + '_test']
    fs = GridFS(db)
    yield db, fs
    client.drop_database(db.name)

@pytest.fixture
def sample_3d_model_data():
    return {
        "name": "test_cube",
        "obj_file_path": "test_3d_files/test_cube.obj",
        "mtl_file_path": "test_3d_files/test_cube.mtl"
    }

def test_insert_3d_model(db_connection, sample_3d_model_data):
    db, fs = db_connection

    with open(sample_3d_model_data['obj_file_path'], 'rb') as obj_file:
        obj_id = fs.put(obj_file, filename=os.path.basename(sample_3d_model_data['obj_file_path']))
    
    with open(sample_3d_model_data['mtl_file_path'], 'rb') as mtl_file:
        mtl_id = fs.put(mtl_file, filename=os.path.basename(sample_3d_model_data['mtl_file_path']))

    model = ThreeDModel(
        name=sample_3d_model_data['name'],
        obj_id=obj_id,
        mtl_id=mtl_id
    )

    result = db.three_d_models.insert_one(model.to_dict())
    inserted_id = result.inserted_id

    assert inserted_id is not None
    inserted_model = db.three_d_models.find_one({"_id": inserted_id})
    assert inserted_model is not None
    assert inserted_model['name'] == sample_3d_model_data['name']
    assert ObjectId(inserted_model['obj_file']) == obj_id
    assert ObjectId(inserted_model['mtl_file']) == mtl_id

    assert fs.exists(obj_id)
    assert fs.exists(mtl_id)

def test_retrieve_3d_model(db_connection, sample_3d_model_data):
    db, fs = db_connection

    model = db.three_d_models.find_one({"name": sample_3d_model_data['name']})
    assert model is not None

    obj_file = fs.get(ObjectId(model['obj_file']))
    mtl_file = fs.get(ObjectId(model['mtl_file']))

    assert obj_file is not None
    assert mtl_file is not None
    assert obj_file.filename == os.path.basename(sample_3d_model_data['obj_file_path'])
    assert mtl_file.filename == os.path.basename(sample_3d_model_data['mtl_file_path'])
    
    
class ThreeDModelAPITestCase(APITestCase):
    def setUp(self):
        
        client = MongoClient(settings.MONGO_URI)
        self.db = client[settings.MONGO_DB_NAME + '_test']
        self.collection = self.db['three_d_models']

        self.test_model = {
            "name": "test_cube",
            "obj_file": "obj123",
            "mtl_file": "mtl456",
            "category": "test"
        }
        self.collection.insert_one(self.test_model)

    def tearDown(self):
        self.db.drop_collection('three_d_models')

    def test_get_three_d_models(self):
        url = reverse('three_d_model_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.test_model['name'])