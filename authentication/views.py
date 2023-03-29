from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Roles, User
from .serializers import UserSerializer, select_serializer


class UserViewSet(GenericViewSet):
    def get_serializer_class(self, request=None):
        if self.action == "partial_update" and request:
            return select_serializer(request.user.role.id)
        return UserSerializer

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [perm() for perm in permission_classes]

    def retrieve(self, request, pk=None):
        if pk is None:
            pk = request.user.id
        user = get_object_or_404(User, id=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = self.get_serializer_class(request)(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        if request.user.role.id == Roles.USER and int(pk) != request.user.id:
            raise PermissionDenied("Cannot change other users")

        user = get_object_or_404(User, id=pk)
        serializer = self.get_serializer_class(request)(
            user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
