from django.views.generic import TemplateView
from datetime import datetime
from .models import TrainingLog
from calendar import HTMLCalendar  # これをインポートする

# (ここに TrainingCalendar クラスを定義)
class TrainingCalendar(HTMLCalendar):
    def __init__(self, logs, year, month):
        super().__init__()
        self.logs = logs
        self.year = year
        self.month = month

    def formatday(self, day, weekday):
        if day == 0: return '<td class="noday">&nbsp;</td>'
        day_logs = self.logs.filter(date__day=day)
        mark = "💪" if day_logs.exists() else ""
        url = f"/calendar/day/{self.year}-{self.month:02d}-{day:02d}/"
        return f'<td class="{self.cssclasses[weekday]}"><a href="{url}">{day} {mark}</a></td>'

# (その下に各ページ用のビュークラスを定義)
class WelcomePageView(TemplateView): template_name = "page/welcome.html"
class LoginPageView(TemplateView): template_name = "page/login.html"
class DashBoardPageView(TemplateView): template_name = "page/dashboard.html"
class StatisPageView(TemplateView): template_name = "page/statis.html"
class TimerPageView(TemplateView): template_name = "page/timer.html"
class MealPageView(TemplateView): template_name = "page/meal.html"
class RecipePageView(TemplateView): template_name = "page/recipe.html"
class ProfilePageView(TemplateView): template_name = "page/profile.html"
class EditPageView(TemplateView): template_name = "page/edit.html"
class DayDetailView(TemplateView): template_name = "page/day_detail.html"

class CalendarPageView(TemplateView):
    template_name = "page/calendar.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.now()
        logs = TrainingLog.objects.filter(date__year=now.year, date__month=now.month)
        cal = TrainingCalendar(logs, now.year, now.month)
        context['calendar_html'] = cal.formatmonth(now.year, now.month)
        context['years'] = range(2021, 2033)
        context['months'] = ["January", "February", "March", "April", "May", "June", 
                             "July", "August", "September", "October", "November", "December"]
        return context