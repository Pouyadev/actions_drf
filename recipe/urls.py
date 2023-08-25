from django.urls import path
from . import views

app_name = 'recipe'

urlpatterns = [
    path('recipes/', views.RecipeListView.as_view(), name='recipe-list'),
    path('recipes/<int:recipe_id>/', views.RecipeDetailView.as_view(), name='recipe-detail'),
    path('tags/', views.TagListView.as_view(), name='tag-list'),
    path('tags/<int:tag_id>/', views.TagDetailView.as_view(), name='tag-detail'),
    path('ingredients/', views.IngredientListView.as_view(), name='ingredient-list'),
    path('ingredients/<int:ingredient_id>/', views.IngredientDetailView.as_view(), name='ingredient-detail'),
]
