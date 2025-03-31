from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from rest_framework import viewsets, permissions
from .models import (Farmer, Buyer, ProduceCategory, Produce, Order, Rating,
    Sponsorship, SponsorshipMilestone, SponsorshipPayment
)
from .serializers import (
    FarmerSerializer, BuyerSerializer, ProduceCategorySerializer,
    ProduceSerializer, OrderSerializer, RatingSerializer,
    SponsorshipSerializer, SponsorshipMilestoneSerializer, SponsorshipPaymentSerializer
)
import logging  # Added for debugging

# Set up logging
logger = logging.getLogger(__name__)

class SponsorshipViewSet(viewsets.ModelViewSet):
    queryset = Sponsorship.objects.all()
    serializer_class = SponsorshipSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'farmer_profile'):
            return Sponsorship.objects.filter(farmer=user.farmer_profile)
        else:
            return Sponsorship.objects.filter(sponsor=user)
    
    def perform_create(self, serializer):
        if hasattr(self.request.user, 'farmer_profile'):
            serializer.save(farmer=self.request.user.farmer_profile)
        else:
            serializer.save(sponsor=self.request.user)

class SponsorshipMilestoneViewSet(viewsets.ModelViewSet):
    queryset = SponsorshipMilestone.objects.all()
    serializer_class = SponsorshipMilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        sponsorship_id = self.request.query_params.get('sponsorship', None)
        if sponsorship_id:
            return SponsorshipMilestone.objects.filter(sponsorship_id=sponsorship_id)
        return SponsorshipMilestone.objects.none()

class SponsorshipPaymentViewSet(viewsets.ModelViewSet):
    queryset = SponsorshipPayment.objects.all()
    serializer_class = SponsorshipPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        sponsorship_id = self.request.query_params.get('sponsorship', None)
        if sponsorship_id:
            return SponsorshipPayment.objects.filter(sponsorship_id=sponsorship_id)
        return SponsorshipPayment.objects.none()

# API ViewSets
def sponsorship_list(request):
    """List all sponsorship opportunities"""
    user = request.user
    
    if hasattr(user, 'farmer_profile'):
        # Farmers see their own sponsorship requests
        sponsorships = Sponsorship.objects.filter(farmer=user.farmer_profile)
        context = {
            'sponsorships': sponsorships,
            'user_type': 'farmer'
        }
    elif user.is_authenticated:
        # Sponsors see available sponsorship opportunities
        sponsorships = Sponsorship.objects.filter(status='pending')
        my_sponsorships = Sponsorship.objects.filter(sponsor=user)
        context = {
            'sponsorships': sponsorships,
            'my_sponsorships': my_sponsorships,
            'user_type': 'sponsor'
        }
    else:
        # Unauthenticated users see available sponsorship opportunities
        sponsorships = Sponsorship.objects.filter(status='pending')
        context = {
            'sponsorships': sponsorships,
            'user_type': 'guest'
        }
    
    return render(request, 'marketplace/sponsorship_list.html', context)

@login_required
def sponsorship_detail(request, sponsorship_id):
    """Detail view for a specific sponsorship"""
    sponsorship = get_object_or_404(Sponsorship, id=sponsorship_id)
    milestones = SponsorshipMilestone.objects.filter(sponsorship=sponsorship)
    payments = SponsorshipPayment.objects.filter(sponsorship=sponsorship)
    
    # Check if user is the farmer or sponsor
    is_farmer = hasattr(request.user, 'farmer_profile') and request.user.farmer_profile == sponsorship.farmer
    is_sponsor = request.user == sponsorship.sponsor
    
    context = {
        'sponsorship': sponsorship,
        'milestones': milestones,
        'payments': payments,
        'is_farmer': is_farmer,
        'is_sponsor': is_sponsor,
    }
    return render(request, 'marketplace/sponsorship_detail.html', context)

@login_required
def create_sponsorship(request):
    """Create a new sponsorship request (for farmers)"""
    if not hasattr(request.user, 'farmer_profile'):
        return redirect('marketplace:marketplace_home')
    
    if request.method == 'POST':
        # Process form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        amount_requested = request.POST.get('amount_requested')
        expected_yield = request.POST.get('expected_yield')
        expected_completion_date = request.POST.get('expected_completion_date')
        
        # Create sponsorship
        sponsorship = Sponsorship.objects.create(
            farmer=request.user.farmer_profile,
            title=title,
            description=description,
            amount_requested=amount_requested,
            expected_yield=expected_yield,
            expected_completion_date=expected_completion_date,
            status='pending'
        )
        
        # Create milestones
        milestone_titles = request.POST.getlist('milestone_title')
        milestone_descriptions = request.POST.getlist('milestone_description')
        milestone_due_dates = request.POST.getlist('milestone_due_date')
        
        for i in range(len(milestone_titles)):
            SponsorshipMilestone.objects.create(
                sponsorship=sponsorship,
                title=milestone_titles[i],
                description=milestone_descriptions[i],
                due_date=milestone_due_dates[i],
                status='pending'
            )
        
        return redirect('marketplace:sponsorship_detail', sponsorship_id=sponsorship.id)
    
    return render(request, 'marketplace/create_sponsorship.html')

