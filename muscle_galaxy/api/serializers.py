from rest_framework import serializers
from .models import AIPlan, AIPlanRevision


class AIPlanSerializer(serializers.ModelSerializer):
    revisions_count = serializers.SerializerMethodField()

    class Meta:
        model = AIPlan
        fields = [
            'id',
            'title',
            'goal',
            'start_date',
            'weeks',
            'status',
            'profile',
            'plan',
            'source_prompt',
            'provider',
            'model',
            'mock_mode',
            'revisions_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['provider', 'model', 'mock_mode', 'created_at', 'updated_at', 'revisions_count']

    def get_revisions_count(self, obj) -> int:
        return obj.revisions.count()


class AIPlanRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIPlanRevision
        fields = [
            'id',
            'plan',
            'request_text',
            'previous_plan',
            'response_plan',
            'provider',
            'model',
            'mock_mode',
            'created_at',
        ]
        read_only_fields = ['created_at']


class AIPlanGenerateRequestSerializer(serializers.Serializer):
    goal = serializers.ChoiceField(
        choices=[
            ('muscle_gain', '筋肥大'),
            ('fat_loss', '減量'),
            ('maintenance', '維持'),
            ('performance', '競技力向上'),
        ],
        default='muscle_gain',
    )
    goal_detail = serializers.CharField(required=False, allow_blank=True, default='')
    height_cm = serializers.FloatField(required=False, min_value=80, max_value=250)
    weight_kg = serializers.FloatField(required=False, min_value=25, max_value=250)
    age = serializers.IntegerField(required=False, min_value=13, max_value=100)
    gender = serializers.ChoiceField(
        choices=[
            ('male', '男性'),
            ('female', '女性'),
            ('other', 'その他'),
        ],
        required=False,
        default='other',
    )
    experience_level = serializers.ChoiceField(
        choices=[
            ('beginner', '初心者'),
            ('intermediate', '中級者'),
            ('advanced', '上級者'),
        ],
        default='beginner',
    )
    training_days_per_week = serializers.IntegerField(min_value=1, max_value=7, default=4)
    food_preferences = serializers.CharField(required=False, allow_blank=True, default='')
    allergies = serializers.CharField(required=False, allow_blank=True, default='')
    request_text = serializers.CharField(required=False, allow_blank=True, default='')
    start_date = serializers.DateField(required=False)
    generate_images = serializers.BooleanField(required=False, default=False)


class AIPlanAdjustRequestSerializer(serializers.Serializer):
    request_text = serializers.CharField()
    generate_images = serializers.BooleanField(required=False, default=False)


class RecipeImageRequestSerializer(serializers.Serializer):
    title = serializers.CharField()
    prompt = serializers.CharField()
