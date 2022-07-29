from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.generic.base import TemplateView, View
from django.views.generic import ListView
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .forms import AddDoForm, RegisterForm, LoginForm, ChangeAvatarAboutForm, SendMailForm
from .models import Do, Category, Profile
from .utils import DataMixin

from datetime import datetime
from mysite import settings

import json


# Представление для главной страницы
class IndexView(DataMixin, LoginRequiredMixin, ListView):
    model = Do
    context_object_name = 'all_do'
    template_name = 'todo/index.html'
    http_method_names = ['get', 'post']

    # Изменение контекста в шаблоне
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        c_mixin = self.get_user_context(title='Главная страница', active_path='index', active_category='pages')
        context.update(c_mixin)

        return context

    # Формирование выборки из БД
    def get_queryset(self):
        return Do.objects.filter(is_completed=False, user=self.request.user).order_by('-create_at')

    # Действия при методе, которое не определено в http_method_names
    def http_method_not_allowed(self, request, *args, **kwargs):
        return JsonResponse(
            {'error': 'http method not allowed'}
        )


# Представление для страницы с добавлением задания
class AddDoView(DataMixin, LoginRequiredMixin, TemplateView):
    template_name = 'todo/add_do.html'
    http_method_names = ['get', 'post']

    # Изменение контекста в шаблоне
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_mixin = self.get_user_context(title='Добавление задания', active_path='add_do', active_category='pages')
        context.update(c_mixin)

        form = kwargs.get('form')
        context['form'] = form if form else AddDoForm()

        return context

    # Метод обработки post-запроса
    def post(self, request, *args, **kwargs):
        form = AddDoForm(request.POST, request.FILES)

        if form.is_valid():
            title = form.cleaned_data['title'] # Название задания введённое пользователем в форме
            if not Do.objects.filter(title=title): # Если такого задания в бд ещё нет - то всё нормально - сохраняем и уведомляем
                response = form.save(commit=False)
                response.user = request.user
                response.save()
                
                messages.add_message(request, messages.SUCCESS, 'Задание успешно добавлено.')
            else: # Если в бд уже есть такое задание - то уведомляем об этом пользователя
                form.add_error('title', 'Такое задание уже есть.')
        else: # Иначе - формируем сообщение об ошибке
            messages.add_message(request, messages.ERROR, 'Ошибка добавления задания.')

        return render(request, self.template_name, self.get_context_data(form=form))


# Представление для страницы задания
class DoView(DataMixin, LoginRequiredMixin, TemplateView):
    template_name = 'todo/do.html'

    # Изменение контекста в шаблоне
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        do = get_object_or_404(Do, slug=kwargs['slug'], user=self.request.user) # Задание из БД, если его нет - то вызываем ошибку 404
        c_mixin = self.get_user_context(title='Просмотр задания', active_category='cats', active_cat_slug=do.category.slug)
        context.update(c_mixin)

        context['do'] = do # Кладём задание в контекст

        return context


# Представление для страницы категории
class CategoryView(DataMixin, LoginRequiredMixin, ListView):
    model = Do
    context_object_name = 'all_do'
    template_name = 'todo/category.html'

    # Изменение контекста в шаблоне
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_mixin = self.get_user_context(title='Задания по категориям', active_cat_slug=self.kwargs['slug'], active_category='cats')
        context.update(c_mixin)

        # Если длина сформированной коллекции наших заданий больше 0 - то берём категорию из элемента с индексом 0
        if len(context['all_do']):
            context['category'] = context['all_do'][0].category.name
        else:
            context['category'] = Category.objects.get(slug=self.kwargs['slug'])

        return context

    # Формирование выборки из БД
    def get_queryset(self):
        return Do.objects.filter(category__slug=self.kwargs['slug'], is_completed=False, user=self.request.user).order_by('-create_at')


# Представление для страницы выполненных заданий
class CompletedView(DataMixin, LoginRequiredMixin, ListView):
    model = Do
    context_object_name = 'all_do'
    template_name = 'todo/completed_do.html'

    # Изменение контекста в шаблоне
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_mixin = self.get_user_context(title='Выполненные задания', active_path='completed', active_category='other')
        context.update(c_mixin)
        context['completed'] = 'Все выполненные задания'

        return context

    # Формирование выборки из БД
    def get_queryset(self):
        return Do.objects.filter(is_completed=True, user=self.request.user).order_by('-create_at')


