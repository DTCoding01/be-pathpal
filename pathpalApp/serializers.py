from rest_framework import serializers

# convert the MongoDB data into a dictionary
class ThreeDModelSerializer(serializers.Serializer):
    id = serializers.CharField(source='_id')
    name = serializers.CharField()
    obj_file = serializers.CharField()
    mtl_file = serializers.CharField(allow_null=True)
    category = serializers.CharField(allow_blank=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()