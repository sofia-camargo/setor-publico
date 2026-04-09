"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from users.views import (
    SectorCreateListView, UsersCreateListView, 
    SectorRetrieveUpdateDestroyView, UsersRetrieveUpdateDestroyView)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('sector/', SectorCreateListView.as_view(), name='sector-create-list'),

    path('users/', UsersCreateListView.as_view(), name='users-create-list'),


    path('setores/<int:pk>/', SectorRetrieveUpdateDestroyView.as_view(), name='sector-detail-view'),

    path('usuarios/<int:pk>/', UsersRetrieveUpdateDestroyView.as_view(), name='users-detail-view'),


]
