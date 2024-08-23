import pytest
import json
from unittest.mock import patch
from bson import ObjectId
from django.core.management import call_command
from pymongo import MongoClient
from django.conf import settings
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework import status
from pathpalApp.views.three_d_views import ThreeDModelListView, ThreeDModelNameView


@pytest.fixture(scope="function")
def db_connection():
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    collection = db['three_d_models']
    yield db, collection
    client.close()

def test_seed_3d_models(db_connection, tmpdir):
    db, collection = db_connection
    
    json_file = tmpdir.join("test_three_d_models.json")
    test_data = {
        "models": [
            {
                "name": "test_cube",
                "file_name": "test_cube.glb",
                "category": "test_category",
                "description": "A test cube model",
            },
            {
                "name": "test_sphere",
                "file_name": "test_sphere.glb",
                "category": "test_category",
                "description": "A test sphere model",
            }
        ]
    }
    json_file.write(json.dumps(test_data))

    call_command('seed_3d_models', '--file', str(json_file), '--clear')

    assert collection.count_documents({}) == 2
    assert collection.find_one({"name": "test_cube"}) is not None
    assert collection.find_one({"name": "test_sphere"}) is not None

class ThreeDModelViewTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch('pathpalApp.views.three_d_views.collection.find')
    def test_get_all_models_success(self, mock_find):
        mock_find.return_value = [
            {"_id": ObjectId(), "name": "Model1", "file_name": "model1.glb", "description": "", "category": "test"},
            {"_id": ObjectId(), "name": "Model2", "file_name": "model2.glb", "description": "", "category": "test"},
        ]

        request = self.factory.get('/api/3d-models/')
        response = ThreeDModelListView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'Model1')
        self.assertEqual(response.data[1]['name'], 'Model2')

    @patch('pathpalApp.views.three_d_views.collection.find_one')
    def test_get_model_by_name_success(self, mock_find_one):
        mock_find_one.return_value = {
            "_id": ObjectId(),
            "name": "Model1",
            "file_name": "model1.glb",
            "description": "",
            "category": "test"
        }

        request = self.factory.get('/api/3d-models/Model1/')
        response = ThreeDModelNameView.as_view()(request, name='Model1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['model']['name'], 'Model1')

    @patch('pathpalApp.views.three_d_views.collection.find_one')
    def test_get_model_by_name_not_found(self, mock_find_one):
        mock_find_one.return_value = None

        request = self.factory.get('/api/3d-models/NonExistentModel/')
        response = ThreeDModelNameView.as_view()(request, name='NonExistentModel')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
