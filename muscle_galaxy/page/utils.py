from calendar import HTMLCalendar

class TrainingCalendar(HTMLCalendar):
    def __init__(self, logs, year, month): # 年と月を受け取るように変更
        super().__init__()
        self.logs = logs
        self.year = year
        self.month = month

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="noday">&nbsp;</td>'
        
        # 記録チェック（フィルタリング条件も年・月に対応させる）
        day_logs = self.logs.filter(date__year=self.year, date__month=self.month, date__day=day)
        mark = "💪" if day_logs.exists() else ""
        
        # URLを動的に生成
        url = f"/calendar/day/{self.year}-{self.month:02d}-{day:02d}/"
        return f'<td class="{self.cssclasses[weekday]}"><a href="{url}">{day} {mark}</a></td>'