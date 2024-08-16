from django.conf import settings

def create_test_user(data):
    user_collection = settings.MONGO_DB["users"]
    user_id = user_collection.insert_one(data).inserted_id
    return user_id
