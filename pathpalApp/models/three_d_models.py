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
        
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data['name'],
            glb_id=data['glb_id'],
            category=data.get('category', ""),
            _id=data.get('_id')
        )