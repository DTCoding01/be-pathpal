from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers import UserSerializer
from ..utils.db_connection import MongoDBClient
import logging

logger = logging.getLogger(__name__)
collection = MongoDBClient.get_collection('users')

class UserView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            user_data = serializer.validated_data
            try:
                inserted_id = collection.insert_one(user_data).inserted_id
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
    
    def get(self, request):
        try:
            users = list(collection.find({}))
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error retrieving users: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def deep_update(original, updates):
    for key, value in updates.items():
        if isinstance(value, dict):
            original[key] = deep_update(original.get(key, {}), value)
        else:
            original[key] = value
    return original 

class UserGetByEmailView(APIView):
    def get(self, request, email):
        collection = MongoDBClient.get_collection('users')
        try:
            user = collection.find_one({'email': email})
            if user is None:
                return Response({"error": "user not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error retrieving user: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, email):
        collection = MongoDBClient.get_collection('users')
        try:
            user = collection.find_one({"email": email})
            if user is None:
                return Response({"error":"user not found"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                try:
                    updated_data = deep_update(user, serializer.validated_data)
                    collection.update_one({'email':email}, {'$set':updated_data})
                    updated_user = collection.find_one({'email':email})
                    return Response(UserSerializer(updated_user).data, status=status.HTTP_200_OK)
                except Exception as e:
                    logger.error(f"error updating user: {str(e)}")
                    return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:   
             logger.error(f"Error in PATCH operation: {str(e)}")
             return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
