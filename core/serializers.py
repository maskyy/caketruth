"""Serializers for core models"""
from datetime import datetime

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
        read_only_fields = ["is_public", "is_verified", "user"]

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
        food = FoodSerializer(
            instance.food_ptr, data=validated_data, partial=True)
        if food.is_valid(raise_exception=True):
            food.save()
        return super().update(instance, validated_data)


class ProductStaffSerializer(ProductSerializer):
    class Meta(ProductSerializer.Meta):
        read_only_fields = None


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "calories", "product_category", "product_brand"]


class RecipeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeCategory
        fields = "__all__"
        read_only_fields = ["id"]


class RecipeProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeProduct
        fields = ["product", "mass"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["product"] = ProductListSerializer(instance.product).data
        return data


class RecipeSerializer(serializers.ModelSerializer):
    mass = serializers.FloatField(min_value=1)
    products = RecipeProductSerializer(many=True)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "name",
            "calories",
            "proteins",
            "fats",
            "carbs",
            "ethanol",
            "is_public",
            "is_verified",
            "user",
            "directions",
            "mass",
            "recipe_category",
            "products"
        ]
        read_only_fields = [
            "calories",
            "proteins",
            "fats",
            "carbs",
            "ethanol",
            "is_public",
            "is_verified",
            "user"
        ]

    def _check_products(self, products):
        if len(products) < 2:
            raise serializers.ValidationError({"products": [
                "At least 2 products are required"
            ]})
        ids = [entry["product"].id for entry in products]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError({"products": [
                "Duplicate entries not allowed"
            ]})
        return products

    def _calculate_nutrients(self, products, mass):
        data = {
            "calories": 0,
            "proteins": 0,
            "fats": 0,
            "carbs": 0,
            "ethanol": 0,
        }
        for product in products:
            p = product["product"]
            m = product["mass"] / 100
            for k in data:
                data[k] += getattr(p, k) * m
        data = {k: round(v / (mass / 100), 2) for k, v in data.items()}
        return data

    def create(self, validated_data):
        products = self._check_products(validated_data.pop("products"))
        nutrients = self._calculate_nutrients(products, validated_data["mass"])
        validated_data |= nutrients

        validated_data["food_type"] = FoodType.objects.get(
            id=FoodTypes.RECIPE)
        food = FoodSerializer(data=validated_data)
        if not food.is_valid(raise_exception=True):
            return None

        recipe = Recipe(**validated_data)
        recipe.save()

        for product in products:
            RecipeProduct.objects.create(recipe=recipe, **product)
        return recipe

    def update(self, instance, validated_data):
        food = FoodSerializer(
            instance.food_ptr, data=validated_data, partial=True)
        if food.is_valid(raise_exception=True):
            food.save()

        mass = validated_data.get("mass", instance.mass)
        orig_products = [{"product": p.product, "mass": p.mass}
                         for p in instance.products.all()]
        products = validated_data.pop("products", orig_products)
        if mass != instance.mass or products != orig_products:
            products = self._check_products(products)
            nutrients = self._calculate_nutrients(products, mass)
            validated_data |= nutrients
            # recreate entries if they are changed
            if products != orig_products:
                RecipeProduct.objects.filter(recipe=instance).delete()
                for product in products:
                    RecipeProduct.objects.create(recipe=instance, **product)

        return super().update(instance, validated_data)


class RecipeStaffSerializer(RecipeSerializer):
    class Meta(RecipeSerializer.Meta):
        read_only_fields = ["calories", "proteins", "fats", "carbs", "ethanol"]


class RecipeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ["id", "name", "calories", "mass", "recipe_category"]


class DiarySerializer(serializers.ModelSerializer):
    mass = serializers.FloatField(min_value=0.01, max_value=10000)
    added_date = serializers.DateTimeField(
        required=False, default=datetime.now())

    class Meta:
        model = Diary
        fields = [
            "id",
            "mass",
            "calc_calories",
            "calc_proteins",
            "calc_fats",
            "calc_carbs",
            "calc_ethanol",
            "user",
            "meal",
            "food",
            "added_date"
        ]
        read_only_fields = [
            "calc_calories",
            "calc_proteins",
            "calc_fats",
            "calc_carbs",
            "calc_ethanol",
            "user"
        ]

    def _calculate_nutrients(self, food, mass):
        mass /= 100
        keys = ["calories", "proteins", "fats", "carbs", "ethanol"]
        result = {}
        for k in keys:
            result["calc_" + k] = round(getattr(food, k) * mass, 2)
        return result

    def create(self, validated_data):
        if validated_data["user"].id != validated_data["meal"].user.id:
            raise serializers.ValidationError({"meal": [
                "Cannot use other users' meals"
            ]})
        print(validated_data["user"].id, validated_data["meal"].user.id)
        food = validated_data["food"]
        mass = validated_data["mass"]
        validated_data |= self._calculate_nutrients(food, mass)
        record = Diary(**validated_data)
        record.save()

        return record

    def update(self, instance, validated_data):
        mass = validated_data.get("mass", instance.mass)
        food = validated_data.get("food", instance.food)
        if mass != instance.mass or food != instance.food:
            validated_data |= self._calculate_nutrients(instance.food, mass)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop("food")
        if instance.food.food_type.id == FoodTypes.PRODUCT:
            product = Product.objects.get(id=instance.food.id)
            data["product"] = ProductListSerializer(product).data
        else:
            recipe = Recipe.objects.get(id=instance.food.id)
            data["recipe"] = RecipeListSerializer(recipe).data
        return data
