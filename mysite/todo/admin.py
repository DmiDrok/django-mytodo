from django.contrib import admin

from .models import Do, Category, Profile


# Визуал для категорий в админке
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    list_display_links = ['name', 'slug']
    readonly_fields = ['slug']


# Визуал для заданий в админке
class DoAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'photo', 'category', 'is_completed', 'is_favourite', 'create_at', 'update_at']
    list_display_links = ['title', 'slug']
    readonly_fields = ['slug', 'create_at', 'update_at']
    list_editable = ['is_completed']


# Визуал для модели, дополняющей модель User
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'avatar']
    list_display_links = ['user']


# Регистрируем модели и визуал к ним
admin.site.register(Do, DoAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Profile, ProfileAdmin)