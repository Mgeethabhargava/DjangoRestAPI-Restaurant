from rest_framework import serializers
from . import models
import base64
from django.conf import settings
import os


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Restaurant
        fields = ['id', 'name', 'direction', 'phone']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ingredient
        fields = ['id', 'name']


class RecipeSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField('encode_thumbnail')
    ingredients = serializers.SerializerMethodField('get_ingredients')

    def encode_thumbnail(self, recipe):
        with open(os.path.join(settings.MEDIA_ROOT, recipe.thumbnail.name), "rb") as image_file:
            return base64.b64encode(image_file.read())

    def get_ingredients(self, recipe):
        try:
            recipe_ingredients = models.Ingredient.objects.filter(recipe__id=recipe.id)
            return IngredientSerializer(recipe_ingredients, many=True).data
        except models.Ingredient.DoesNotExist:
            return None

    def create(self, validated_data):

        restaurant = models.Restaurant.objects.get(pk=validated_data["restaurant_id"])
        validated_data["restaurant"] = restaurant
        recipe = models.Recipe.objects.create(**validated_data)

        if "ingredients" in validated_data:
            # Assign ingredients if they are present in the body
            ingredient_validated_data = validated_data.pop("ingredients")
            for ingredient in ingredient_validated_data:
                ingredient.recipe = recipe
            IngredientSerializer.create(validated_data=ingredient_validated_data)
        return recipe

    class Meta:
        model = models.Recipe
        fields = ['id', 'name', 'type', 'thumbnail', 'ingredients']
