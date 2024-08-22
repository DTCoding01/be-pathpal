import pytest
from django.urls import reverse
from django.test import Client

def test_api_endpoints():
    client = Client()
    url = reverse('get_api')
    response = client.get(url)
    
    assert response.status_code == 200
    data = response.json()
    
    endpoints = data.get('endpoints', [])
    paths = [endpoint['path'] for endpoint in endpoints]
    
    assert "/api/user/create/" in paths
    assert "/api/user/<id>/" in paths
