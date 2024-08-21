from datetime import datetime, UTC
from bson import ObjectId

class ThreeDModel:
    def __init__(self, name, glb_id, category="", _id=None):
        self._id = ObjectId() if _id is None else ObjectId(_id)
        self.name = name
        self.glb_id = str(glb_id)
        self.category = category
        self.created_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
        
    def to_dict(self):
        return {
            "_id": self._id,
            "name": self.name,
            "glb_id": self.glb_id,
            "category": self.category,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data['name'],
            glb_id=data['glb_id'],
            category=data.get('category', ""),
            _id=data.get('_id')
        )