

from django.contrib import admin
from django.urls import path
from ai_text_generator import views


urlpatterns = [
    path('', views.generate_text, name='generate_text'),
    path('admin/', admin.site.urls),
]
