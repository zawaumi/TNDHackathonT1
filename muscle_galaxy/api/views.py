import json
from copy import deepcopy

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from page.models import TrainingLog
from .models import AIPlan, AIPlanRevision
from .serializers import (
    AIPlanAdjustRequestSerializer,
    AIPlanGenerateRequestSerializer,
    AIPlanRevisionSerializer,
    AIPlanSerializer,
    RecipeImageRequestSerializer,
)
from .services import generate_monthly_plan, generate_recipe_image


@login_required
def get_training_data(request, year, month):
    logs = TrainingLog.objects.filter(user=request.user, date__year=year, date__month=month)
    data = list(logs.values('date', 'weight', 'workout_name'))
    return JsonResponse({'logs': data}, safe=False)


class HealthView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=OpenApiResponse(description='API health and AI mode'))
    def get(self, request):
        return Response({
            'status': 'ok',
            'ai_planner_mock_mode': settings.AI_PLANNER_MOCK_MODE,
            'openai_model': settings.OPENAI_MODEL,
            'image_generation_enabled': settings.OPENAI_ENABLE_IMAGE_GENERATION,
        })


class AIPlanViewSet(viewsets.ModelViewSet):
    serializer_class = AIPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return AIPlan.objects.none()
        if not self.request.user.is_authenticated:
            return AIPlan.objects.none()
        return AIPlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        request=AIPlanGenerateRequestSerializer,
        responses={status.HTTP_201_CREATED: AIPlanSerializer},
        description='プロフィール、身体データ、要望から4週間の食事・筋トレプランを生成して保存します。',
    )
    @action(detail=False, methods=['post'], url_path='generate')
    def generate(self, request):
        serializer = AIPlanGenerateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.validated_data
        result = generate_monthly_plan(request_data, request.user)
        plan_data = result['plan']
        profile = _json_safe({key: value for key, value in request_data.items() if key not in {'request_text', 'generate_images'}})
        ai_plan = AIPlan.objects.create(
            user=request.user,
            title=plan_data.get('plan_title', 'AIフィットネスプラン'),
            goal=request_data.get('goal', ''),
            start_date=request_data.get('start_date') or timezone.localdate(),
            weeks=plan_data.get('weeks', 4),
            status='draft',
            profile=profile,
            plan=plan_data,
            source_prompt=request_data.get('request_text', ''),
            provider=result['provider'],
            model=result['model'],
            mock_mode=result['mock_mode'],
        )
        return Response(AIPlanSerializer(ai_plan, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=AIPlanAdjustRequestSerializer,
        responses={status.HTTP_200_OK: AIPlanSerializer},
        description='保存済みAIプランに自然文の調整リクエストを反映します。',
    )
    @action(detail=True, methods=['post'], url_path='adjust')
    def adjust(self, request, pk=None):
        ai_plan = self.get_object()
        serializer = AIPlanAdjustRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.validated_data
        previous_plan = deepcopy(ai_plan.plan)
        result = generate_monthly_plan(request_data, request.user, existing_plan=previous_plan)
        plan_data = result['plan']
        ai_plan.plan = plan_data
        ai_plan.title = plan_data.get('plan_title', ai_plan.title)
        ai_plan.source_prompt = request_data['request_text']
        ai_plan.provider = result['provider']
        ai_plan.model = result['model']
        ai_plan.mock_mode = result['mock_mode']
        ai_plan.save()
        AIPlanRevision.objects.create(
            plan=ai_plan,
            request_text=request_data['request_text'],
            previous_plan=previous_plan,
            response_plan=plan_data,
            provider=result['provider'],
            model=result['model'],
            mock_mode=result['mock_mode'],
        )
        return Response(AIPlanSerializer(ai_plan, context={'request': request}).data)

    @extend_schema(
        responses={status.HTTP_200_OK: AIPlanRevisionSerializer(many=True)},
        description='保存済みAIプランの調整履歴を返します。',
    )
    @action(detail=True, methods=['get'], url_path='revisions')
    def revisions(self, request, pk=None):
        ai_plan = self.get_object()
        serializer = AIPlanRevisionSerializer(ai_plan.revisions.all(), many=True)
        return Response(serializer.data)


class RecipeImageView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=RecipeImageRequestSerializer,
        responses=OpenApiResponse(description='Generated recipe image URL or data URL'),
        description='レシピ画像を生成します。モックモードでは静的なプレースホルダーを返します。',
    )
    def post(self, request):
        serializer = RecipeImageRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = generate_recipe_image(
            serializer.validated_data['title'],
            serializer.validated_data['prompt'],
        )
        return Response(result)


def _json_safe(value):
    return json.loads(json.dumps(value, ensure_ascii=False, default=str))
