from pymongo import MongoClient
from django.conf import settings
import logging 

logger = logging.getLogger(__name__)

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]
    
def get_collection(collection_name):
    
    logger.info(f"Getting collection {collection_name} from database {db.name}")
    collection = db[collection_name]
    return collection, client