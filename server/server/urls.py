from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('jet/', include(('jet.urls', 'jet'), namespace='jet')),  # Django JET URLS
    path('admin/', admin.site.urls),
    path('api/server/', include('server.urls', namespace='server')),
]