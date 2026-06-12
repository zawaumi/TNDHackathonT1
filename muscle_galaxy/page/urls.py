from django.urls import path
from .views import (
    WelcomePageView, LoginPageView, DashBoardPageView, 
    CalendarPageView, StatisPageView, TimerPageView, 
    MealPageView, RecipePageView, ProfilePageView, EditPageView,
    AIPlanPageView, DayDetailView, RegisterPageView, LogoutPageView,
    InitialInfoPageView, StartWorkoutRecordView,
)

urlpatterns = [
    path('', WelcomePageView.as_view(), name='welcome'),
    path('login/', LoginPageView.as_view(), name='login'),
    path('register/', RegisterPageView.as_view(), name='register'),
    path('initial-info/', InitialInfoPageView.as_view(), name='initial_info'),
    path('logout/', LogoutPageView.as_view(), name='logout'),
    path('home/', DashBoardPageView.as_view(), name='dashboard'),
    path('calendar/', CalendarPageView.as_view(), name='calendar'),
    path('statis/', StatisPageView.as_view(), name='statis'),
    path('timer/', TimerPageView.as_view(), name='timer'),
    path('calendar/meal/', MealPageView.as_view(), name='meal'),
    path('calendar/meal/recipe/', RecipePageView.as_view(), name='recipe'),
    path('profile/', ProfilePageView.as_view(), name='profile'),
    path('edit/', EditPageView.as_view(), name='edit'),
    path('ai-plan/', AIPlanPageView.as_view(), name='ai_plan'),
    path('timer/record/start/', StartWorkoutRecordView.as_view(), name='timer_record_start'),
    path('calendar/day/<str:date>/', DayDetailView.as_view(), name='day_detail'),
]
