from django.shortcuts import get_object_or_404
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from authentication.permissions import IsOwner, IsStaffOrReadOnly, IsStaffOrOwnerOrReadOnly
from rest_framework.exceptions import PermissionDenied
from authentication.models import Roles
from .models import *  # pylint: disable=wildcard-import,unused-wildcard-import
from .serializers import *  # pylint: disable=wildcard-import,unused-wildcard-import


class MealViewSet(ModelViewSet):
    serializer_class = MealSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Meal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductCategoryViewSet(ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsStaffOrReadOnly]


class ProductBrandViewSet(ModelViewSet):
    queryset = ProductBrand.objects.all()
    serializer_class = ProductBrandSerializer
    permission_classes = [IsStaffOrReadOnly]


# TODO search
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [IsStaffOrOwnerOrReadOnly]

    def get_serializer_class(self, request=None):
        if self.action == "list":
            return ProductListSerializer
        if request and request.user.role.id != Roles.USER:
            return ProductStaffSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def partial_update(self, request, pk=None):
        product = get_object_or_404(Product, id=pk)
        if request.user.role.id == Roles.USER and request.user.id != product.user.id:
            raise PermissionDenied("Cannot change other users' products")
        serializer = self.get_serializer_class(request)(
            product, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class RecipeCategoryViewSet(ModelViewSet):
    queryset = RecipeCategory.objects.all()
    serializer_class = RecipeCategorySerializer
    permission_classes = [IsStaffOrReadOnly]


# TODO search
class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DiaryViewSet(ModelViewSet):
    serializer_class = DiarySerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Diary.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
