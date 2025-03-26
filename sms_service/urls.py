from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'messages', views.SMSMessageViewSet)
router.register(r'weather-alerts', views.WeatherAlertViewSet)
router.register(r'price-updates', views.PriceUpdateViewSet)
router.register(r'templates', views.SMSTemplateViewSet)
router.register(r'subscriptions', views.SMSSubscriptionViewSet)

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Web UI endpoints
    path('', views.sms_dashboard, name='sms_dashboard'),
    path('send/', views.send_sms, name='send_sms'),
    path('history/', views.sms_history, name='sms_history'),
    path('templates/', views.template_list, name='template_list'),
    path('templates/<int:template_id>/', views.template_detail, name='template_detail'),
    path('weather-alerts/', views.weather_alert_list, name='weather_alert_list'),
    path('price-updates/', views.price_update_list, name='price_update_list'),
    path('subscriptions/', views.subscription_management, name='subscription_management'),
]
