from rest_framework import serializers
from core.models import Recipe, Tag, Ingredient
import magic

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['image']
        extra_kwargs = {'image': {'required': True}}

    def validate_image(self, value):
        # print(value)
        # file_type = magic.from_buffer(value.read(), mime=True)
        # print(file_type)
        # if not file_type.startswith('image/'):
        #     raise serializers.ValidationError("Only image files are allowed.")
        return value

class RecipeSerializer(serializers.ModelSerializer):
    tag = TagSerializer(many=True, required=False)
    ingredient = IngredientSerializer(many=True, required=False)

    """by default nested serializer is read_only (you can't create or edit tag base on tag field),
    in this case we want to create tag and recipe together"""

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'description',
                  'price', 'time_minute', 'link', 'tag', 'ingredient']
        read_only_fields = ['id']
        extra_kwargs = {'description': {'write_only': True}}

    def _get_or_create_tag(self, tags, recipe):
        user = self.context.get('request').user
        for tag in tags:
            obj, _ = Tag.objects.get_or_create(user=user, name=tag['name'])
            recipe.tag.add(obj)

    def _get_or_create_ingredient(self, ingredients, recipe):
        user = self.context.get('request').user
        for ingredient in ingredients:
            obj, _ = Ingredient.objects.get_or_create(user=user, name=ingredient['name'])
            recipe.ingredient.add(obj)

    def create(self, validated_data):
        tags = validated_data.pop('tag', [])
        ingredients = validated_data.pop('ingredient', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tag(tags, recipe)
        self._get_or_create_ingredient(ingredients, recipe)

        return recipe


    def update(self, instance, validated_data):
        tags = validated_data.pop('tag', None)
        if tags is not None:
            instance.tag.clear()
            self._get_or_create_tag(tags, instance)

        ingredients = validated_data.pop('ingredient', None)
        if ingredients is not None:
            instance.ingredient.clear()
            self._get_or_create_ingredient(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeLinkSerializer(RecipeSerializer):
    tag = serializers.HyperlinkedRelatedField(
        many=True, required=False, view_name='recipe:tag-detail',
        lookup_field='pk', lookup_url_kwarg='tag_id', queryset=Tag.objects.all()
    )
    ingredient = serializers.HyperlinkedRelatedField(
        many=True, required=False, view_name='recipe:ingredient-detail',
        lookup_field='pk', lookup_url_kwarg='ingredient_id', queryset=Ingredient.objects.all()
    )

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['image']


class RecipeDetailSerializer(RecipeSerializer):
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['image']
        read_only_fields = RecipeSerializer.Meta.read_only_fields + ['image']
        extra_kwargs = {'description': {'write_only': False}}
