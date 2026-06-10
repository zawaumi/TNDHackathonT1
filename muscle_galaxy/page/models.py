from django.db import models
from django.conf import settings
from django.utils import timezone


class Exercise(models.Model):
    name = models.CharField('エクササイズ名', max_length=100)
    muscle_group = models.CharField(
        '対象筋群',
        max_length=50,
        choices=[
            ('chest', '胸'),
            ('back', '背中'),
            ('shoulders', '肩'),
            ('biceps', '上腕二頭筋'),
            ('triceps', '上腕三頭筋'),
            ('legs', '脚'),
            ('glutes', '臀部'),
            ('abs', '腹筋'),
            ('full_body', '全身'),
            ('cardio', '有酸素'),
            ('other', 'その他'),
        ],
        default='other',
    )
    description = models.TextField('説明', null=True, blank=True)
    video_url = models.URLField('動画URL', null=True, blank=True)
    is_custom = models.BooleanField('カスタム種目', default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='created_exercises',
        verbose_name='作成者',
    )
    created_at = models.DateTimeField('作成日時', auto_now_add=True)

    class Meta:
        verbose_name = 'エクササイズ'
        verbose_name_plural = 'エクササイズ一覧'
        ordering = ['name']

    def __str__(self):
        return self.name


class Workout(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workouts',
        verbose_name='ユーザー',
    )
    date = models.DateField('トレーニング日', default=timezone.now)
    start_time = models.DateTimeField('開始時刻', null=True, blank=True)
    end_time = models.DateTimeField('終了時刻', null=True, blank=True)
    duration_minutes = models.IntegerField('トレーニング時間(分)', null=True, blank=True)
    notes = models.TextField('メモ', null=True, blank=True)
    feeling = models.CharField(
        '体調',
        max_length=20,
        choices=[
            ('great', '絶好調'),
            ('good', '良い'),
            ('normal', '普通'),
            ('bad', '悪い'),
            ('terrible', '最悪'),
        ],
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = 'ワークアウト'
        verbose_name_plural = 'ワークアウト一覧'
        ordering = ['-date', '-start_time']

    def total_volume(self):
        return sum(
            (s.weight or 0) * (s.reps or 0)
            for s in self.sets.all()
        )

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class WorkoutSet(models.Model):
    workout = models.ForeignKey(
        Workout,
        on_delete=models.CASCADE,
        related_name='sets',
        verbose_name='ワークアウト',
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.SET_NULL,
        null=True,
        related_name='workout_sets',
        verbose_name='エクササイズ',
    )
    exercise_name = models.CharField('エクササイズ名（自由入力）', max_length=100, null=True, blank=True)
    weight = models.FloatField('重量(kg)', null=True, blank=True)
    reps = models.IntegerField('レップ数', null=True, blank=True)
    sets = models.IntegerField('セット数', default=1)
    rpe = models.FloatField('RPE (1-10)', null=True, blank=True)
    rest_time_seconds = models.IntegerField('休憩時間(秒)', null=True, blank=True)
    is_warmup = models.BooleanField('ウォームアップ', default=False)
    sort_order = models.IntegerField('並び順', default=0)
    notes = models.TextField('メモ', null=True, blank=True)

    class Meta:
        verbose_name = 'ワークアウトセット'
        verbose_name_plural = 'ワークアウトセット一覧'
        ordering = ['workout', 'sort_order']

    def estimated_1rm(self):
        if self.weight and self.reps and self.reps > 0:
            return round(self.weight * (1 + self.reps / 30), 2)
        return None

    def volume(self):
        if self.weight and self.reps:
            return round(self.weight * self.reps * self.sets, 2)
        return 0

    def __str__(self):
        return f"{self.workout.date} - {self.exercise or self.exercise_name} - {self.weight}kg × {self.reps}reps × {self.sets}sets"


class FoodCategory(models.Model):
    name = models.CharField('カテゴリ名', max_length=100)
    description = models.TextField('説明', null=True, blank=True)

    class Meta:
        verbose_name = '食品カテゴリ'
        verbose_name_plural = '食品カテゴリ一覧'

    def __str__(self):
        return self.name


class FoodItem(models.Model):
    name = models.CharField('食品名', max_length=200)
    category = models.ForeignKey(
        FoodCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='food_items',
        verbose_name='カテゴリ',
    )
    calories_per_100g = models.FloatField('カロリー(kcal/100g)', null=True, blank=True)
    protein_per_100g = models.FloatField('タンパク質(g/100g)', null=True, blank=True)
    fat_per_100g = models.FloatField('脂質(g/100g)', null=True, blank=True)
    carbs_per_100g = models.FloatField('炭水化物(g/100g)', null=True, blank=True)
    fiber_per_100g = models.FloatField('食物繊維(g/100g)', null=True, blank=True)
    sugar_per_100g = models.FloatField('糖質(g/100g)', null=True, blank=True)
    sodium_per_100g = models.FloatField('ナトリウム(mg/100g)', null=True, blank=True)
    cholesterol_per_100g = models.FloatField('コレステロール(mg/100g)', null=True, blank=True)
    serving_unit = models.CharField('1食あたりの単位', max_length=50, default='g')
    serving_size = models.FloatField('1食あたりの標準量(g)', null=True, blank=True)
    image_url = models.URLField('画像URL', null=True, blank=True)
    is_verified = models.BooleanField('検証済み', default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_foods',
        verbose_name='作成者',
    )
    created_at = models.DateTimeField('作成日時', auto_now_add=True)

    class Meta:
        verbose_name = '食品'
        verbose_name_plural = '食品一覧'
        ordering = ['name']

    def __str__(self):
        return self.name


class Meal(models.Model):
    MEAL_TYPES = [
        ('breakfast', '朝食'),
        ('morning_snack', '午前のおやつ'),
        ('lunch', '昼食'),
        ('afternoon_snack', '午後のおやつ'),
        ('dinner', '夕食'),
        ('night_snack', '夜食'),
        ('pre_workout', 'トレ前'),
        ('post_workout', 'トレ後'),
        ('other', 'その他'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='meals',
        verbose_name='ユーザー',
    )
    date = models.DateField('食事日', default=timezone.now)
    meal_type = models.CharField(
        '食事タイプ',
        max_length=20,
        choices=MEAL_TYPES,
        default='breakfast',
    )
    meal_time = models.DateTimeField('食事時刻', null=True, blank=True)
    name = models.CharField('食事名', max_length=200, null=True, blank=True)
    notes = models.TextField('メモ', null=True, blank=True)
    image_url = models.URLField('食事画像URL', null=True, blank=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = '食事記録'
        verbose_name_plural = '食事記録一覧'
        ordering = ['-date', '-meal_time']

    def total_calories(self):
        return sum(item.calories or 0 for item in self.meal_items.all())

    def total_protein(self):
        return sum(item.protein or 0 for item in self.meal_items.all())

    def total_fat(self):
        return sum(item.fat or 0 for item in self.meal_items.all())

    def total_carbs(self):
        return sum(item.carbs or 0 for item in self.meal_items.all())

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.get_meal_type_display()}"


class MealItem(models.Model):
    meal = models.ForeignKey(
        Meal,
        on_delete=models.CASCADE,
        related_name='meal_items',
        verbose_name='食事',
    )
    food_item = models.ForeignKey(
        FoodItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meal_items',
        verbose_name='食品',
    )
    food_name = models.CharField('食品名（自由入力）', max_length=200, null=True, blank=True)
    quantity = models.FloatField('量(g)', default=100)
    unit = models.CharField('単位', max_length=50, default='g')
    calories = models.FloatField('カロリー(kcal)', null=True, blank=True)
    protein = models.FloatField('タンパク質(g)', null=True, blank=True)
    fat = models.FloatField('脂質(g)', null=True, blank=True)
    carbs = models.FloatField('炭水化物(g)', null=True, blank=True)
    fiber = models.FloatField('食物繊維(g)', null=True, blank=True)
    sugar = models.FloatField('糖質(g)', null=True, blank=True)
    sodium = models.FloatField('ナトリウム(mg)', null=True, blank=True)

    class Meta:
        verbose_name = '食事アイテム'
        verbose_name_plural = '食事アイテム一覧'

    def save(self, *args, **kwargs):
        if self.food_item and not self.food_name:
            self.food_name = self.food_item.name
            ratio = self.quantity / 100
            if self.calories is None and self.food_item.calories_per_100g:
                self.calories = round(self.food_item.calories_per_100g * ratio, 2)
            if self.protein is None and self.food_item.protein_per_100g:
                self.protein = round(self.food_item.protein_per_100g * ratio, 2)
            if self.fat is None and self.food_item.fat_per_100g:
                self.fat = round(self.food_item.fat_per_100g * ratio, 2)
            if self.carbs is None and self.food_item.carbs_per_100g:
                self.carbs = round(self.food_item.carbs_per_100g * ratio, 2)
            if self.fiber is None and self.food_item.fiber_per_100g:
                self.fiber = round(self.food_item.fiber_per_100g * ratio, 2)
            if self.sugar is None and self.food_item.sugar_per_100g:
                self.sugar = round(self.food_item.sugar_per_100g * ratio, 2)
            if self.sodium is None and self.food_item.sodium_per_100g:
                self.sodium = round(self.food_item.sodium_per_100g * ratio, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.food_name or '?'} - {self.quantity}{self.unit}"


class Recipe(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', '簡単'),
        ('medium', '普通'),
        ('hard', '難しい'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='作成者',
    )
    title = models.CharField('レシピ名', max_length=200)
    description = models.TextField('説明', null=True, blank=True)
    cooking_time_minutes = models.IntegerField('調理時間(分)', null=True, blank=True)
    prep_time_minutes = models.IntegerField('準備時間(分)', null=True, blank=True)
    total_time_minutes = models.IntegerField('合計時間(分)', null=True, blank=True)
    difficulty = models.CharField(
        '難易度',
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='easy',
    )
    servings = models.IntegerField('人数分', default=1)
    calories_per_serving = models.FloatField('1人前あたりカロリー(kcal)', null=True, blank=True)
    protein_per_serving = models.FloatField('1人前あたりタンパク質(g)', null=True, blank=True)
    fat_per_serving = models.FloatField('1人前あたり脂質(g)', null=True, blank=True)
    carbs_per_serving = models.FloatField('1人前あたり炭水化物(g)', null=True, blank=True)
    fiber_per_serving = models.FloatField('1人前あたり食物繊維(g)', null=True, blank=True)
    sugar_per_serving = models.FloatField('1人前あたり糖質(g)', null=True, blank=True)
    image_url = models.URLField('画像URL', null=True, blank=True)
    video_url = models.URLField('動画URL', null=True, blank=True)
    source_url = models.URLField('参照元URL', null=True, blank=True)
    is_public = models.BooleanField('公開設定', default=True)
    is_meal_prep = models.BooleanField('作り置き可能', default=False)
    tags = models.CharField('タグ', max_length=500, null=True, blank=True,
                           help_text='カンマ区切りでタグを入力')
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = 'レシピ'
        verbose_name_plural = 'レシピ一覧'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='レシピ',
    )
    food_item = models.ForeignKey(
        FoodItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recipe_ingredients',
        verbose_name='食品',
    )
    name = models.CharField('材料名', max_length=200)
    quantity = models.FloatField('量', null=True, blank=True)
    unit = models.CharField('単位', max_length=50, default='g')
    notes = models.CharField('備考', max_length=200, null=True, blank=True,
                            help_text='例: みじん切り、細切りなど')
    sort_order = models.IntegerField('並び順', default=0)
    is_optional = models.BooleanField('任意', default=False)

    class Meta:
        verbose_name = 'レシピ材料'
        verbose_name_plural = 'レシピ材料一覧'
        ordering = ['recipe', 'sort_order']

    def __str__(self):
        return f"{self.name}: {self.quantity}{self.unit}"


class RecipeStep(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='steps',
        verbose_name='レシピ',
    )
    step_number = models.IntegerField('手順番号')
    instruction = models.TextField('手順')
    duration_minutes = models.IntegerField('所要時間(分)', null=True, blank=True)
    image_url = models.URLField('手順画像URL', null=True, blank=True)
    tip = models.TextField('コツ・ポイント', null=True, blank=True)

    class Meta:
        verbose_name = 'レシピ手順'
        verbose_name_plural = 'レシピ手順一覧'
        ordering = ['recipe', 'step_number']

    def __str__(self):
        return f"{self.recipe.title} - Step {self.step_number}"


class MealRecipe(models.Model):
    meal = models.ForeignKey(
        Meal,
        on_delete=models.CASCADE,
        related_name='meal_recipes',
        verbose_name='食事',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        null=True,
        related_name='meal_recipes',
        verbose_name='レシピ',
    )
    portion_size = models.FloatField('摂取量(g)', null=True, blank=True)

    class Meta:
        verbose_name = '食事-レシピ紐付け'
        verbose_name_plural = '食事-レシピ紐付け一覧'

    def __str__(self):
        return f"{self.meal} - {self.recipe}"


class BodyMeasurement(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='body_measurements',
        verbose_name='ユーザー',
    )
    date = models.DateField('測定日', default=timezone.now)
    weight = models.FloatField('体重(kg)', null=True, blank=True)
    body_fat_percentage = models.FloatField('体脂肪率(%)', null=True, blank=True)
    muscle_mass = models.FloatField('筋肉量(kg)', null=True, blank=True)
    bmi = models.FloatField('BMI', null=True, blank=True)
    waist_cm = models.FloatField('ウエスト(cm)', null=True, blank=True)
    hip_cm = models.FloatField('ヒップ(cm)', null=True, blank=True)
    chest_cm = models.FloatField('バスト(cm)', null=True, blank=True)
    arm_cm = models.FloatField('腕周り(cm)', null=True, blank=True)
    thigh_cm = models.FloatField('太もも(cm)', null=True, blank=True)
    neck_cm = models.FloatField('首周り(cm)', null=True, blank=True)
    notes = models.TextField('メモ', null=True, blank=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)

    class Meta:
        verbose_name = '身体測定'
        verbose_name_plural = '身体測定一覧'
        ordering = ['-date']

    def save(self, *args, **kwargs):
        if self.weight and self.user.height:
            height_m = self.user.height / 100
            self.bmi = round(self.weight / (height_m ** 2), 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class DailyNutritionGoal(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nutrition_goals',
        verbose_name='ユーザー',
    )
    date = models.DateField('日付', default=timezone.now)
    calorie_goal = models.FloatField('目標カロリー(kcal)', null=True, blank=True)
    protein_goal = models.FloatField('目標タンパク質(g)', null=True, blank=True)
    fat_goal = models.FloatField('目標脂質(g)', null=True, blank=True)
    carbs_goal = models.FloatField('目標炭水化物(g)', null=True, blank=True)
    fiber_goal = models.FloatField('目標食物繊維(g)', null=True, blank=True)
    water_goal_ml = models.FloatField('目標水分量(ml)', null=True, blank=True)

    class Meta:
        verbose_name = '栄養目標'
        verbose_name_plural = '栄養目標一覧'
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class TrainingLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    workout_name = models.CharField(max_length=100)
    body_part = models.CharField(max_length=50)  # 胸, 背中, 脚など
    weight = models.FloatField()
    reps = models.IntegerField()
