# muscle_galaxy/api/views.py
from django.http import JsonResponse
from .models import TrainingLog

def get_training_data(request, year, month):
    logs = TrainingLog.objects.filter(date__year=year, date__month=month)
    data = list(logs.values('date', 'weight', 'workout_name'))
    return JsonResponse({'logs': data}, safe=False)