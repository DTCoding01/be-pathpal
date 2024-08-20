from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers import UserSerializer
from django.conf import settings
from pymongo import MongoClient
from ..utils.db_connection import get_collection
import logging

logger = logging.getLogger(__name__)

# Set up MongoDB client and database

collection, client = get_collection('users')

class UserCreateView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            user_data = serializer.validated_data
            try:
                # Insert the user data into MongoDB
                inserted_id = collection.insert_one(user_data).inserted_id
                
                # Verify the user was actually inserted
                inserted_user = collection.find_one({"_id": inserted_id})
                if inserted_user:
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    logger.error("User not found after insertion")
                    return Response({"error": "User not found after insertion"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            except Exception as e:
                logger.error(f"Error inserting user: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.error(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserListView(APIView):
    def get(self, request):
        try:
            users = list(collection.find({}))
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error retrieving users: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
