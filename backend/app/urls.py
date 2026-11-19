from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rotas da API baseadas no padrão example (prefixadas com api/v1/)
    path('api/v1/', include('users.urls')),
    path('api/v1/', include('sector.urls')),
    path('api/v1/', include('oficios.urls')),
    path('api/v1/', include('projects.urls')),
]
