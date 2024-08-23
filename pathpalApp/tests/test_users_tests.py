import pytest
import json
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework import status
from bson import ObjectId
from pathpalApp.views.users_views import UserView, UserGetByEmailView
from django.core.management import call_command
from pymongo import MongoClient
from django.conf import settings

@pytest.fixture(scope="function")
def db_connection():
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    collection = db['users']
    collection.delete_many({})  
    yield db, collection
    collection.delete_many({})  
    client.close()

@pytest.mark.django_db
class UserViewTests(APITestCase):
    @pytest.fixture(autouse=True)
    def setup_view(self, db_connection):
        self.factory = APIRequestFactory()
        self.view = UserView.as_view()
        self.db, self.collection = db_connection

    def test_create_user_success(self):
        request_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "step_details": {"step_goal": 10000},
            "pet_details": {"pet_name": "Fluffy"},
            "collected_items": ["item1", "item2"]
        }
        request = self.factory.post('/api/users/', request_data, format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], request_data['email'])

    def test_get_users_success(self):
        self.collection.insert_many([
            {"_id": ObjectId(), "name": "John Doe", "email": "john.doe@example.com"},
            {"_id": ObjectId(), "name": "Jane Doe", "email": "jane.doe@example.com"}
        ])

        request = self.factory.get('/api/users/')
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

@pytest.mark.django_db
class UserGetByEmailViewTests(APITestCase):
    @pytest.fixture(autouse=True)
    def setup_view(self, db_connection):
        self.factory = APIRequestFactory()
        self.view = UserGetByEmailView.as_view()
        self.db, self.collection = db_connection

    def test_get_user_by_email_success(self):
        user = {"_id": ObjectId(), "name": "John Doe", "email": "john.doe@example.com"}
        self.collection.insert_one(user)

        request = self.factory.get('/api/users/john.doe@example.com/')
        response = self.view(request, email='john.doe@example.com')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], user['email'])

    def test_patch_user_by_email_success(self):
        user = {"_id": ObjectId(), "name": "John Doe", "email": "john.doe@example.com", "step_details": {"step_goal": 10000}}
        self.collection.insert_one(user)

        patch_data = {"step_details": {"step_goal": 15000}}
        request = self.factory.patch('/api/users/john.doe@example.com/', patch_data, format='json')
        response = self.view(request, email='john.doe@example.com')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['step_details']['step_goal'], 15000)

@pytest.mark.django_db
def test_seed_users(db_connection, tmpdir):
    db, collection = db_connection
    
    json_file = tmpdir.join("test_users.json")
    test_data = [
        {"name": "Alice", "email": "alice@example.com"},
        {"name": "Bob", "email": "bob@example.com"}
    ]
    json_file.write(json.dumps(test_data))

    call_command('seed_users', str(json_file))

    assert collection.count_documents({}) == 2
    assert collection.find_one({"name": "Alice"}) is not None
    assert collection.find_one({"name": "Bob"}) is not None