# Представление для страницы избранных заданий
class FavouritesView(DataMixin, LoginRequiredMixin, ListView):
    model = Do
    context_object_name = 'all_do'
    template_name = 'todo/favourites.html'

    # Изменение контекста в шаблоне
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_mixin = self.get_user_context(title='Избранные задания', active_path='favourites', active_category='other')
        context.update(c_mixin)
        context['favourites'] = 'Все избранные задания'

        return context

    # Формирование выборки из БД
    def get_queryset(self):
        return Do.objects.filter(is_favourite=True, is_completed=False, user=self.request.user).order_by('-add_to_favourite_at')


# Представление для страницы регистрации с её обработкой   
class RegisterUserView(DataMixin, TemplateView):
    template_name = 'todo/register.html'

    # Изменение контекста в шаблоне
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_mixin = self.get_user_context(title='Регистрация', active_path='register', active_category='system')
        context.update(c_mixin)

        form = kwargs.get('form')
        context['form'] = form if form else RegisterForm()

        return context

    # Обработка формы
    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username'] # Имя пользователя
            email = form.cleaned_data['email'] # Логин пользователя
            password = form.cleaned_data['password2'] # Пароль пользователя (сразу хеш - см. forms.py)
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            ) # Создаём пользователя в основной БД с пользователями
            Profile.objects.create(user=user) # Создаём пользователя в дополнительной БД с пользователями
            messages.add_message(request, messages.SUCCESS, 'Успешно зарегистрирован!')
            
            return redirect('login') # Перенаправляем пользователя на страницу с авторизацией
        else:
            messages.add_message(request, messages.ERROR, 'Ошибка при регистрации.')

        return render(request, self.template_name, self.get_context_data(form=form))


# Представление для обработки авторизации пользователя
class LoginUserView(DataMixin, TemplateView):
    template_name = 'todo/login.html'

    # Изменение контекста в шаблоне
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_mixin = self.get_user_context(title='Авторизация пользователя', active_path='login', active_category='system')
        context.update(c_mixin)

        form = kwargs.get('form')
        context['form'] = form if form else LoginForm()

        return context

    # Обработка формы
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user_obj = User.objects.filter(username=username) # Пользователь из БД по введённому username
            if user_obj and check_password(password, user_obj[0].password): # Если пользователь был найден в БД и его пароль с введённым паролем из password совпадают
                user = authenticate(username=username, password=password)
                login(request, user)
                # messages.add_message(request, messages.SUCCESS, 'Успешно авторизован!')

                # if self.request.user.is_authenticated:
                return redirect('index')
            elif not user_obj: # Если пользователь не был найден (его нет на сайте) - предупреждаем пользователя об этом
                messages.add_message(request, messages.ERROR, 'Такого пользователя нет на сайте!')
            else:
                messages.add_message(request, messages.ERROR, 'Проверьте корректность введённых данных!')
        else:
            messages.add_message(request, messages.ERROR, 'Ошибка при авторизации.')

        return render(request, self.template_name, self.get_context_data(form=form))


# Представление для аккаунта пользователя
class ProfileUserView(DataMixin, LoginRequiredMixin, TemplateView):
    template_name = 'todo/profile.html'
    kwargs_to_context = {'title': 'Профиль пользователя', 'active_path': 'profile', 'active_category': 'system'}

    # Действия при get-запросе
    def get(self, request, *args, **kwargs):
        if request.user.username != kwargs.get('user_slug'):
            raise Http404
        
        return render(request, self.template_name, self.get_context_data(**self.kwargs_to_context, user_slug=kwargs['user_slug']))
        

    # Изменение контекста в шаблоне
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_mixin = self.get_user_context(**self.kwargs_to_context, user_slug=kwargs['user_slug'])
        context.update(c_mixin)

        # Получаем имя пользователя по слагу. Если пользователя нет - возвращается ошибка 404 страница не найдена.
        context['username'] = get_object_or_404(User, username=kwargs['user_slug'])
        context['profile'] = get_object_or_404(Profile, user__username=kwargs['user_slug'])
        form = kwargs.get('form')

        profile = Profile.objects.get(user=self.request.user)
        context['form'] = form if form else ChangeAvatarAboutForm()
        context['profile_bio'] = profile.bio

        return context

    # Обработка формы
    def post(self, request, *args, **kwargs):
        instance = Profile.objects.get(user=request.user)
        form = ChangeAvatarAboutForm(request.POST, request.FILES, instance=instance)

        if form.is_valid():
            # Profile.objects.get(user=request.user).delete()
            # Всё закоменченное - заменяет параметр instance у формы (это крайне полезная штука!)
            # response = form.save(commit=False)
            # response.user = request.user
            # response.save()

            form.save()
            return redirect('profile', user_slug=kwargs.get('user_slug'))

        return render(request, self.template_name, self.get_context_data(form=form, user_slug=kwargs['user_slug']))


