from django.urls import path
from server import views

app_name = 'server'
urlpatterns = [
    path('news', views.get_news),
    path('set_null_time', views.set_null_time)
]
