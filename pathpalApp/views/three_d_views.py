from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from ..serializers import ThreeDModelSerializer
from ..utils.db_connection import MongoDBClient
import logging

logger = logging.getLogger(__name__)
collection = MongoDBClient.get_collection('three_d_models')

class ThreeDModelListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            models = list(collection.find())
            # parse the model IDs into strings
            for model in models:
                model['_id'] = str(model['_id'])
            # serialize the MongoDB data into a dictionary
            serializer = ThreeDModelSerializer(models, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "An error occurred while retrieving 3D models."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            # close the MongoDB connection at the end of the process
            
                      
class ThreeDModelNameView(APIView):
    def get(self, request, name):
        try:
            model = collection.find_one({name: name})
            serializer = ThreeDModelSerializer(model)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"An error occurred while retrieving 3D model {name}."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )