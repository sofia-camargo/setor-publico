from rest_framework import generics
from .models import Users
from .serializers import UsersSerializer

class UsersCreateListView(generics.ListCreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer

class UsersRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer    