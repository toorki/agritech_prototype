from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'farmers', views.FarmerViewSet)
router.register(r'buyers', views.BuyerViewSet)
router.register(r'categories', views.ProduceCategoryViewSet)
router.register(r'produce', views.ProduceViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'ratings', views.RatingViewSet)

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Web UI endpoints
    path('', views.marketplace_home, name='marketplace_home'),
    path('farmers/', views.farmer_list, name='farmer_list'),
    path('farmers/<int:farmer_id>/', views.farmer_detail, name='farmer_detail'),
    path('produce/', views.produce_list, name='produce_list'),
    path('produce/<int:produce_id>/', views.produce_detail, name='produce_detail'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('profile/', views.user_profile, name='user_profile'),
    path('test/', views.test_view, name='test_view'),
]
