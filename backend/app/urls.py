from django.contrib import admin
from django.urls import path, include

# 1. IMPORT NOVO PARA O LOGIN (JWT)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# 2. Importamos as Views do Setor da nova pasta 'sectors'
from sector.views import SectorCreateListView, SectorRetrieveUpdateDestroyView

# 3. Importamos as Views de Usuário da pasta 'users'
from users.views import UsersCreateListView, UsersRetrieveUpdateDestroyView
from projects.views import ProjectCreateListView # (Se você já está usando include embaixo, talvez nem precise deste import)

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- ROTAS DE LOGIN (AUTENTICAÇÃO JWT) ---
    # É nesta rota que você vai dar o POST no Postman enviando username e password
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- Rotas dos Setores ---
    path('setores/', SectorCreateListView.as_view(), name='sector-create-list'),
    path('setores/<int:pk>/', SectorRetrieveUpdateDestroyView.as_view(), name='sector-detail-view'),

    # --- Rotas dos Usuários ---
    path('usuarios/', UsersCreateListView.as_view(), name='users-create-list'),
    path('usuarios/<int:pk>/', UsersRetrieveUpdateDestroyView.as_view(), name='users-detail-view'),

    # --- Rotas de Projetos ---
    path('projetos/', include('projects.urls')),
]