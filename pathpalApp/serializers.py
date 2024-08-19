from rest_framework import serializers
from bson import ObjectId

class ThreeDModelSerializer(serializers.Serializer):
    id = serializers.CharField(source='_id')
    name = serializers.CharField()
    obj_file = serializers.CharField()
    mtl_file = serializers.CharField(allow_null=True)
    category = serializers.CharField(allow_blank=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(instance, dict):
            id_value = instance.get('_id')
        else:
            id_value = getattr(instance, '_id', None)
        
        if isinstance(id_value, ObjectId):
            data['id'] = str(id_value)
        elif id_value is not None:
            data['id'] = str(id_value)
        return data