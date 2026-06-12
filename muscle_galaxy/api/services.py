import copy
import json
from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import APIException


PLAN_SCHEMA = {
    'type': 'object',
    'properties': {
        'plan_title': {'type': 'string'},
        'summary': {'type': 'string'},
        'start_date': {'type': 'string'},
        'end_date': {'type': 'string'},
        'weeks': {'type': 'integer'},
        'daily_calorie_target': {'type': 'integer'},
        'macro_targets': {
            'type': 'object',
            'properties': {
                'protein_g': {'type': 'integer'},
                'fat_g': {'type': 'integer'},
                'carbs_g': {'type': 'integer'},
                'water_ml': {'type': 'integer'},
            },
            'required': ['protein_g', 'fat_g', 'carbs_g', 'water_ml'],
            'additionalProperties': False,
        },
        'weekly_training_focus': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'week': {'type': 'integer'},
                    'focus': {'type': 'string'},
                },
                'required': ['week', 'focus'],
                'additionalProperties': False,
            },
        },
        'days': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'day_number': {'type': 'integer'},
                    'date': {'type': 'string'},
                    'training': {
                        'type': 'object',
                        'properties': {
                            'title': {'type': 'string'},
                            'type': {'type': 'string'},
                            'duration_minutes': {'type': 'integer'},
                            'exercises': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'name': {'type': 'string'},
                                        'sets': {'type': 'integer'},
                                        'reps': {'type': 'string'},
                                        'intensity': {'type': 'string'},
                                        'notes': {'type': 'string'},
                                    },
                                    'required': ['name', 'sets', 'reps', 'intensity', 'notes'],
                                    'additionalProperties': False,
                                },
                            },
                            'recovery': {'type': 'string'},
                        },
                        'required': ['title', 'type', 'duration_minutes', 'exercises', 'recovery'],
                        'additionalProperties': False,
                    },
                    'meals': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'meal_type': {'type': 'string'},
                                'title': {'type': 'string'},
                                'calories': {'type': 'integer'},
                                'protein_g': {'type': 'integer'},
                                'carbs_g': {'type': 'integer'},
                                'fat_g': {'type': 'integer'},
                                'recipe': {
                                    'type': 'object',
                                    'properties': {
                                        'title': {'type': 'string'},
                                        'ingredients': {
                                            'type': 'array',
                                            'items': {
                                                'type': 'object',
                                                'properties': {
                                                    'name': {'type': 'string'},
                                                    'quantity': {'type': 'string'},
                                                },
                                                'required': ['name', 'quantity'],
                                                'additionalProperties': False,
                                            },
                                        },
                                        'steps': {
                                            'type': 'array',
                                            'items': {'type': 'string'},
                                        },
                                        'image_prompt': {'type': 'string'},
                                        'image_url': {'type': 'string'},
                                    },
                                    'required': ['title', 'ingredients', 'steps', 'image_prompt', 'image_url'],
                                    'additionalProperties': False,
                                },
                            },
                            'required': ['meal_type', 'title', 'calories', 'protein_g', 'carbs_g', 'fat_g', 'recipe'],
                            'additionalProperties': False,
                        },
                    },
                    'notes': {'type': 'string'},
                },
                'required': ['day_number', 'date', 'training', 'meals', 'notes'],
                'additionalProperties': False,
            },
        },
        'adjustment_notes': {
            'type': 'array',
            'items': {'type': 'string'},
        },
        'safety_notes': {
            'type': 'array',
            'items': {'type': 'string'},
        },
        'recipe_image_status': {
            'type': 'object',
            'properties': {
                'enabled': {'type': 'boolean'},
                'mode': {'type': 'string'},
                'limit': {'type': 'integer'},
            },
            'required': ['enabled', 'mode', 'limit'],
            'additionalProperties': False,
        },
    },
    'required': [
        'plan_title',
        'summary',
        'start_date',
        'end_date',
        'weeks',
        'daily_calorie_target',
        'macro_targets',
        'weekly_training_focus',
        'days',
        'adjustment_notes',
        'safety_notes',
        'recipe_image_status',
    ],
    'additionalProperties': False,
}


