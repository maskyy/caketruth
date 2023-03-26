"""Serializers for core models"""
from rest_framework import serializers

from .models import *  # pylint: disable=wildcard-import,unused-wildcard-import


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = "__all__"
        read_only_fields = ["id", "user"]


class FoodTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodType
        fields = ["name"]
        read_only_fields = ["name"]


class FoodSerializer(serializers.ModelSerializer):
    calories = serializers.FloatField(min_value=0.0, max_value=900.0)
    proteins = serializers.FloatField(min_value=0.0, max_value=100.0)
    fats = serializers.FloatField(min_value=0.0, max_value=100.0)
    carbs = serializers.FloatField(min_value=0.0, max_value=100.0)
    ethanol = serializers.FloatField(
        required=False, default=0.0, min_value=0.0, max_value=100.0
    )

    class Meta:
        model = Food
        fields = "__all__"
        read_only_fields = ["id", "is_public", "is_verified",
                            "food_type", "user"]

    def create(self, validated_data):
        keys_to_round = ["calories", "proteins", "fats", "carbs", "ethanol"]
        for k in keys_to_round:
            validated_data[k] = round(validated_data[k], 2)
        food = Food(**validated_data)
        food.save()
        return food


class FoodStaffSerializer(FoodSerializer):
    class Meta(FoodSerializer.Meta):
        read_only_fields = ["id", "food_type", "user"]


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = "__all__"
        read_only_fields = ["id"]


class ProductBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBrand
        fields = "__all__"
        read_only_fields = ["id"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ["food_type"]

    def create(self, validated_data):
        validated_data["food_type"] = FoodType.objects.get(
            id=FoodTypes.PRODUCT)
        food = FoodSerializer(data=validated_data)
        if not food.is_valid(raise_exception=True):
            return None
        product = Product(**validated_data)
        product.food = food
        product.save()
        return product

    def update(self, instance, validated_data):
        food = FoodSerializer(instance.food, data=validated_data, partial=True)
        if food.is_valid(raise_exception=True):
            food.save()
        # TODO
        return instance



class RecipeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeCategory
        fields = "__all__"
        read_only_fields = ["id"]


class RecipeProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = RecipeProduct
        fields = "__all__"
        read_only_fields = ["id", "recipe", "product"]


class RecipeSerializer(serializers.ModelSerializer):
    recipe_category = RecipeCategorySerializer()
    products = RecipeProductSerializer(many=True)

    class Meta:
        model = Recipe
        fields = "__all__"
        read_only_fields = ["id"]


class DiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = "__all__"
        read_only_fields = ["user", "food"]
