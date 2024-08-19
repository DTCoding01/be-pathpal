from datetime import datetime, UTC
from bson import ObjectId

class ThreeDModel:
    def __init__(self, name, obj_id, mtl_id=None, category="", _id=None):
        self._id = ObjectId() if _id is None else ObjectId(_id)
        self.name = name
        self.obj_file = str(obj_id)
        self.mtl_file = str(mtl_id) if mtl_id else None
        self.category = category
        self.created_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
        
    def to_dict(self):
        return {
            "_id": self._id,
            "name": self.name,
            "obj_file": self.obj_file,
            "mtl_file": self.mtl_file,
            "category": self.category,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data['name'],
            obj_id=data['obj_file'],
            mtl_id=data.get('mtl_file'),
            category=data.get('category', ""),
            _id=data.get('_id')
        )