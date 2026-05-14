from rest_framework import generics
from rest_framework.permissions import IsAuthenticated  # <-- 1. IMPORTA O CADEADO
from .models import Sector
from .serializers import SectorSerializer

# View para listar todos os setores e criar um novo
class SectorCreateListView(generics.ListCreateAPIView):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    permission_classes = [IsAuthenticated]  # <-- 2. TRANCA ESTA ROTA

# View para ver detalhes, editar e deletar UM setor específico
class SectorRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    permission_classes = [IsAuthenticated]  # <-- 3. TRANCA ESTA ROTA TAMBÉM