from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from rest_framework import viewsets, permissions
from .models import (
    Farmer, Buyer, ProduceCategory, Produce, Order, Rating,
    Sponsorship, SponsorshipMilestone, SponsorshipPayment, UserProfile, Sponsor
)
from .serializers import (
    FarmerSerializer, BuyerSerializer, ProduceCategorySerializer,
    ProduceSerializer, OrderSerializer, RatingSerializer,
    SponsorshipSerializer, SponsorshipMilestoneSerializer, SponsorshipPaymentSerializer
)
import logging
import re

logger = logging.getLogger(__name__)

# API ViewSets (unchanged)
class FarmerViewSet(viewsets.ModelViewSet):
    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer
    permission_classes = [permissions.IsAuthenticated]

class BuyerViewSet(viewsets.ModelViewSet):
    queryset = Buyer.objects.all()
    serializer_class = BuyerSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProduceCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProduceCategory.objects.all()
    serializer_class = ProduceCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class ProduceViewSet(viewsets.ModelViewSet):
    queryset = Produce.objects.all()
    serializer_class = ProduceSerializer
    permission_classes = [permissions.IsAuthenticated]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

class SponsorshipViewSet(viewsets.ModelViewSet):
    queryset = Sponsorship.objects.all()
    serializer_class = SponsorshipSerializer
    permission_classes = [permissions.IsAuthenticated]

class SponsorshipMilestoneViewSet(viewsets.ModelViewSet):
    queryset = SponsorshipMilestone.objects.all()
    serializer_class = SponsorshipMilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]

class SponsorshipPaymentViewSet(viewsets.ModelViewSet):
    queryset = SponsorshipPayment.objects.all()
    serializer_class = SponsorshipPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

# Web UI Views
def marketplace_home(request):
    categories = ProduceCategory.objects.all()
    featured_produce = Produce.objects.filter(is_available=True).order_by('-created_at')[:6]
    top_farmers = Farmer.objects.order_by('-rating')[:5]
    if request.user.is_authenticated and hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'farmer':
        try:
            profile = UserProfile.objects.get(user=request.user)
            farmer = Farmer.objects.get(profile=profile)
            crops = Produce.objects.filter(farmer=farmer, is_available=True)
            buyers = Buyer.objects.all()  # Adjust queryset as needed
            farmers = Farmer.objects.exclude(profile=profile)  # Exclude current farmer
            context = {
                'categories': categories,
                'featured_produce': featured_produce,
                'top_farmers': top_farmers,
                'crops': crops,
                'buyers': buyers,
                'farmers': farmers,
            }
        except (UserProfile.DoesNotExist, Farmer.DoesNotExist):
            context = {
                'categories': categories,
                'featured_produce': featured_produce,
                'top_farmers': top_farmers,
            }
    else:
        context = {
            'categories': categories,
            'featured_produce': featured_produce,
            'top_farmers': top_farmers,
        }
    return render(request, 'marketplace/home.html', context)

@login_required
def sponsorship(request):
    if request.user.is_authenticated and request.user.userprofile.role == 'sponsor':
        try:
            profile = UserProfile.objects.get(user=request.user)
            sponsor = Sponsor.objects.get(profile=profile)
            active_sponsorships = Sponsorship.objects.filter(sponsor=sponsor, status='active')
            context = {
                'sponsor': sponsor,
                'active_sponsorships': active_sponsorships,
            }
            return render(request, 'marketplace/sponsorship.html', context)
        except (UserProfile.DoesNotExist, Sponsor.DoesNotExist):
            return redirect('marketplace:marketplace_home')
    return redirect('marketplace:marketplace_home')

# ... (rest of the views remain unchanged, including sponsor_dashboard, etc.)

# Ensure URLs are updated in agritech/urls.py
# Add this to agritech/urls.py if not present:
# path('sponsorship/', views.sponsorship, name='sponsorship'),