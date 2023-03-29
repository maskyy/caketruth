from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core import views

router = DefaultRouter()
router.register("meals", views.MealViewSet, "meals")
router.register("product-categories", views.ProductCategoryViewSet,
                "product-categories")
router.register("product-brands", views.ProductBrandViewSet, "product-brands")
router.register("products", views.ProductViewSet, "products")
router.register("recipe-categories", views.RecipeCategoryViewSet,
                "recipe-categories")
router.register("recipes", views.RecipeViewSet, "recipes")
router.register("diary", views.DiaryViewSet, "diary")

urlpatterns = [
    path("", include(router.urls)),
]
