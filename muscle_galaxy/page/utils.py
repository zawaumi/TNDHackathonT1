from calendar import HTMLCalendar
from .models import TrainingLog

class TrainingCalendar(HTMLCalendar):
    def __init__(self, logs):
        super().__init__()
        self.logs = logs

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="noday">&nbsp;</td>'
        
        # その日の日付（例: 2026-06-05）に記録があるか確認
        day_logs = self.logs.filter(date__day=day)
        mark = "💪" if day_logs.exists() else ""
        
        # 詳細ページへのリンク付きセルを生成
        return f'<td class="{self.cssclasses[weekday]}"><a href="/calendar/day/2026-06-{day:02d}/">{day} {mark}</a></td>'