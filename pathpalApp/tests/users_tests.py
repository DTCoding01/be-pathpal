import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.conf import settings
from pymongo import MongoClient
import logging
logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def db_connection():
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    collection = db['users']
    yield collection
    collection.delete_many({})  # Clean up after each test
    client.close()

@pytest.fixture(autouse=True)
def clean_database(db_connection):
    db_connection.delete_many({})

@pytest.fixture
def api_client():
    return APIClient()

class TestUserAPI:
    def test_create_user(self, api_client, db_connection):
        logger.info(f"Test is using database: {settings.MONGO_DB_NAME}")
        url = reverse('user-create')
        new_user_data = {
            "name": "Alice Smith",
            "email": "alice.smith@example.com",
            "step_details": {"step_goal": 12000},
            "pet_details": {"selected_pet": "Bird"},
            "collected_items": []
        }
        logger.info(f"Sending POST request to {url} with data: {new_user_data}")
        response = api_client.post(url, new_user_data, format='json')
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response data: {response.data}")
        assert response.status_code == status.HTTP_201_CREATED

        logger.info(f"Searching for user in database: {db_connection.name}")
        inserted_user = db_connection.find_one({"email": "alice.smith@example.com"})
        logger.info(f"Retrieved user: {inserted_user}")
        assert inserted_user is not None
        assert inserted_user['name'] == new_user_data['name']

    def test_get_users(self, api_client, db_connection):
        # Add a user to the collection first
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

# Add these print statements at the beginning of the file for debugging
print("MONGO_URI:", settings.MONGO_URI)
print("MONGO_DB_NAME:", settings.MONGO_DB_NAME)