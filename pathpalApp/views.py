from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt 
from pathpalApp.services.user_service import create_test_user

@csrf_exempt
def create_user(request):
    if request.method == "POST": 
        data = request.POST
        user_id = create_test_user(data)
        return JsonResponse({"id": str(user_id)})
    
