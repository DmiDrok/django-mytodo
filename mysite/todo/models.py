from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

from autoslug.fields import AutoSlugField


# Модель со всеми заданиями
class Do(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    slug = AutoSlugField(populate_from='title', db_index=True, unique=True, verbose_name='URL')
    content = models.TextField(blank=True, verbose_name='Описание')
    create_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    update_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    photo = models.ImageField(upload_to='photos/%Y/%m/%d', blank=True, verbose_name='Фотография')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name='Категория')
    is_completed = models.BooleanField(default=False, verbose_name='Выполнено')
    is_favourite = models.BooleanField(default=False, verbose_name='В избранном')
    add_to_favourite_at = models.DateTimeField(verbose_name='Дата добавления в избранное', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('do', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
        ordering = ['-id']


# Модель со всеми категориями
class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    slug = AutoSlugField(populate_from='name', db_index=True, unique=True, verbose_name='URL')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['id']


# Модель с расширенными данными о пользователе
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    bio = models.TextField(verbose_name='О пользователе')
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d', verbose_name='Аватар пользователя', blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи (расширенная таблица)'
        ordering = ['-id']