SYSTEM_PROMPT = (
    'あなたは筋力トレーニングと栄養計画の専門アシスタントです。'
    'ユーザーのプロフィール、体重、身長、目的、嗜好、制約をもとに、'
    '4週間分の食事と筋トレ計画をJSONスキーマ通りに作成します。'
    '医療診断はせず、安全上の注意と調整余地も必ず含めます。'
)


GOAL_LABELS = {
    'muscle_gain': '筋肥大',
    'fat_loss': '減量',
    'maintenance': '維持',
    'performance': '競技力向上',
}


WORKOUTS = [
    {
        'title': '上半身プッシュ',
        'type': 'strength',
        'exercises': ['ベンチプレス', 'インクラインダンベルプレス', 'ショルダープレス', 'ケーブルプレスダウン'],
    },
    {
        'title': '下半身',
        'type': 'strength',
        'exercises': ['スクワット', 'ルーマニアンデッドリフト', 'レッグプレス', 'カーフレイズ'],
    },
    {
        'title': '上半身プル',
        'type': 'strength',
        'exercises': ['ラットプルダウン', 'シーテッドロー', 'フェイスプル', 'ダンベルカール'],
    },
    {
        'title': '全身コンディショニング',
        'type': 'conditioning',
        'exercises': ['ゴブレットスクワット', 'プッシュアップ', 'ケトルベルスイング', 'プランク'],
    },
]


MEAL_TEMPLATES = [
    {
        'meal_type': 'breakfast',
        'title': 'オートミールとギリシャヨーグルト',
        'ingredients': [('オートミール', '60g'), ('ギリシャヨーグルト', '150g'), ('ベリー', '80g'), ('ナッツ', '10g')],
        'steps': ['オートミールを水か牛乳で温める', 'ヨーグルトとベリーをのせる', 'ナッツを散らして仕上げる'],
        'prompt': 'A clean fitness meal photo of oatmeal with Greek yogurt, berries, and nuts on a white table',
    },
    {
        'meal_type': 'lunch',
        'title': '鶏むね肉と玄米のボウル',
        'ingredients': [('鶏むね肉', '160g'), ('玄米', '180g'), ('ブロッコリー', '120g'), ('オリーブオイル', '小さじ1')],
        'steps': ['鶏むね肉に軽く塩を振って焼く', '玄米と野菜を器に盛る', '鶏むね肉をのせてオリーブオイルをかける'],
        'prompt': 'A simple high protein chicken breast and brown rice bowl with broccoli, bright white background',
    },
    {
        'meal_type': 'snack',
        'title': 'プロテインスムージー',
        'ingredients': [('プロテイン', '1杯'), ('バナナ', '1本'), ('低脂肪牛乳', '200ml'), ('氷', '適量')],
        'steps': ['材料をミキサーに入れる', 'なめらかになるまで混ぜる', 'トレーニング前後に飲む'],
        'prompt': 'A minimal protein smoothie in a clear glass with banana beside it, bright natural light',
    },
    {
        'meal_type': 'dinner',
        'title': '鮭と豆腐の高たんぱく定食',
        'ingredients': [('鮭', '150g'), ('豆腐', '120g'), ('雑穀米', '160g'), ('葉物野菜', '120g')],
        'steps': ['鮭を焼く', '豆腐と野菜を添える', '雑穀米と一緒に盛り付ける'],
        'prompt': 'A healthy Japanese salmon tofu dinner set on a white plate, clean fitness nutrition style',
    },
]


def generate_monthly_plan(request_data, user=None, existing_plan=None):
    mock_mode = settings.AI_PLANNER_MOCK_MODE
    if mock_mode:
        plan = _build_mock_plan(request_data, existing_plan)
        provider = 'mock'
        model = 'mock-fitness-planner-v1'
    else:
        plan = _build_openai_plan(request_data, existing_plan)
        provider = 'openai'
        model = settings.OPENAI_MODEL
    plan = attach_recipe_images(plan, request_data.get('generate_images', False), mock_mode)
    return {
        'plan': plan,
        'provider': provider,
        'model': model,
        'mock_mode': mock_mode,
    }


