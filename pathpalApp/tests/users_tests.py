import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.conf import settings
from pymongo import MongoClient
import logging
logger = logging.getLogger(__name__)


# sets up the database and cleans it for each function
@pytest.fixture(scope="function")
def db_connection():
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    collection = db['users']
    yield collection
    collection.delete_many({})
    client.close()

@pytest.fixture(autouse=True)
def clean_database(db_connection):
    db_connection.delete_many({})

@pytest.fixture
def api_client():
    return APIClient()

class TestUserAPI:
    def test_create_user(self, api_client, db_connection):
        url = reverse('user-create')
        new_user_data = {
            "name": "Alice Smith",
            "email": "alice.smith@example.com",
            "step_details": {"step_goal": 12000},
            "pet_details": {"selected_pet": "Bird"},
            "collected_items": []
        }
        response = api_client.post(url, new_user_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

        inserted_user = db_connection.find_one({"email": "alice.smith@example.com"})
        assert inserted_user is not None
        assert inserted_user['name'] == new_user_data['name']

    def test_get_users(self, api_client, db_connection):
        db_connection.insert_one({
            "name": "Alice Smith",
            "email": "alice.smith@example.com",
            "step_details": {'step_goal': 12000},
            "pet_details": {'selected_pet': "Bird"},
            "collected_items": []
        })

        url = reverse('user-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == "Alice Smith"

def test_mongodb_connection():
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    assert db.command("ping")["ok"] == 1
    client.close()
