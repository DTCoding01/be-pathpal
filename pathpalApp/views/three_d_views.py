from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from ..serializers import ThreeDModelSerializer
from django.conf import settings
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)

class ThreeDModelListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            client = MongoClient(settings.MONGO_URI)
            db = client[settings.MONGO_DB_NAME]
            collection = db['three_d_models']
            models = list(collection.find())
            for model in models:
                model['_id'] = str(model['_id'])

            serializer = ThreeDModelSerializer(models, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in ThreeDModelListView: {str(e)}")
            return Response(
                {"error": "An error occurred while retrieving 3D models."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            if 'client' in locals():
                client.close()