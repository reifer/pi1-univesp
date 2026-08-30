from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('bazar.urls')), # Encaminha a raiz para o arquivo urls.py do app bazar
]