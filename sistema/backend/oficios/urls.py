from django.urls import path
from . import views

urlpatterns = [
    path('oficios/', views.OficiosListCreateView.as_view(), name='oficios-list-create'),
    path('oficios/<int:pk>/', views.OficiosRetrieveUpdateDestroyView.as_view(), name='oficios-detail'),
]
