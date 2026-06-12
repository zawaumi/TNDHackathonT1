from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AIPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='プラン名')),
                ('goal', models.CharField(blank=True, max_length=200, verbose_name='目標')),
                ('start_date', models.DateField(default=django.utils.timezone.localdate, verbose_name='開始日')),
                ('weeks', models.PositiveSmallIntegerField(default=4, verbose_name='週数')),
                ('status', models.CharField(choices=[('draft', '下書き'), ('active', '有効'), ('archived', 'アーカイブ')], default='draft', max_length=20, verbose_name='ステータス')),
                ('profile', models.JSONField(blank=True, default=dict, verbose_name='プロフィール入力')),
                ('plan', models.JSONField(blank=True, default=dict, verbose_name='AIプラン')),
                ('source_prompt', models.TextField(blank=True, verbose_name='生成リクエスト')),
                ('provider', models.CharField(default='mock', max_length=50, verbose_name='生成元')),
                ('model', models.CharField(blank=True, max_length=100, verbose_name='モデル')),
                ('mock_mode', models.BooleanField(default=True, verbose_name='モックモード')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ai_plans', to=settings.AUTH_USER_MODEL, verbose_name='ユーザー')),
            ],
            options={
                'verbose_name': 'AIプラン',
                'verbose_name_plural': 'AIプラン一覧',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='AIPlanRevision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_text', models.TextField(verbose_name='調整リクエスト')),
                ('previous_plan', models.JSONField(blank=True, default=dict, verbose_name='調整前プラン')),
                ('response_plan', models.JSONField(blank=True, default=dict, verbose_name='調整後プラン')),
                ('provider', models.CharField(default='mock', max_length=50, verbose_name='生成元')),
                ('model', models.CharField(blank=True, max_length=100, verbose_name='モデル')),
                ('mock_mode', models.BooleanField(default=True, verbose_name='モックモード')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='revisions', to='api.aiplan', verbose_name='AIプラン')),
            ],
            options={
                'verbose_name': 'AIプラン調整履歴',
                'verbose_name_plural': 'AIプラン調整履歴一覧',
                'ordering': ['-created_at'],
            },
        ),
    ]
