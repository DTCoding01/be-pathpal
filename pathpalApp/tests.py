import pytest
from django.conf import settings
from pathpalApp.services.user_service import create_test_user

@pytest.mark.django_db
def test_create_test_user():
    data = {'name': 'test user', 'email': 'test@user.com'}
    user_id = create_test_user(data)
    user = settings.MONGO_DB['users'].find_one({'_id': user_id})
    
    assert user is not None
    assert user['name'] == 'test user'
    assert user['email'] == 'test@user.com'