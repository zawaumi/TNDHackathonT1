from django.contrib import admin

from .models import (
    Exercise,
    Workout,
    WorkoutSet,
    FoodCategory,
    FoodItem,
    Meal,
    MealItem,
    Recipe,
    RecipeIngredient,
    RecipeStep,
    MealRecipe,
    BodyMeasurement,
    DailyNutritionGoal,
)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'muscle_group', 'is_custom', 'created_at']
    list_filter = ['muscle_group', 'is_custom']
    search_fields = ['name', 'description']


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'duration_minutes', 'feeling', 'total_volume']
    list_filter = ['date', 'feeling']
    search_fields = ['user__username', 'notes']
    date_hierarchy = 'date'


@admin.register(WorkoutSet)
class WorkoutSetAdmin(admin.ModelAdmin):
    list_display = ['workout', 'exercise', 'weight', 'reps', 'sets', 'estimated_1rm']
    list_filter = ['exercise']
    search_fields = ['exercise__name', 'exercise_name']


@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'calories_per_100g', 'protein_per_100g', 'is_verified']
    list_filter = ['category', 'is_verified']
    search_fields = ['name']


class MealItemInline(admin.TabularInline):
    model = MealItem
    extra = 1


class MealRecipeInline(admin.TabularInline):
    model = MealRecipe
    extra = 1


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'meal_type', 'name', 'total_calories', 'total_protein']
    list_filter = ['meal_type', 'date']
    search_fields = ['user__username', 'name', 'notes']
    date_hierarchy = 'date'
    inlines = [MealItemInline, MealRecipeInline]


@admin.register(MealItem)
class MealItemAdmin(admin.ModelAdmin):
    list_display = ['meal', 'food_name', 'quantity', 'calories', 'protein']
    search_fields = ['food_name']


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeStepInline(admin.TabularInline):
    model = RecipeStep
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'total_time_minutes', 'difficulty', 'calories_per_serving', 'is_public']
    list_filter = ['difficulty', 'is_public', 'is_meal_prep']
    search_fields = ['title', 'description', 'tags']
    inlines = [RecipeIngredientInline, RecipeStepInline]


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'name', 'quantity', 'unit']
    search_fields = ['name']


@admin.register(RecipeStep)
class RecipeStepAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'step_number', 'instruction', 'duration_minutes']
    list_filter = ['recipe']


@admin.register(MealRecipe)
class MealRecipeAdmin(admin.ModelAdmin):
    list_display = ['meal', 'recipe', 'portion_size']


@admin.register(BodyMeasurement)
class BodyMeasurementAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'weight', 'body_fat_percentage', 'muscle_mass', 'bmi']
    list_filter = ['date']
    search_fields = ['user__username']
    date_hierarchy = 'date'


@admin.register(DailyNutritionGoal)
class DailyNutritionGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'calorie_goal', 'protein_goal']
    list_filter = ['date']
    search_fields = ['user__username']
    date_hierarchy = 'date'