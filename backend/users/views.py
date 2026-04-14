from rest_framework import generics
from .models import users
from .serializers import UsersSerializer

class UsersCreateListView(generics.ListCreateAPIView):
    queryset = users.objects.all()
    serializer_class = UsersSerializer

class UsersRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = users.objects.all()
    serializer_class = UsersSerializer    