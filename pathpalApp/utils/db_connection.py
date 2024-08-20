from pymongo import MongoClient
from django.conf import settings
import logging 
from django.conf import settings

logger = logging.getLogger(__name__)

class MongoDBClient:
    _client = None
    
    @staticmethod
    def get_db_name():
        return settings.MONGO_DB_NAME

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = MongoClient(settings.MONGO_URI)
        return cls._client

    @classmethod
    def get_collection(cls, collection_name):
        client = cls.get_client()
        db = client[settings.MONGO_DB_NAME]
        return db[collection_name]
