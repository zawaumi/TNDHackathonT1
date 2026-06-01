"""
URL configuration for muscle_galaxy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import WelcomePageView, CalendarPageView, DashBoardPageView, EditPageView, LoginPageView, MealPageView, ProfilePageView, RecipePageView, StatisPageView, TimerPageView


urlpatterns = [
    path('', WelcomePageView.as_view()),
    path('login/', LoginPageView.as_view()),
    path('home/', DashBoardPageView.as_view()),
    path('calendar/', CalendarPageView.as_view()),
    path('statis/', StatisPageView.as_view()),
    path('timer/', TimerPageView.as_view()),
    path('calendar/meal', MealPageView.as_view()),
    path('calendar/meal/recipe', RecipePageView.as_view()),
    path('profile/', ProfilePageView.as_view()),
    path('edit/', EditPageView.as_view()),
]
