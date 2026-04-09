from rest_framework import generics
from .models import users, sector 
from .serializers import UsersSerializer, SectorSerializer

class SectorCreateListView(generics.ListCreateAPIView):
    queryset = sector.objects.all()
    serializer_class = SectorSerializer

class UsersCreateListView(generics.ListCreateAPIView):
    queryset = users.objects.all()
    serializer_class = UsersSerializer


#coisinhas novas para deletar 

class SectorRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = sector.objects.all()
    serializer_class = SectorSerializer

class UsersRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = users.objects.all()
    serializer_class = UsersSerializer    