@login_required
def sponsor_project(request, sponsorship_id):
    """Sponsor a project (for sponsors)"""
    sponsorship = get_object_or_404(Sponsorship, id=sponsorship_id, status='pending')
    
    if request.method == 'POST':
        # Process sponsorship
        sponsorship.sponsor = request.user
        sponsorship.status = 'active'
        sponsorship.save()
        
        # Create payment record
        SponsorshipPayment.objects.create(
            sponsorship=sponsorship,
            amount=sponsorship.amount_requested,
            payment_type='investment',
            transaction_id=request.POST.get('transaction_id', '')
        )
        
        return redirect('marketplace:sponsorship_detail', sponsorship_id=sponsorship.id)
    
    return render(request, 'marketplace/sponsor_project.html', {'sponsorship': sponsorship})

@login_required
def update_milestone(request, milestone_id):
    """Update milestone status (for agents/admins)"""
    milestone = get_object_or_404(SponsorshipMilestone, id=milestone_id)
    
    if not request.user.is_staff:
        return redirect('marketplace:sponsorship_detail', sponsorship_id=milestone.sponsorship.id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        milestone.status = status
        if status == 'completed':
            milestone.verify(request.user, notes)
        else:
            milestone.verification_notes = notes
            milestone.save()
        
        return redirect('marketplace:sponsorship_detail', sponsorship_id=milestone.sponsorship.id)
    
    return render(request, 'marketplace/update_milestone.html', {'milestone': milestone})

@login_required
def complete_sponsorship(request, sponsorship_id):
    """Complete a sponsorship and distribute returns"""
    sponsorship = get_object_or_404(Sponsorship, id=sponsorship_id, status='active')
    
    if not request.user.is_staff:
        return redirect('marketplace:sponsorship_detail', sponsorship_id=sponsorship.id)
    
    if request.method == 'POST':
        actual_yield = request.POST.get('actual_yield')
        selling_price = request.POST.get('selling_price')
        
        # Calculate returns
        total_revenue = float(actual_yield) * float(selling_price)
        investment = float(sponsorship.amount_requested)
        profit = total_revenue - investment
        
        if profit > 0:
            # 40% to sponsor, 40% to farmer, 20% to AgriTech
            sponsor_return = investment + (profit * 0.4)
            farmer_return = profit * 0.4
            agritech_fee = profit * 0.2
            
            # Create payment records
            SponsorshipPayment.objects.create(
                sponsorship=sponsorship,
                amount=sponsor_return,
                payment_type='return',
                transaction_id=request.POST.get('sponsor_transaction_id', '')
            )
            
            # Update sponsorship status
            sponsorship.status = 'completed'
            sponsorship.save()
        else:
            # Handle case where there's no profit
            sponsorship.status = 'completed'
            sponsorship.save()
        
        return redirect('marketplace:sponsorship_detail', sponsorship_id=sponsorship.id)
    
    return render(request, 'marketplace/complete_sponsorship.html', {'sponsorship': sponsorship})

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

def logout_view(request):
    logout(request)
    return redirect('marketplace:marketplace_home')

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
        return redirect('marketplace:marketplace_home')
    
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
        return redirect('marketplace:marketplace_home')
    
    return render(request, 'marketplace/user_profile.html', context)

@login_required
def add_produce(request):
    try:
        farmer = Farmer.objects.get(user=request.user)
    except Farmer.DoesNotExist:
        return redirect('marketplace:marketplace_home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        price_per_unit = request.POST.get('price_per_unit')
        unit = request.POST.get('unit')
        quantity = request.POST.get('quantity')
        location = request.POST.get('location')
        
        try:
            category = ProduceCategory.objects.get(id=category_id)
            Produce.objects.create(
                farmer=farmer,
                name=name,
                category=category,
                price_per_unit=price_per_unit,
                unit=unit,
                quantity=quantity,
                location=location,
                is_available=True
            )
            messages.success(request, 'Produce added successfully!')
            return redirect('marketplace:farmer_dashboard')
        except ProduceCategory.DoesNotExist:
            messages.error(request, 'Invalid category selected.')
        except Exception as e:
            messages.error(request, f'Error adding produce: {str(e)}')
    
    categories = ProduceCategory.objects.all()
    return render(request, 'marketplace/add_produce.html', {'categories': categories})

@login_required
def farmer_dashboard(request):
    if not hasattr(request.user, 'farmer_profile'):
        return redirect('marketplace:marketplace_home')
    farmer = request.user.farmer_profile
    produce_items = Produce.objects.filter(farmer=farmer)
    orders = Order.objects.filter(produce__farmer=farmer)
    sponsorships = Sponsorship.objects.filter(farmer=farmer)
    context = {
        'farmer': farmer,
        'produce_items': produce_items,
        'orders': orders,
        'sponsorships': sponsorships,
    }
    return render(request, 'marketplace/farmer_dashboard.html', context)

@login_required
def sponsor_dashboard(request):
    if not hasattr(request.user, 'sponsor'):
        return redirect('marketplace:marketplace_home')
    sponsorships = Sponsorship.objects.filter(sponsor=request.user)
    context = {
        'sponsorships': sponsorships,
    }
    return render(request, 'marketplace/sponsor_dashboard.html', context)

@login_required
def buyer_dashboard(request):
    if not hasattr(request.user, 'buyer_profile'):
        return redirect('marketplace:marketplace_home')
    buyer = request.user.buyer_profile
    orders = Order.objects.filter(buyer=buyer)
    context = {
        'buyer': buyer,
        'orders': orders,
    }
    return render(request, 'marketplace/buyer_dashboard.html', context)