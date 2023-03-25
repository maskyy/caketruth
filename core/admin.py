"""Register the app models"""
from django.contrib import admin
from .models import *  # pylint: disable=wildcard-import,unused-wildcard-import

admin.site.register(Meal)
admin.site.register(FoodType)
admin.site.register(Food)
admin.site.register(ProductCategory)
admin.site.register(ProductBrand)
admin.site.register(Product)
admin.site.register(RecipeCategory)
admin.site.register(Recipe)
admin.site.register(RecipeProduct)
admin.site.register(Diary)
