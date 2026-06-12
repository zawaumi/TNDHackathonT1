from django.utils import timezone

from api.models import AIPlan


def app_notifications(request):
    if not request.user.is_authenticated:
        return {'notifications': []}
    today = timezone.localdate().isoformat()
    ai_plan = AIPlan.objects.filter(user=request.user).order_by('-updated_at').first()
    today_plan = None
    if ai_plan:
        today_plan = next((day for day in ai_plan.plan.get('days', []) if day.get('date') == today), None)
    training_title = (today_plan or {}).get('training', {}).get('title', '今日のメニューを確認してください。')
    meals = (today_plan or {}).get('meals', [])
    return {
        'notifications': [
            {'title': '今日の筋トレ', 'body': training_title},
            {'title': '食事記録', 'body': f'{len(meals)}件の食事予定があります。'},
            {'title': 'タイマー', 'body': '完了時に筋トレ記録が自動で開始されます。'},
        ]
    }
