from django.contrib import admin
from django.urls import path, include

# 1. Importamos as Views do Setor da nova pasta 'sectors'
from sector.views import SectorCreateListView, SectorRetrieveUpdateDestroyView

# 2. Importamos as Views de Usuário da pasta 'users'
from users.views import UsersCreateListView, UsersRetrieveUpdateDestroyView
from projects.views import ProjectCreateListView

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- Rotas dos Setores ---
    path('setores/', SectorCreateListView.as_view(), name='sector-create-list'),
    path('setores/<int:pk>/', SectorRetrieveUpdateDestroyView.as_view(), name='sector-detail-view'),

    # --- Rotas dos Usuários ---
    path('usuarios/', UsersCreateListView.as_view(), name='users-create-list'),
    path('usuarios/<int:pk>/', UsersRetrieveUpdateDestroyView.as_view(), name='users-detail-view'),




    path('projetos/', include('projects.urls')),
]