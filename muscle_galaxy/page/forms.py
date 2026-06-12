from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from account.models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='ユーザー名')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label='メールアドレス', required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class InitialInfoForm(forms.ModelForm):
    goal = forms.CharField(label='目標', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['height'].required = True
        self.fields['weight'].required = True

    class Meta:
        model = User
        fields = ['height', 'weight', 'gender', 'birth_date', 'bio']
        labels = {
            'height': '身長 cm',
            'weight': '体重 kg',
            'gender': '性別',
            'birth_date': '生年月日',
            'bio': 'メモ',
        }
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'トレーニング目標や生活リズムなど'}),
        }
