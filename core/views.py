from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.viewsets import ModelViewSet

from authentication.permissions import IsOwner, IsStaffOrReadOnly

from .models import * # pylint: disable=wildcard-import,unused-wildcard-import
from .serializers import * # pylint: disable=wildcard-import,unused-wildcard-import


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
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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
