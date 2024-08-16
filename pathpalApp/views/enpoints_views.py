import json
from django.http import JsonResponse
from pathlib import Path

def get_api(request):
    file_path = Path(__file__).resolve().parent / 'endpoints.json'
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return JsonResponse(data)