def generate_recipe_image(title, prompt):
    if settings.AI_PLANNER_MOCK_MODE or not settings.OPENAI_ENABLE_IMAGE_GENERATION:
        return {
            'title': title,
            'image_url': _mock_image_url(),
            'provider': 'mock',
            'model': 'mock-image-v1',
            'mock_mode': True,
        }
    return {
        'title': title,
        'image_url': _request_openai_image(prompt),
        'provider': 'openai',
        'model': settings.OPENAI_IMAGE_MODEL,
        'mock_mode': False,
    }


def attach_recipe_images(plan, generate_images, mock_mode):
    result = copy.deepcopy(plan)
    mode = 'disabled'
    if generate_images:
        mode = 'mock' if mock_mode or not settings.OPENAI_ENABLE_IMAGE_GENERATION else 'openai'
    result['recipe_image_status'] = {
        'enabled': bool(generate_images),
        'mode': mode,
        'limit': settings.OPENAI_IMAGE_GENERATION_LIMIT,
    }
    if not generate_images:
        return result
    generated = 0
    for day in result.get('days', []):
        for meal in day.get('meals', []):
            recipe = meal.get('recipe', {})
            if generated >= settings.OPENAI_IMAGE_GENERATION_LIMIT:
                continue
            if mode == 'openai':
                recipe['image_url'] = _request_openai_image(recipe.get('image_prompt', recipe.get('title', 'healthy meal')))
            else:
                recipe['image_url'] = _mock_image_url()
            generated += 1
    return result


def _build_openai_plan(request_data, existing_plan=None):
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        raise APIException('OPENAI_API_KEY が設定されていません。AI_PLANNER_MOCK_MODE=true でモック実行できます。')
    payload = {
        'model': settings.OPENAI_MODEL,
        'instructions': SYSTEM_PROMPT,
        'input': _build_prompt(request_data, existing_plan),
        'text': {
            'format': {
                'type': 'json_schema',
                'name': 'monthly_fitness_plan',
                'description': '4週間の筋トレ、食事、レシピ、画像プロンプトを含むプラン',
                'schema': PLAN_SCHEMA,
                'strict': True,
            }
        },
    }
    response_data = _post_openai('/responses', payload)
    raw_text = _extract_response_text(response_data)
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise APIException('OpenAIレスポンスをJSONとして解析できませんでした。') from exc


def _request_openai_image(prompt):
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        raise APIException('OPENAI_API_KEY が設定されていません。')
    payload = {
        'model': settings.OPENAI_IMAGE_MODEL,
        'prompt': prompt,
        'size': '1024x1024',
    }
    response_data = _post_openai('/images/generations', payload)
    items = response_data.get('data', [])
    if not items:
        raise APIException('画像生成レスポンスが空でした。')
    image_base64 = items[0].get('b64_json')
    if not image_base64:
        url = items[0].get('url')
        if url:
            return url
        raise APIException('画像URLまたはbase64データが見つかりませんでした。')
    return f'data:image/png;base64,{image_base64}'


