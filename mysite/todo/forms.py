from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password

from captcha.fields import CaptchaField

from .models import Do, Profile


# Форма добавления задания
class AddDoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = False
        self.fields['photo'].required = False
        self.fields['category'].empty_label = None
        
        # self.fields['content'].widget = forms.Textarea(attrs={'cols': 30, 'rows': 10})
        # self.fields['category'].required = False
        # self.fields['category'].label = 'Категория'

    class Meta:
        model = Do
        fields = ['title', 'content', 'photo', 'category']


# Форма регистрации
class RegisterForm(forms.Form):
    username = forms.CharField(label="Логин", max_length=255, widget=forms.TextInput())
    email = forms.EmailField(label="Email", widget=forms.EmailInput())
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Повторите пароль", widget=forms.PasswordInput())

    # Валидатор для проверки того, что введённого username нет в таблице с пользователями
    def clean_username(self):
        username = self.cleaned_data.get('username')

        # Если такой пользователь уже есть в таблице User
        if User.objects.filter(username=username):
            raise forms.ValidationError('Такой пользователь уже зарегистрирован!') # Возвращаем ошибку валидации формы
        
        return username

    # Валидатор для проверки того, что введённого email нет в таблице с пользователями
    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Если такой email уже есть в таблице User
        if User.objects.filter(email=email):
            raise forms.ValidationError('Такая почта уже используется!') # Возвращаем ошибку валидации формы

        return email

    # Валидатор для проверки равенства паролей (возвращает hash при совпадении)
    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        
        # Если пароли не равны
        if password1 != password2:
            raise forms.ValidationError('Пароли не совпадают!') # Возвращаем ошибку валидации формы

        return password2


# Форма авторизации
class LoginForm(forms.Form):
    username = forms.CharField(label="Логин", max_length=255, widget=forms.TextInput())
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput())


# Форма изменения аватара и 'о себе' у пользователя
class ChangeAvatarAboutForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].label = 'Ваш аватар'
        self.fields['bio'].label = 'Расскажите о себе'
    
    class Meta:
        model = Profile
        fields = ['avatar', 'bio']


# Форма обратной связи
class SendMailForm(forms.Form):
    CATEGORY_CHOICES = [
        ("error_msg", "Сообщение об ошибке"),
        ("update_msg", "Предложение по улучшению"),
    ]

    category = forms.ChoiceField(label="Выберите категорию", choices=CATEGORY_CHOICES)
    content = forms.CharField(label="Содержимое письма", required=True, widget=forms.Textarea(attrs={'cols': 30, 'rows': 10}))
    captcha = CaptchaField()