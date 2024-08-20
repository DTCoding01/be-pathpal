from rest_framework import serializers
from bson import ObjectId

class ObjectIdField(serializers.Field):
    """Custom field to handle MongoDB ObjectId serialization and deserialization."""
    def to_representation(self, value):
        return str(value) if isinstance(value, ObjectId) else value

    def to_internal_value(self, data):
        try:
            return ObjectId(data)
        except (TypeError, ValueError):
            raise serializers.ValidationError("Invalid ObjectId")

class ThreeDModelSerializer(serializers.Serializer):
    id = ObjectIdField(source='_id')
    name = serializers.CharField()
    obj_file = serializers.CharField()
    mtl_file = serializers.CharField(allow_null=True)
    category = serializers.CharField(allow_blank=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

class UserSerializer(serializers.Serializer):
    id = ObjectIdField(source='_id', read_only=True)
    name = serializers.CharField()
    email = serializers.EmailField()
    step_details = serializers.DictField()
    pet_details = serializers.DictField()
    collected_items = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)

    def to_internal_value(self, data):
        if 'step_goal' in data:
            data['step_details'] = {'step_goal': data.pop('step_goal')}
        if 'selected_pet' in data:
            data['pet_details'] = {'selected_pet': data.pop('selected_pet')}
        return super().to_internal_value(data)
