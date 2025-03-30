from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Root URL for agritech.views.home
    path('marketplace/', include('marketplace.urls')),  # Include marketplace URLs
]