def _post_openai(path, payload):
    base_url = settings.OPENAI_BASE_URL.rstrip('/')
    try:
        response = requests.post(
            f'{base_url}{path}',
            headers={
                'Authorization': f'Bearer {settings.OPENAI_API_KEY}',
                'Content-Type': 'application/json',
            },
            json=payload,
            timeout=settings.AI_PLANNER_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise APIException(f'OpenAI APIへの接続に失敗しました: {exc}') from exc
    if response.status_code >= 400:
        raise APIException(f'OpenAI APIエラー {response.status_code}: {response.text}')
    return response.json()


def _extract_response_text(response_data):
    output_text = response_data.get('output_text')
    if output_text:
        return output_text
    for item in response_data.get('output', []):
        for content in item.get('content', []):
            if content.get('type') in {'output_text', 'text'} and content.get('text'):
                return content['text']
    raise APIException('OpenAIレスポンスにテキスト出力がありませんでした。')


def _build_prompt(request_data, existing_plan=None):
    payload = {
        'request': request_data,
        'requirements': [
            '4週間分、28日間の食事とトレーニングを返す',
            '食事はレシピ、材料、手順、画像生成用プロンプトを含める',
            'ユーザーの追加リクエストを反映する',
            '過度な負荷や医療的断定を避ける',
        ],
    }
    if existing_plan:
        payload['current_plan'] = existing_plan
        payload['adjustment_mode'] = True
    return json.dumps(payload, ensure_ascii=False, default=str)


def _build_mock_plan(request_data, existing_plan=None):
    if existing_plan:
        return _adjust_mock_plan(request_data, existing_plan)
    start_date = request_data.get('start_date') or timezone.localdate()
    if isinstance(start_date, str):
        start_date = timezone.datetime.fromisoformat(start_date).date()
    goal = request_data.get('goal', 'muscle_gain')
    goal_label = GOAL_LABELS.get(goal, goal)
    targets = _calculate_targets(request_data)
    days = []
    training_indexes = _training_indexes(request_data.get('training_days_per_week', 4))
    for index in range(28):
        current_date = start_date + timedelta(days=index)
        training = _training_for_day(index, training_indexes, request_data)
        meals = _meals_for_day(index, targets)
        days.append({
            'day_number': index + 1,
            'date': current_date.isoformat(),
            'training': training,
            'meals': meals,
            'notes': '睡眠時間と疲労感を記録し、違和感があれば重量かセット数を下げます。',
        })
    return {
        'plan_title': f'{goal_label}向け4週間プラン',
        'summary': '入力値から推定した摂取目標と、週単位で負荷を上げるトレーニングを組み合わせたモックプランです。',
        'start_date': start_date.isoformat(),
        'end_date': (start_date + timedelta(days=27)).isoformat(),
        'weeks': 4,
        'daily_calorie_target': targets['calories'],
        'macro_targets': {
            'protein_g': targets['protein_g'],
            'fat_g': targets['fat_g'],
            'carbs_g': targets['carbs_g'],
            'water_ml': targets['water_ml'],
        },
        'weekly_training_focus': [
            {'week': 1, 'focus': 'フォーム確認と基準重量の設定'},
            {'week': 2, 'focus': '主要種目の重量または回数を少し伸ばす'},
            {'week': 3, 'focus': '補助種目のボリュームを増やす'},
            {'week': 4, 'focus': '疲労を確認しながら達成度を記録する'},
        ],
        'days': days,
        'adjustment_notes': [
            request_data.get('request_text') or '追加要望があれば調整APIで反映できます。',
        ],
        'safety_notes': [
            '痛みがある動作は中止し、必要に応じて専門家に相談してください。',
            '急激な体重変化を狙わず、週単位で摂取量と負荷を調整してください。',
        ],
        'recipe_image_status': {
            'enabled': False,
            'mode': 'disabled',
            'limit': settings.OPENAI_IMAGE_GENERATION_LIMIT,
        },
    }


def _adjust_mock_plan(request_data, existing_plan):
    plan = copy.deepcopy(existing_plan)
    request_text = request_data.get('request_text', '')
    notes = plan.get('adjustment_notes', [])
    notes.append(f'調整リクエスト: {request_text}')
    plan['adjustment_notes'] = notes
    plan['summary'] = f"{plan.get('summary', '')} 直近の要望を反映し、食事とトレーニングの運用メモを更新しました。".strip()
    for day in plan.get('days', [])[:7]:
        day['notes'] = f"{day.get('notes', '')} 調整内容: {request_text}".strip()
    return plan


def _calculate_targets(request_data):
    weight = float(request_data.get('weight_kg') or 70)
    height = float(request_data.get('height_cm') or 170)
    age = int(request_data.get('age') or 30)
    gender = request_data.get('gender') or 'other'
    if gender == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    elif gender == 'female':
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 78
    activity = 1.35 + min(int(request_data.get('training_days_per_week') or 4), 6) * 0.05
    calories = int(round(bmr * activity / 50) * 50)
    goal = request_data.get('goal', 'muscle_gain')
    if goal == 'muscle_gain':
        calories += 250
    elif goal == 'fat_loss':
        calories -= 300
    elif goal == 'performance':
        calories += 150
    calories = max(calories, 1400)
    protein = int(round(weight * 1.8))
    fat = int(round(weight * 0.8))
    carbs = max(int(round((calories - protein * 4 - fat * 9) / 4)), 100)
    water = int(round(weight * 35 / 100) * 100)
    return {
        'calories': calories,
        'protein_g': protein,
        'fat_g': fat,
        'carbs_g': carbs,
        'water_ml': water,
    }


def _training_indexes(days_per_week):
    count = max(1, min(int(days_per_week or 4), 7))
    indexes = []
    for item in range(count):
        indexes.append(round(item * 7 / count))
    return sorted(set(min(index, 6) for index in indexes))


def _training_for_day(index, training_indexes, request_data):
    weekday = index % 7
    if weekday not in training_indexes:
        return {
            'title': '回復日',
            'type': 'recovery',
            'duration_minutes': 20,
            'exercises': [
                {
                    'name': '軽いウォーキング',
                    'sets': 1,
                    'reps': '20分',
                    'intensity': '会話できる強度',
                    'notes': '血流を促して疲労を抜きます。',
                }
            ],
            'recovery': '入浴、ストレッチ、十分な睡眠を優先します。',
        }
    plan_index = training_indexes.index(weekday) % len(WORKOUTS)
    template = WORKOUTS[(index // 7 + plan_index) % len(WORKOUTS)]
    level = request_data.get('experience_level', 'beginner')
    sets = 3 if level == 'beginner' else 4
    duration = 45 if level == 'beginner' else 60
    exercises = [
        {
            'name': name,
            'sets': sets,
            'reps': '8-12回' if template['type'] == 'strength' else '30-45秒',
            'intensity': 'RPE 7前後',
            'notes': '最後の2回で余力が残る重量を選びます。',
        }
        for name in template['exercises']
    ]
    return {
        'title': template['title'],
        'type': template['type'],
        'duration_minutes': duration,
        'exercises': exercises,
        'recovery': 'トレーニング後にたんぱく質と炭水化物を補給します。',
    }


def _meals_for_day(index, targets):
    ratios = [0.25, 0.35, 0.12, 0.28]
    meals = []
    for meal_index, template in enumerate(MEAL_TEMPLATES):
        calories = int(round(targets['calories'] * ratios[meal_index]))
        protein = int(round(targets['protein_g'] * ratios[meal_index]))
        carbs = int(round(targets['carbs_g'] * ratios[meal_index]))
        fat = int(round(targets['fat_g'] * ratios[meal_index]))
        title = template['title']
        if index % 7 in {5, 6} and template['meal_type'] == 'dinner':
            title = '豚ヒレと温野菜の定食'
        meals.append({
            'meal_type': template['meal_type'],
            'title': title,
            'calories': calories,
            'protein_g': protein,
            'carbs_g': carbs,
            'fat_g': fat,
            'recipe': {
                'title': title,
                'ingredients': [
                    {'name': name, 'quantity': quantity}
                    for name, quantity in template['ingredients']
                ],
                'steps': template['steps'],
                'image_prompt': template['prompt'],
                'image_url': '',
            },
        })
    return meals


def _mock_image_url():
    static_url = settings.STATIC_URL
    if not static_url.startswith('/'):
        static_url = f'/{static_url}'
    return f'{static_url}img/recipe-placeholder.svg'
