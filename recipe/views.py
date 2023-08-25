from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes)
from core.models import Recipe, Tag, Ingredient
from .serializers import (
    RecipeSerializer, RecipeLinkSerializer, RecipeDetailSerializer,
    TagSerializer, IngredientSerializer, RecipeImageSerializer)


class PageNumber(PageNumberPagination):
    page_size = 6
    max_page_size = 24
    page_query_param = 'p'
    page_size_query_param = 'ps'


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                name='tags',
                type=OpenApiTypes.STR,
                default='10,2',
                required=False,
                description='Filtered of tags item'
            ),
            OpenApiParameter(
                name='ingredients',
                type=OpenApiTypes.STR,
                default='10,2',
                required=False,
                description='Filtered of ingredients item',
            ),
        ]
    )
)
class RecipeListView(generics.ListCreateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def _split_query_params(self, qp):
        return [int(i) for i in qp.split(',')]

    def get_queryset(self):
        queryset = self.queryset

        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')

        if tags:
            list_tag_ids = self._split_query_params(tags)
            queryset = queryset.filter(tag__id__in=list_tag_ids)
        if ingredients:
            list_ingredients_id = self._split_query_params(ingredients)
            queryset = queryset.filter(ingredient__id__in=list_ingredients_id)

        return queryset.filter(user=self.request.user).distinct()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeLinkSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecipeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeDetailSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    lookup_field = 'pk'
    lookup_url_kwarg = 'recipe_id'

    def get_object(self):
        return get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'), user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RecipeImageSerializer
        return self.serializer_class

    def post(self, request, *args, **kwargs):
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                name='assign_only',
                type=OpenApiTypes.INT, enum=[0, 1],
                required=False,
                description='Filter by assign item to recipes',
            )
        ]
    )
)
class TagListView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        queryset = self.queryset
        assign_only = bool(
            int(self.request.query_params.get('assign_only', 0)))

        if assign_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(user=self.request.user).distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    lookup_field = 'pk'
    lookup_url_kwarg = 'tag_id'

    def get_object(self):
        return get_object_or_404(Tag, user=self.request.user, id=self.kwargs.get('tag_id'))


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                name='assi_only',
                type=OpenApiTypes.INT, enum=[0, 1],
                required=False,
                description='Filter by assign item to recipes'
            )
        ]
    )
)
class IngredientListView(generics.ListCreateAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        queryset = self.queryset
        assign_only = bool(
            int(self.request.query_params.get('assign_only', 0)))

        if assign_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(user=self.request.user).distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class IngredientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    lookup_field = 'pk'
    lookup_url_kwarg = 'ingredient_id'

    def get_object(self):
        return get_object_or_404(
            Ingredient, user=self.request.user, id=self.kwargs.get('ingredient_id'))
