from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Roles, User
from .permissions import IsStaffOrOwnerOrReadOnly
from .serializers import UserSerializer, select_serializer


@api_view(["POST"])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsStaffOrOwnerOrReadOnly])
def update_user(request, pk=None):
    if pk is None:
        pk = request.user.id

    if request.user.role.id == Roles.USER and pk != request.user.id:
        raise PermissionDenied("Cannot change other users")

    user = User.objects.get(id=pk)
    serializer = select_serializer(request.user.role.id)(
        user, data=request.data, partial=True)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_info(request, pk=None):
    if pk is None:
        pk = request.user.id
    user = get_object_or_404(User, id=pk)
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)
