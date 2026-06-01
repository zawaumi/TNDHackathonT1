from django.views.generic import TemplateView
# Create your views here.


class WelcomePageView(TemplateView):
    template_name = "page/welcome.html"


class LoginPageView(TemplateView):
    template_name = "page/login.html"


class DashBoardPageView(TemplateView):
    template_name = "page/dashboard.html"


class CalendarPageView(TemplateView):
    template_name = "page/calendar.html"


class StatisPageView(TemplateView):
    template_name = "page/statis.html"


class TimerPageView(TemplateView):
    template_name = "page/timer.html"


class MealPageView(TemplateView):
    template_name = "page/meal.html"


class RecipePageView(TemplateView):
    template_name = "page/recipe.html"


class ProfilePageView(TemplateView):
    template_name = "page/profile.html"


class EditPageView(TemplateView):
    template_name = "page/edit.html"