from django.urls import path
from . import views

urlpatterns = [
    path('welcome/', views.welcome, name='welcome'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
path('test-db-connection/', views.test_db_connection, name='test_db_connection'),
]