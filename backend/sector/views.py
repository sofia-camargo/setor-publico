from rest_framework import generics
from .models import Sector
from .serializers import SectorSerializer

# View para listar todos os setores e criar um novo
class SectorCreateListView(generics.ListCreateAPIView):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer

# View para ver detalhes, editar e deletar UM setor específico
class SectorRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer