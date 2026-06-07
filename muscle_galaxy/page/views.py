from django.views.generic import TemplateView
from calendar import HTMLCalendar
from datetime import datetime
from .models import TrainingLog
from .utils import TrainingCalendar

# 全てのViewクラスを定義
class WelcomePageView(TemplateView): template_name = "page/welcome.html"
class LoginPageView(TemplateView): template_name = "page/login.html"
class DashBoardPageView(TemplateView): template_name = "page/dashboard.html"
class TimerPageView(TemplateView): template_name = "page/timer.html"
class MealPageView(TemplateView): template_name = "page/meal.html"
class RecipePageView(TemplateView): template_name = "page/recipe.html"
class ProfilePageView(TemplateView): template_name = "page/profile.html"
class EditPageView(TemplateView): template_name = "page/edit.html"
class StatisPageView(TemplateView): template_name = "page/statistics.html"

class CalendarPageView(TemplateView): 
    template_name = "page/calendar.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 今月のトレーニング記録をDBから取得
        logs = TrainingLog.objects.filter(date__month=datetime.now().month)
        
        # 自作した TrainingCalendar を使用
        cal = TrainingCalendar(logs)
        context['calendar_html'] = cal.formatmonth(datetime.now().year, datetime.now().month)
        return context

class DayDetailView(TemplateView):
    template_name = "page/day_detail.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target_date = self.kwargs['date'] # URLから日付を取得
        # その日の記録をDBから抽出
        context['logs'] = TrainingLog.objects.filter(date=target_date)
        context['date'] = target_date
        return context