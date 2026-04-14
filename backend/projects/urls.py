from django.urls import path
from .views import ProjectCreateListView

urlpatterns = [
    path('', ProjectCreateListView.as_view(), name='project-list'),
]