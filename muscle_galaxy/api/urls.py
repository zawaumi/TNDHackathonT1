from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AIPlanViewSet, HealthView, RecipeImageView, get_training_data


router = DefaultRouter()
router.register('ai/plans', AIPlanViewSet, basename='ai-plan')

urlpatterns = [
    path('', include(router.urls)),
    path('health/', HealthView.as_view(), name='api-health'),
    path('training/<int:year>/<int:month>/', get_training_data, name='training-data'),
    path('ai/recipe-image/', RecipeImageView.as_view(), name='recipe-image'),
]
