from rest_framework import generics
from .models import Oficios
from .serializers import OficiosSerializer
import datetime
from django.db.models import Max

class OficiosListCreateView(generics.ListCreateAPIView):
    queryset = Oficios.objects.all().order_by('-data_oficio', '-id_oficio')
    serializer_class = OficiosSerializer

    def perform_create(self, serializer):
        ano = datetime.datetime.now().year
        data_oficio = datetime.datetime.now().date()
        
        # Obter o maximo numero_sequencial do ano atual
        max_num = Oficios.objects.filter(ano=ano).aggregate(Max('numero_sequencial'))['numero_sequencial__max']
        numero_sequencial = (max_num or 0) + 1

        serializer.save(ano=ano, data_oficio=data_oficio, numero_sequencial=numero_sequencial)

class OficiosRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Oficios.objects.all()
    serializer_class = OficiosSerializer
