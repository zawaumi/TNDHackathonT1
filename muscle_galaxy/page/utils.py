from calendar import HTMLCalendar
from html import escape


class TrainingCalendar(HTMLCalendar):
    def __init__(self, logs, plan_days=None, meals=None):
        super().__init__()
        self.logs = logs
        self.plan_days = plan_days or {}
        self.meals = meals or {}
        self.year = None
        self.month = None

    def formatmonth(self, theyear, themonth, withyear=True):
        self.year = theyear
        self.month = themonth
        return super().formatmonth(theyear, themonth, withyear)

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="noday">&nbsp;</td>'

        date_key = f'{self.year}-{self.month:02d}-{day:02d}'
        day_logs = self.logs.filter(date__day=day)
        plan_day = self.plan_days.get(date_key, {})
        meals = self.meals.get(date_key, [])
        training = plan_day.get('training', {})
        meal_title = meals[0].name if meals else first_plan_meal_title(plan_day)
        log_mark = '<span class="pill">記録</span>' if day_logs.exists() else ''
        training_html = f'<span class="calendar-mini">{escape(training.get("title", ""))}</span>' if training else ''
        meal_html = f'<span class="calendar-mini">食事: {escape(meal_title)}</span>' if meal_title else ''
        return (
            f'<td class="{self.cssclasses[weekday]}">'
            f'<a class="calendar-day-link" href="/calendar/day/{date_key}/">'
            f'<span class="calendar-date">{day}</span>{log_mark}{training_html}{meal_html}'
            '</a></td>'
        )


def first_plan_meal_title(plan_day):
    meals = plan_day.get('meals') or []
    if not meals:
        return ''
    return meals[0].get('title', '')
