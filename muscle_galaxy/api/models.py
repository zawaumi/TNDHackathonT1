from django.db import models
from django.conf import settings
from django.utils import timezone


class AIPlan(models.Model):
    STATUS_CHOICES = [
        ('draft', '下書き'),
        ('active', '有効'),
        ('archived', 'アーカイブ'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_plans',
        verbose_name='ユーザー',
    )
    title = models.CharField('プラン名', max_length=200)
    goal = models.CharField('目標', max_length=200, blank=True)
    start_date = models.DateField('開始日', default=timezone.localdate)
    weeks = models.PositiveSmallIntegerField('週数', default=4)
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='draft')
    profile = models.JSONField('プロフィール入力', default=dict, blank=True)
    plan = models.JSONField('AIプラン', default=dict, blank=True)
    source_prompt = models.TextField('生成リクエスト', blank=True)
    provider = models.CharField('生成元', max_length=50, default='mock')
    model = models.CharField('モデル', max_length=100, blank=True)
    mock_mode = models.BooleanField('モックモード', default=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = 'AIプラン'
        verbose_name_plural = 'AIプラン一覧'
        ordering = ['-updated_at']

    def __str__(self):
        return self.title


class AIPlanRevision(models.Model):
    plan = models.ForeignKey(
        AIPlan,
        on_delete=models.CASCADE,
        related_name='revisions',
        verbose_name='AIプラン',
    )
    request_text = models.TextField('調整リクエスト')
    previous_plan = models.JSONField('調整前プラン', default=dict, blank=True)
    response_plan = models.JSONField('調整後プラン', default=dict, blank=True)
    provider = models.CharField('生成元', max_length=50, default='mock')
    model = models.CharField('モデル', max_length=100, blank=True)
    mock_mode = models.BooleanField('モックモード', default=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)

    class Meta:
        verbose_name = 'AIプラン調整履歴'
        verbose_name_plural = 'AIプラン調整履歴一覧'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.plan.title} - {self.created_at:%Y-%m-%d %H:%M}"
