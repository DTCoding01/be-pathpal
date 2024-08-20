from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers import UserSerializer
from ..models.user_models import User
from django.conf import settings
from pathpalApp.utils.db_connection import get_collection
import logging

logger = logging.getLogger(__name__)

class UserCreateView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        logger.info(f"Request data: {request.data}")
        
        if serializer.is_valid():
            user_data = serializer.validated_data
            logger.info(f"Validated data: {user_data}")
            logger.info(f"Inserting user into database: {settings.MONGO_DB_NAME}, collection: users")
            try:
                user = User(
                    name=user_data['name'],
                    email=user_data['email'],
                    step_details=user_data['step_details'],
                    pet_details=user_data['pet_details'],
                    collected_items=user_data['collected_items']
                )
                inserted_id = user.insert()
                logger.info(f"User inserted with ID: {inserted_id}")
                
                # Verify the user was actually inserted
                users_collection, _ = get_collection('users')
                inserted_user = users_collection.find_one({"_id": inserted_id})
                if inserted_user:
                    logger.info(f"User successfully retrieved after insertion: {inserted_user}")
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
        users = User.get_all_users()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)