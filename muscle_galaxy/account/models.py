from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    age = models.CharField('年齢', null=True, max_length=3)
    height = models.FloatField('身長(cm)', null=True, blank=True)
    weight = models.FloatField('体重(kg)', null=True, blank=True)
    gender = models.CharField(
        '性別',
        max_length=10,
        choices=[('male', '男性'), ('female', '女性'), ('other', 'その他')],
        null=True,
        blank=True,
    )
    birth_date = models.DateField('生年月日', null=True, blank=True)
    profile_image = models.URLField('プロフィール画像URL', null=True, blank=True)
    bio = models.TextField('自己紹介', null=True, blank=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー一覧'

    def __str__(self):
        return self.username


class LoginHistory(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_histories',
        verbose_name='ユーザー',
    )
    login_at = models.DateTimeField('ログイン日時', default=timezone.now)
    ip_address = models.GenericIPAddressField('IPアドレス', null=True, blank=True)
    user_agent = models.TextField('ユーザーエージェント', null=True, blank=True)
    device_type = models.CharField(
        'デバイス種別',
        max_length=50,
        choices=[
            ('web', 'Web'),
            ('ios', 'iOS'),
            ('android', 'Android'),
            ('other', 'その他'),
        ],
        default='web',
    )
    is_success = models.BooleanField('ログイン成功', default=True)

    class Meta:
        verbose_name = 'ログイン履歴'
        verbose_name_plural = 'ログイン履歴一覧'
        ordering = ['-login_at']

    def __str__(self):
        return f"{self.user.username} - {self.login_at.strftime('%Y-%m-%d %H:%M')}"