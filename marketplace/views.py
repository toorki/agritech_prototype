from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions
from .models import Farmer, Buyer, ProduceCategory, Produce, Order, Rating
from .serializers import (
    FarmerSerializer, BuyerSerializer, ProduceCategorySerializer,
    ProduceSerializer, OrderSerializer, RatingSerializer
)

def home(request):
    """Redirect to marketplace home"""
    return marketplace_home(request)

def test_view(request):
    from django.http import HttpResponse
    return HttpResponse("Test view works!")
# API ViewSets
class FarmerViewSet(viewsets.ModelViewSet):
    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class BuyerViewSet(viewsets.ModelViewSet):
    queryset = Buyer.objects.all()
    serializer_class = BuyerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ProduceCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProduceCategory.objects.all()
    serializer_class = ProduceCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ProduceViewSet(viewsets.ModelViewSet):
    queryset = Produce.objects.all()
    serializer_class = ProduceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Produce.objects.all()
        category = self.request.query_params.get('category', None)
        location = self.request.query_params.get('location', None)
        
        if category:
            queryset = queryset.filter(category__id=category)
        if location:
            queryset = queryset.filter(location__icontains=location)
            
        return queryset

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'buyer_profile'):
            return Order.objects.filter(buyer=user.buyer_profile)
        elif hasattr(user, 'farmer_profile'):
            return Order.objects.filter(produce__farmer=user.farmer_profile)
        return Order.objects.none()

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]


# Web UI Views
def marketplace_home(request):
    """Home page for the marketplace"""
    categories = ProduceCategory.objects.all()
    featured_produce = Produce.objects.filter(is_available=True).order_by('-created_at')[:6]
    top_farmers = Farmer.objects.order_by('-rating')[:5]
    
    context = {
        'categories': categories,
        'featured_produce': featured_produce,
        'top_farmers': top_farmers,
    }
    return render(request, 'marketplace/home.html', context)

def farmer_list(request):
    """List all farmers"""
    farmers = Farmer.objects.all().order_by('-rating')
    context = {'farmers': farmers}
    return render(request, 'marketplace/farmer_list.html', context)

def farmer_detail(request, farmer_id):
    """Detail view for a specific farmer"""
    farmer = get_object_or_404(Farmer, id=farmer_id)
    produce_items = Produce.objects.filter(farmer=farmer, is_available=True)
    ratings = Rating.objects.filter(farmer=farmer).order_by('-created_at')
    
    context = {
        'farmer': farmer,
        'produce_items': produce_items,
        'ratings': ratings,
    }
    return render(request, 'marketplace/farmer_detail.html', context)

def produce_list(request):
    """List all available produce"""
    categories = ProduceCategory.objects.all()
    selected_category = request.GET.get('category')
    location = request.GET.get('location')
    
    produce_items = Produce.objects.filter(is_available=True)
    
    if selected_category:
        produce_items = produce_items.filter(category__id=selected_category)
    if location:
        produce_items = produce_items.filter(location__icontains=location)
    
    context = {
        'produce_items': produce_items,
        'categories': categories,
        'selected_category': selected_category,
        'location': location,
    }
    return render(request, 'marketplace/produce_list.html', context)

def produce_detail(request, produce_id):
    """Detail view for a specific produce item"""
    produce = get_object_or_404(Produce, id=produce_id)
    related_items = Produce.objects.filter(
        category=produce.category, 
        is_available=True
    ).exclude(id=produce_id)[:4]
    
    context = {
        'produce': produce,
        'related_items': related_items,
    }
    return render(request, 'marketplace/produce_detail.html', context)

@login_required
def order_list(request):
    """List orders for the current user"""
    user = request.user
    if hasattr(user, 'buyer_profile'):
        orders = Order.objects.filter(buyer=user.buyer_profile)
    elif hasattr(user, 'farmer_profile'):
        orders = Order.objects.filter(produce__farmer=user.farmer_profile)
    else:
        orders = Order.objects.none()
    
    context = {'orders': orders}
    return render(request, 'marketplace/order_list.html', context)

@login_required
def order_detail(request, order_id):
    """Detail view for a specific order"""
    user = request.user
    if hasattr(user, 'buyer_profile'):
        order = get_object_or_404(Order, id=order_id, buyer=user.buyer_profile)
    elif hasattr(user, 'farmer_profile'):
        order = get_object_or_404(Order, id=order_id, produce__farmer=user.farmer_profile)
    else:
        return redirect('marketplace_home')
    
    context = {'order': order}
    return render(request, 'marketplace/order_detail.html', context)

@login_required
def user_profile(request):
    """User profile page"""
    user = request.user
    if hasattr(user, 'buyer_profile'):
        profile = user.buyer_profile
        orders = Order.objects.filter(buyer=profile)
        context = {
            'profile': profile,
            'orders': orders,
            'profile_type': 'buyer',
        }
    elif hasattr(user, 'farmer_profile'):
        profile = user.farmer_profile
        produce_items = Produce.objects.filter(farmer=profile)
        orders = Order.objects.filter(produce__farmer=profile)
        context = {
            'profile': profile,
            'produce_items': produce_items,
            'orders': orders,
            'profile_type': 'farmer',
        }
    else:
        return redirect('marketplace_home')
    
    
    return render(request, 'marketplace/user_profile.html', context)

home = marketplace_home