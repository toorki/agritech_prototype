from django.urls import path
from . import views

app_name = 'marketplace'
urlpatterns = [
    path('', views.home, name='home'),
    path('sponsorships/', views.sponsorship_list, name='sponsorship_list'),
    path('produce/', views.produce_list, name='produce_list'),
    path('profile/', views.user_profile, name='user_profile'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('farmer/dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
    path('sponsor/dashboard/', views.sponsor_dashboard, name='sponsor_dashboard'),
    path('buyer/dashboard/', views.buyer_dashboard, name='buyer_dashboard'),
]