# Представление для обратной связи
class FeedbackView(DataMixin, LoginRequiredMixin, TemplateView):
    template_name = 'todo/feedback.html'

    # Изменение контекста в шаблоне
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_mixin = self.get_user_context(title='Обратная связь', active_path='feedback', active_category='other')
        context.update(c_mixin)

        form = kwargs.get('form')
        context['form'] = form if form else SendMailForm()

        return context

    # Обработка формы
    def post(self, request, *args, **kwargs):
        form = SendMailForm(request.POST)

        # Если введённые данные прошли проверку - отсылаем письмо на почту
        if form.is_valid():
            content = form.cleaned_data['content']
            category = form.cleaned_data['category']
            html_message = render_to_string('todo/mail.html', context={'user': self.request.user, 'category': category, 'content': content}) # HTML который мы будем отправлять на почту
            plain_message = strip_tags(html_message) # Обычный текст из html без тегов

            mail = send_mail(
                            subject=f'Письмо Todo-шника [{category}]', 
                            message=plain_message, 
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=['drobkov155099@gmail.com'], 
                            fail_silently=False,
                            html_message=html_message,
                        )


            # Если письмо было отправлен
            if mail:
                messages.add_message(request, messages.SUCCESS, 'Сообщение успешно отправлено!') # Уведомляем пользователя об успешной отправке
            else: # Если при отправке произошла ошибка
                messages.add_message(request, messages.ERROR, 'Произошла ошибка при отправке письма!') # Уведомляем пользователя об ошибке при отправке

            return redirect('feedback')
        else:
            messages.add_message(request, messages.ERROR, 'Ошибка в введённых данных!')

        return render(request, self.template_name, self.get_context_data(form=form))


# Представление чтобы принять и обработать данные от xhr - запроса
class GetDataXHR(View):
    http_method_names = ['post'] # Разрешённые для обработки этим представлением методы

    # Обработка post - запроса
    def post(self, request, *args, **kwargs):
        data_completed = json.loads(request.body)

        # Добавление заданий в 'выполнено'
        for add_do in data_completed['add']:
            Do.objects.filter(title=add_do).update(is_completed=True)

        # Удаление невыполненных заданий
        for del_do in data_completed['del']:
            Do.objects.filter(title=del_do).delete()

        # Возвращение выполненных заданий в невыполненные
        for return_do in data_completed['return']:
            Do.objects.filter(title=return_do).update(is_completed=False, create_at=datetime.now())

        # Добавление заданий в избранное
        for favourite_do in data_completed['favourite']:
            Do.objects.filter(title=favourite_do).update(is_favourite=True, add_to_favourite_at=datetime.now())

        # Удаление заданий из избранного
        for favourite_del_do in data_completed['favourite_del']:
            Do.objects.filter(title=favourite_del_do).update(is_favourite=False)


        return JsonResponse({'status': 'success'})

        

    # Обработка не разрешённых методов
    def http_method_not_allowed(self, request, *args, **kwargs):
        return JsonResponse({'status': 'http method not allowed'})


# Функция выхода из системы
def logout_user(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS, 'Успешно вышли из аккаунта.')
    return redirect('login')


def test(request):
    return render(request, 'todo/mail.html', context={'category': 'Сообщение об ошибке', 'message': 'hihihihihhihih'})