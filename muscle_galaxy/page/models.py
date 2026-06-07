from django.db import models
from django.conf import settings

class TrainingLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    workout_name = models.CharField(max_length=100)
    body_part = models.CharField(max_length=50) # 胸, 背中, 脚など
    weight = models.FloatField()
    reps = models.IntegerField()