from datetime import datetime, UTC
from bson import ObjectId

class ThreeDModel:
    def __init__(self, name, file_name, description="", category="", _id=None):
        self._id = ObjectId() if _id is None else ObjectId(_id)
        self.name = name
        self.file_name = file_name
        self.description = description
        self.category = category
        self.created_at = datetime.now(UTC)
        
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data['name'],
            file_name=data['file_name'],
            category=data['category'],
            description=data['description']
        )    
   