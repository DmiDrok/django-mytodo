from django.core.paginator import Paginator

from .models import Do, Category


# Менюшка
menu = {
        'profile': [{'name_link': 'Мой профиль', 'name_path': 'profile'},
                    {'name_link': 'Выйти из аккаунта', 'name_path': 'logout'}],

        'system': [{'name_link': 'Авторизация', 'name_path': 'login'},
                   {'name_link': 'Регистрация', 'name_path': 'register'},],

        'pages': [{'name_link': 'Главная', 'name_path': 'index'},
                  {'name_link': 'Добавление задания', 'name_path': 'add_do'},],
        
        'other': [{'name_link': 'Выполненные задания', 'name_path': 'completed'},
                  {'name_link': 'Избранные задания', 'name_path': 'favourites'},
                  {'name_link': 'Обратная связь', 'name_path': 'feedback',}]
    }

# Миксин для очищения файла вьюх от кучи повторений
class DataMixin:
    def get_user_context(self, *args, **kwargs):
        context = kwargs
        context['menu'] = menu
        context['all_cats'] = Category.objects.order_by('id')
        
        self.page = self.request.GET.get('page') # Параметр page: активная страница из url-а
        # Если в GET-запросе присутствует параметр page
        # if self.page or self.request.path == '/':
        all_do = kwargs.get('all_do') # Берём запрос для формирования queryset для всех заданий
        if all_do:
            self.paginator = Paginator(all_do, 6) # Формируем локальное свойство с пагинатором
            self.page_obj = self.paginator.get_page(self.page)
            context['page_obj'] = self.page_obj
            context['all_do'] = self.page_obj.object_list


        return context