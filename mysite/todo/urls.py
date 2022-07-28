from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('add_do/', views.AddDoView.as_view(), name='add_do'),
    path('do_page/<slug:slug>', views.DoView.as_view(), name='do'),
    path('category/<slug:slug>', views.CategoryView.as_view(), name='category'),
    path('completed/', views.CompletedView.as_view(), name='completed'),
    path('favourites/', views.FavouritesView.as_view(), name='favourites'),
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('profile/<slug:user_slug>/', views.ProfileUserView.as_view(), name='profile'),
    path('logout/', views.logout_user, name='logout'),
    path('feedback/', views.FeedbackView.as_view(), name='feedback'),
    path('get_ajax/', views.GetDataXHR.as_view(), name='get_data_from_ajax'),
    path('test/', views.test, name='test'),
]