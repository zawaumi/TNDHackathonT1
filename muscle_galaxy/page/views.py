from datetime import timedelta

from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import FormView, TemplateView

from api.models import AIPlan
from .forms import InitialInfoForm, LoginForm, RegisterForm
from .models import BodyMeasurement, Meal, TrainingLog, Workout, WorkoutSet
from .utils import TrainingCalendar


class AppLoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            current_url = request.resolver_match.url_name if request.resolver_match else ''
            if current_url != 'initial_info' and needs_initial_info(request.user):
                return redirect('initial_info')
        return super().dispatch(request, *args, **kwargs)


class WelcomePageView(TemplateView):
    template_name = 'page/welcome.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('initial_info' if needs_initial_info(request.user) else 'dashboard')
        return super().dispatch(request, *args, **kwargs)


class LoginPageView(FormView):
    template_name = 'page/login.html'
    form_class = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('initial_info' if needs_initial_info(request.user) else 'dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('initial_info') if needs_initial_info(self.request.user) else reverse_lazy('dashboard')


class RegisterPageView(FormView):
    template_name = 'page/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('initial_info')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('initial_info' if needs_initial_info(request.user) else 'dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class LogoutPageView(View):
    def post(self, request):
        logout(request)
        return redirect('welcome')


class InitialInfoPageView(AppLoginRequiredMixin, FormView):
    template_name = 'page/initial_info.html'
    form_class = InitialInfoForm
    success_url = reverse_lazy('dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class DashBoardPageView(AppLoginRequiredMixin, TemplateView):
    template_name = 'page/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        latest_plan = latest_ai_plan(self.request.user)
        upcoming_days = plan_days_for_range(latest_plan, today, 5)
        today_plan = plan_day_for_date(latest_plan, today)
        week_hours = workout_hours(self.request.user, today - timedelta(days=today.weekday()), today + timedelta(days=1))
        last_week_hours = workout_hours(
            self.request.user,
            today - timedelta(days=today.weekday() + 7),
            today - timedelta(days=today.weekday()),
        )
        context.update({
            'today': today,
            'latest_plan': latest_plan,
            'upcoming_days': upcoming_days,
            'today_plan': today_plan,
            'progress': {
                'week_hours': week_hours,
                'week_delta': round(week_hours - last_week_hours, 1),
                'weight_delta': weight_delta(self.request.user),
                'completed_workouts': Workout.objects.filter(user=self.request.user).count(),
            },
            'notifications': notifications_for(self.request.user, today, latest_plan),
        })
        return context


class TimerPageView(AppLoginRequiredMixin, TemplateView):
    template_name = 'page/timer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today_plan = plan_day_for_date(latest_ai_plan(self.request.user), timezone.localdate())
        context['today_plan'] = today_plan
        context['timer_items'] = timer_items_from_plan(today_plan)
        return context


class MealPageView(AppLoginRequiredMixin, TemplateView):
    template_name = 'page/meal.html'


class RecipePageView(AppLoginRequiredMixin, TemplateView):
    template_name = 'page/recipe.html'


class ProfilePageView(AppLoginRequiredMixin, TemplateView):
    template_name = 'page/profile.html'


class EditPageView(AppLoginRequiredMixin, FormView):
    template_name = 'page/edit.html'
    form_class = InitialInfoForm
    success_url = reverse_lazy('profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class StatisPageView(AppLoginRequiredMixin, TemplateView):
    template_name = 'page/statis.html'


class AIPlanPageView(AppLoginRequiredMixin, TemplateView):
    template_name = 'page/ai_plan.html'


class CalendarPageView(AppLoginRequiredMixin, TemplateView):
    template_name = 'page/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        latest_plan = latest_ai_plan(self.request.user)
        logs = TrainingLog.objects.filter(user=self.request.user, date__year=today.year, date__month=today.month)
        meals = Meal.objects.filter(user=self.request.user, date__year=today.year, date__month=today.month)
        cal = TrainingCalendar(logs, month_plan_day_map(latest_plan, today.year, today.month), meal_day_map(meals))
        context['calendar_html'] = cal.formatmonth(today.year, today.month)
        return context


class DayDetailView(AppLoginRequiredMixin, TemplateView):
    template_name = 'page/day_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target_date = self.kwargs['date']
        context['logs'] = TrainingLog.objects.filter(user=self.request.user, date=target_date)
        context['meals'] = Meal.objects.filter(user=self.request.user, date=target_date)
        context['date'] = target_date
        context['plan_day'] = plan_day_for_date(latest_ai_plan(self.request.user), target_date)
        return context


class StartWorkoutRecordView(AppLoginRequiredMixin, View):
    def post(self, request):
        today_plan = plan_day_for_date(latest_ai_plan(request.user), timezone.localdate())
        training = (today_plan or {}).get('training', {})
        workout = Workout.objects.create(
            user=request.user,
            date=timezone.localdate(),
            start_time=timezone.now(),
            end_time=timezone.now(),
            duration_minutes=int(training.get('duration_minutes') or 0),
            notes=f"{training.get('title', '今日のトレーニング')} のタイマー完了から作成",
            feeling='normal',
        )
        for index, exercise in enumerate(training.get('exercises', []), start=1):
            WorkoutSet.objects.create(
                workout=workout,
                exercise_name=exercise.get('name') or '種目',
                sets=parse_int(exercise.get('sets'), 1),
                reps=parse_int(exercise.get('reps'), 10),
                sort_order=index,
                notes=exercise.get('notes', ''),
            )
        return JsonResponse({
            'id': workout.id,
            'title': training.get('title', '今日のトレーニング'),
            'duration_minutes': workout.duration_minutes,
            'sets_count': workout.sets.count(),
        })


def latest_ai_plan(user):
    return AIPlan.objects.filter(user=user).order_by('-updated_at').first()


def needs_initial_info(user):
    return not user.height or not user.weight


def plan_day_for_date(ai_plan, target_date):
    if not ai_plan:
        return fallback_plan_day(target_date)
    if isinstance(target_date, str):
        target_date = timezone.datetime.fromisoformat(target_date).date()
    for day in ai_plan.plan.get('days', []):
        if day.get('date') == target_date.isoformat():
            return day
    return fallback_plan_day(target_date)


def plan_days_for_range(ai_plan, start_date, days):
    return [plan_day_for_date(ai_plan, start_date + timedelta(days=offset)) for offset in range(days)]


def plan_day_map(ai_plan):
    if not ai_plan:
        return {}
    return {
        day.get('date'): day
        for day in ai_plan.plan.get('days', [])
        if day.get('date')
    }


def month_plan_day_map(ai_plan, year, month):
    result = plan_day_map(ai_plan)
    current = timezone.datetime(year, month, 1).date()
    while current.month == month:
        result.setdefault(current.isoformat(), fallback_plan_day(current))
        current += timedelta(days=1)
    return result


def meal_day_map(meals):
    result = {}
    for meal in meals:
        result.setdefault(meal.date.isoformat(), []).append(meal)
    return result


def fallback_plan_day(target_date):
    if isinstance(target_date, str):
        target_date = timezone.datetime.fromisoformat(target_date).date()
    return {
        'day_number': target_date.day,
        'date': target_date.isoformat(),
        'training': {
            'title': '全身ベーシック',
            'type': 'strength',
            'duration_minutes': 35,
            'exercises': [
                {'name': 'スクワット', 'sets': 3, 'reps': '10回', 'intensity': 'RPE 7', 'notes': 'フォームを優先します。'},
                {'name': 'プッシュアップ', 'sets': 3, 'reps': '8回', 'intensity': 'RPE 7', 'notes': '胸を床に近づけます。'},
                {'name': 'プランク', 'sets': 3, 'reps': '30秒', 'intensity': '安定重視', 'notes': '腰を反らさないようにします。'},
            ],
            'recovery': '各セットの間は60秒休みます。',
        },
        'meals': [
            {'meal_type': 'breakfast', 'title': 'オートミールとヨーグルト', 'calories': 420, 'protein_g': 28},
            {'meal_type': 'lunch', 'title': '鶏むね肉と玄米のボウル', 'calories': 650, 'protein_g': 45},
            {'meal_type': 'dinner', 'title': '鮭と野菜の定食', 'calories': 610, 'protein_g': 42},
        ],
        'notes': 'AIプランを作成すると、ここが個別メニューに置き換わります。',
    }


def timer_items_from_plan(plan_day):
    training = (plan_day or {}).get('training', {})
    items = []
    for exercise in training.get('exercises', []):
        sets = parse_int(exercise.get('sets'), 1)
        for set_number in range(1, sets + 1):
            items.append({
                'name': exercise.get('name') or '種目',
                'set_number': set_number,
                'sets': sets,
                'reps': exercise.get('reps') or '10回',
                'seconds': 60,
                'notes': exercise.get('notes') or '',
            })
    return items


def workout_hours(user, start_date, end_date):
    minutes = 0
    for workout in Workout.objects.filter(user=user, date__gte=start_date, date__lt=end_date):
        minutes += workout.duration_minutes or 0
    return round(minutes / 60, 1)


def weight_delta(user):
    measurements = list(BodyMeasurement.objects.filter(user=user).order_by('-date')[:2])
    if len(measurements) < 2 or measurements[0].weight is None or measurements[1].weight is None:
        return None
    return round(measurements[0].weight - measurements[1].weight, 1)


def notifications_for(user, today, ai_plan):
    today_plan = plan_day_for_date(ai_plan, today)
    training = today_plan.get('training', {})
    meals = today_plan.get('meals', [])
    return [
        {'title': '今日の筋トレ', 'body': training.get('title', 'メニューを確認してください。')},
        {'title': '食事記録', 'body': f"{len(meals)}件の食事メニューがあります。"},
        {'title': '進捗', 'body': 'タイマー完了後に記録が自動作成されます。'},
    ]


def parse_int(value, default):
    try:
        return int(str(value).split('-')[0].replace('回', '').strip())
    except (TypeError, ValueError):
        return default
