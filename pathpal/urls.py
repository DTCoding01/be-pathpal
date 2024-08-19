"""
URL configuration for pathpal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from pathpalApp.views.enpoints_views import get_api
from pathpalApp.views.three_d_views import ThreeDModelListView


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('api/', get_api, name="get_api"),
    path('api/3d-models/', ThreeDModelListView.as_view(), name="three_d_model_list"),
]
