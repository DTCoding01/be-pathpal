from rest_framework import serializers
from bson import ObjectId
from datetime import datetime, timezone

class ObjectIdField(serializers.Field):
    def to_representation(self, value):
        return str(value) if isinstance(value, ObjectId) else value

    def to_internal_value(self, data):
        try:
            return ObjectId(data)
        except (TypeError, ValueError):
            raise serializers.ValidationError("Invalid ObjectId")

class ThreeDModelSerializer(serializers.Serializer):
    id = ObjectIdField(source='_id', required=False)  
    name = serializers.CharField()
    file_name = serializers.CharField()
    category = serializers.CharField(allow_blank=True)
    description = serializers.CharField(allow_blank=True)
    created_at = serializers.DateTimeField(required=False)  
    color = serializers.CharField()

    def to_representation(self,instance):
        representation = super().to_representation(instance)
        if "created_at" not in representation or not representation['created_at']:
            representation['created_at'] = datetime.now(timezone.utc)
        return representation


    def create(self, validated_data):
        validated_data['_id'] = validated_data.get('_id', ObjectId()) 
        validated_data['created_at'] = validated_data.get('created_at', datetime.now(timezone.utc)) 
        return validated_data

class UserSerializer(serializers.Serializer):
    id = ObjectIdField(source='_id', read_only=True)
    name = serializers.CharField()
    email = serializers.EmailField()
    level = serializers.IntegerField(default=1)
    xp = serializers.IntegerField(default=0)
    step_details = serializers.DictField(required=False)
    pet_details = serializers.DictField(required=False)
    collected_items = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)

    def to_internal_value(self, data):
        if 'step_details' in data:
            step_details = data['step_details']
            step_details['step_goal'] = step_details.get('step_goal', 0)
            step_details.setdefault('total_steps', 0)
            step_details.setdefault('todays_steps', 0)
        if 'pet_details' in data:
            pet_details = data['pet_details']
            pet_details['selected_pet'] = pet_details.get('selected_pet', '')
            pet_details.setdefault('pet_name', '')
            pet_details.setdefault('selected_hat', '')
            pet_details.setdefault('selected_toy', '')
        return super().to_internal_value(data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['step_details'] = representation.get('step_details', {})
        representation['pet_details'] = representation.get('pet_details', {})
        return representation
