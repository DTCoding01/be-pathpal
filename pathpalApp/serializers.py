from rest_framework import serializers
from bson import ObjectId
from datetime import datetime, timezone

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
    step_details = serializers.DictField()
    pet_details = serializers.DictField()
    collected_items = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)

    def to_internal_value(self, data):
        step_details = data.get('step_details', {})
        step_details['step_goal'] = data.pop('step_goal', step_details.get('step_goal', 0))
        step_details.setdefault('total_steps', 0)
        step_details.setdefault('todays_steps', 0)
        data['step_details'] = step_details
        
        pet_details = data.get('pet_details', {})
        pet_details.setdefault('pet_name', '')
        pet_details['selected_pet'] = data.pop('selected_pet', pet_details.get('selected_pet', ''))
        pet_details.setdefault('selected_hat', '')
        pet_details.setdefault('selected_toy', '')
        data['pet_details'] = pet_details

        return super().to_internal_value(data)