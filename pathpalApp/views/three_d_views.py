import logging
import gridfs
from bson import ObjectId
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from ..serializers import ThreeDModelSerializer
from ..utils.db_connection import MongoDBClient
from django.http import FileResponse


logger = logging.getLogger(__name__)
client = MongoDBClient.get_client()
db = client[MongoDBClient.get_db_name()]
collection = db['three_d_models']
fs = gridfs.GridFS(db)

class ThreeDModelListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            models = list(collection.find())
            # Convert ObjectId to string for serialization
            for model in models:
                model['_id'] = str(model['_id'])
            serializer = ThreeDModelSerializer(models, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.exception("Error retrieving 3D models")
            return Response(
                {"error": "An error occurred while retrieving 3D models."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ThreeDModelNameView(APIView):
    def get(self, request, name):
        try:
            model = collection.find_one({'name': name})
            if not model: 
                return Response({'error': "Model not found"}, status=status.HTTP_404_NOT_FOUND)

            file_name = model.get('file_name')
            
            response_content = {
                'model': ThreeDModelSerializer(model).data,
                'glb_file_url': f'/api/3d-models/files/{file_name}.glb' if file_name else None,
            }
            
            return Response(response_content, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(f"Error retrieving 3D model '{name}'")
            return Response(
                {"error": f"An error occurred while retrieving 3D model {name}."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FileDownloadView(APIView):
    def get(self, request, file_id):
        try:
            file = fs.get(ObjectId(file_id))
            response = FileResponse(file, content_type='model/gltf-binary')
            response['Content-Disposition'] = f'inline; filename={file.filename}'
            return response
        except gridfs.NoFile:
            logger.exception(f"File with ID '{file_id}' not found")
            return Response(
                {"error": "File not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception(f"Error retrieving file with ID '{file_id}'")
            return Response(
                {"error": "An error occurred while retrieving the file."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
