from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt 
from pathpalApp.services.user_service import create_test_user
from django.conf import settings

@csrf_exempt
def create_user(request):
    if request.method == "POST": 
        data = request.POST
        user_id = create_test_user(data)
        return JsonResponse({"id": str(user_id)})
    
def test_mongo_connection(request):
    try:
        collections = settings.MONGO_DB.list_collection_names()
        return JsonResponse({"status": "success", "collections": collections})
    except Exception as e:
        return JsonResponse({"status": "error", "msg": str(e)})
        