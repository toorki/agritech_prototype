from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from agritech.views import CustomLoginView, AddProduceView

app_name = 'marketplace'  # Namespace for the app

router = DefaultRouter()
router.register(r'farmers', views.FarmerViewSet)
router.register(r'buyers', views.BuyerViewSet)
router.register(r'categories', views.ProduceCategoryViewSet)
router.register(r'produce', views.ProduceViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'ratings', views.RatingViewSet)
router.register(r'sponsorships', views.SponsorshipViewSet)
router.register(r'sponsorship-milestones', views.SponsorshipMilestoneViewSet)
router.register(r'sponsorship-payments', views.SponsorshipPaymentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.marketplace_home, name='marketplace_home'),
    path('farmers/', views.farmer_list, name='farmer_list'),
    path('farmers/<int:farmer_id>/', views.farmer_detail, name='farmer_detail'),
    path('produce/', views.produce_list, name='produce_list'),
    path('produce/<int:produce_id>/', views.produce_detail, name='produce_detail'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/update/', views.user_profile_update, name='user_profile_update'),  
    path('sponsorships/', views.sponsorship_list, name='sponsorship_list'),
    path('sponsorships/<int:sponsorship_id>/', views.sponsorship_detail, name='sponsorship_detail'),
    path('sponsorships/create/', views.create_sponsorship, name='create_sponsorship'),
    path('sponsorships/create-proposal/', views.create_sponsorship_proposal, name='create_sponsorship_proposal'),
    path('sponsorships/<int:sponsorship_id>/sponsor/', views.sponsor_project, name='sponsor_project'),
    path('milestones/<int:milestone_id>/update/', views.update_milestone, name='update_milestone'),
    path('sponsorships/<int:sponsorship_id>/complete/', views.complete_sponsorship, name='complete_sponsorship'),
    path('login/farmer/', CustomLoginView.as_view(), name='login_farmer'),
    path('login/sponsor/', CustomLoginView.as_view(), name='login_sponsor'),
    path('login/buyer/', CustomLoginView.as_view(), name='login_buyer'),
    path('logout/', views.logout_view, name='logout'),
    path('register/farmer/', views.register_farmer, name='register_farmer'),
    path('register/sponsor/', views.register_sponsor, name='register_sponsor'),
    path('register/buyer/', views.register_buyer, name='register_buyer'),
    path('farmer/dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
    path('farmer/add-produce/', AddProduceView.as_view(), name='add_produce'),
    path('sponsor/dashboard/', views.sponsor_dashboard, name='sponsor_dashboard'),
    path('buyer/dashboard/', views.buyer_dashboard, name='buyer_dashboard'),
    path('sponsorship/', views.sponsorship_view, name='sponsorship'),
    path('marketplace/', views.buyer_marketplace, name='buyer_marketplace'),
]