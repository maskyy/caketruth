"""Provides models for the app"""
from django.db import models
from authentication.models import User


class Meal(models.Model):
    """A user's meal and its name"""
    name = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class FoodType(models.Model):
    """product or recipe"""
    name = models.CharField(max_length=64)


class Food(models.Model):
    """Represents a food item which must be either a product or a recipe"""
    name = models.CharField(max_length=64)
    calories = models.FloatField()
    proteins = models.FloatField()
    fats = models.FloatField()
    carbs = models.FloatField()
    ethanol = models.FloatField(default=0.0)
    is_public = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    food_type = models.ForeignKey(
        FoodType, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)


class ProductCategory(models.Model):
    """Product categories (dairy, meat etc.)"""
    title = models.CharField(max_length=64)


class ProductBrand(models.Model):
    """Product manufacturers"""
    title = models.CharField(max_length=64)


class Product(Food):
    """Additional data for products"""
    net_grams = models.FloatField(blank=True)
    drained_grams = models.FloatField(blank=True)
    product_category = models.ForeignKey(
        ProductCategory, null=True, on_delete=models.SET_NULL)
    product_brand = models.ForeignKey(
        ProductBrand, null=True, on_delete=models.SET_NULL)


class RecipeCategory(models.Model):
    """Recipe categories (breakfast, lunch etc.)"""
    title = models.CharField(max_length=64)


class Recipe(Food):
    """Additional data for recipes"""
    directions = models.TextField()
    mass = models.FloatField()
    recipe_category = models.ForeignKey(
        RecipeCategory, null=True, on_delete=models.SET_NULL)


class RecipeProduct(models.Model):
    """A list of products for a recipe"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    mass = models.FloatField()

    class Meta:  # pylint: disable=too-few-public-methods
        """Recipe must not contain repeated products"""
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "product"], name="unique_recipe_product")
        ]


class Diary(models.Model):
    """Diary records for users"""
    mass = models.FloatField()
    calc_calories = models.FloatField()
    calc_proteins = models.FloatField()
    calc_fats = models.FloatField()
    calc_carbs = models.FloatField()
    calc_ethanol = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, null=True, on_delete=models.SET_NULL)
    food = models.ForeignKey(Food, null=True, on_delete=models.SET_NULL)
    added_date = models.DateTimeField()
