# marketplace/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, permissions
from .models import (
    Farmer, Buyer, ProduceCategory, Produce, Order, Rating,
    Sponsorship, SponsorshipMilestone, SponsorshipPayment, UserProfile, Sponsor, Notification
)
from .serializers import (
    FarmerSerializer, BuyerSerializer, ProduceCategorySerializer,
    ProduceSerializer, OrderSerializer, RatingSerializer,
    SponsorshipSerializer, SponsorshipMilestoneSerializer, SponsorshipPaymentSerializer
)
import logging
import re
from sms_service.utils import send_sms  # Correct import if utils.py is in sms_service/

logger = logging.getLogger(__name__)

# API ViewSets
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
            buyers = Buyer.objects.all()
            farmers = Farmer.objects.exclude(profile=profile)
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

def buyer_marketplace(request):
    if not request.user.is_authenticated or request.user.userprofile.role != 'buyer':
        return redirect('marketplace:marketplace_home')
    
    categories = ProduceCategory.objects.all()
    featured_produce = Produce.objects.filter(is_available=True).order_by('-created_at')[:6]
    top_farmers = Farmer.objects.order_by('-rating')[:5]
    
    try:
        profile = UserProfile.objects.get(user=request.user)
        buyer = Buyer.objects.get(profile=profile)
    except (UserProfile.DoesNotExist, Buyer.DoesNotExist):
        return redirect('marketplace:marketplace_home')
    
    produce_items = Produce.objects.filter(is_available=True)
    location_filter = request.GET.get('location', '')
    crop_filter = request.GET.get('crop', '')
    if location_filter:
        produce_items = produce_items.filter(location__icontains=location_filter)
    if crop_filter:
        produce_items = produce_items.filter(title__icontains=crop_filter).distinct()
    
    context = {
        'buyer': buyer,
        'categories': categories,
        'featured_produce': featured_produce,
        'top_farmers': top_farmers,
        'produce_items': produce_items,
        'location_filter': location_filter,
        'crop_filter': crop_filter,
    }
    return render(request, 'marketplace/buyer_marketplace.html', context)

def farmer_list(request):
    farmers = Farmer.objects.all().order_by('-rating')
    context = {'farmers': farmers}
    return render(request, 'marketplace/farmer_list.html', context)

def farmer_detail(request, farmer_id):
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
    produce = get_object_or_404(Produce, id=produce_id)
    related_items = Produce.objects.filter(category=produce.category, is_available=True).exclude(id=produce_id)[:4]
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
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
        if profile.role == 'buyer':
            orders = Order.objects.filter(buyer__profile=profile)
        elif profile.role == 'farmer':
            orders = Order.objects.filter(produce__farmer__profile=profile)
        else:
            orders = Order.objects.none()
    except UserProfile.DoesNotExist:
        orders = Order.objects.none()
    context = {'orders': orders}
    return render(request, 'marketplace/order_list.html', context)

@login_required
def order_detail(request, order_id):
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
        if profile.role == 'buyer':
            order = get_object_or_404(Order, id=order_id, buyer__profile=profile)
        elif profile.role == 'farmer':
            order = get_object_or_404(Order, id=order_id, produce__farmer__profile=profile)
        else:
            return redirect('marketplace:marketplace_home')
    except UserProfile.DoesNotExist:
        return redirect('marketplace:marketplace_home')
    context = {'order': order}
    return render(request, 'marketplace/order_detail.html', context)

@login_required
def user_profile(request):
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
        logger.debug(f"User {user.username} accessed profile with role: {profile.role}")

        if profile.role == 'buyer':
            buyer = Buyer.objects.get(profile=profile)
            orders = Order.objects.filter(buyer=buyer).order_by('-created_at')
            context = {'profile': buyer, 'orders': orders, 'profile_type': 'buyer'}
        elif profile.role == 'farmer':
            farmer = Farmer.objects.get(profile=profile)
            produce_items = Produce.objects.filter(farmer=farmer).order_by('-created_at')
            orders = Order.objects.filter(produce__farmer=farmer).order_by('-created_at')
            context = {'profile': farmer, 'produce_items': produce_items, 'orders': orders, 'profile_type': 'farmer'}
        elif profile.role == 'sponsor':
            sponsor = Sponsor.objects.get(profile=profile)
            context = {'profile': sponsor, 'profile_type': 'sponsor'}
        else:
            logger.warning(f"User {user.username} has an invalid role: {profile.role}")
            messages.error(request, "Invalid user role.")
            return redirect('marketplace:marketplace_home')

        return render(request, 'marketplace/user_profile.html', context)
    except UserProfile.DoesNotExist:
        logger.error(f"User {user.username} has no UserProfile.")
        messages.error(request, "Profile not found. Please complete your registration.")
        return redirect('marketplace:marketplace_home')
    except (Buyer.DoesNotExist, Farmer.DoesNotExist, Sponsor.DoesNotExist) as e:
        logger.error(f"Profile detail missing for user {user.username}: {str(e)}")
        messages.error(request, "Profile details are incomplete.")
        return redirect('marketplace:marketplace_home')

@login_required
def user_profile_update(request):
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
        logger.debug(f"User {user.username} accessing profile update with role: {profile.role}")

        if request.method == 'POST':
            if profile.role == 'buyer':
                buyer = Buyer.objects.get(profile=profile)
                buyer.phone_number = request.POST.get('phone_number')
                buyer.location = request.POST.get('location')
                buyer.save()
                messages.success(request, "Buyer profile updated successfully!")
                return redirect('marketplace:user_profile')
            elif profile.role == 'farmer':
                farmer = Farmer.objects.get(profile=profile)
                farmer.phone_number = request.POST.get('phone_number')
                farmer.location = request.POST.get('location')
                farmer.save()
                messages.success(request, "Farmer profile updated successfully!")
                return redirect('marketplace:user_profile')
            elif profile.role == 'sponsor':
                sponsor = Sponsor.objects.get(profile=profile)
                sponsor.phone_number = request.POST.get('phone_number')
                sponsor.organization = request.POST.get('organization')
                sponsor.save()
                messages.success(request, "Sponsor profile updated successfully!")
                return redirect('marketplace:user_profile')
            else:
                logger.warning(f"User {user.username} has an invalid role: {profile.role}")
                messages.error(request, "Invalid user role.")
                return redirect('marketplace:marketplace_home')
        
        if profile.role == 'buyer':
            profile_instance = Buyer.objects.get(profile=profile)
        elif profile.role == 'farmer':
            profile_instance = Farmer.objects.get(profile=profile)
        elif profile.role == 'sponsor':
            profile_instance = Sponsor.objects.get(profile=profile)
        else:
            return redirect('marketplace:marketplace_home')

        context = {
            'profile': profile_instance,
            'profile_type': profile.role,
        }
        return render(request, 'marketplace/user_profile_update.html', context)
    except UserProfile.DoesNotExist:
        logger.error(f"User {user.username} has no UserProfile.")
        messages.error(request, "Profile not found.")
        return redirect('marketplace:marketplace_home')
    except (Buyer.DoesNotExist, Farmer.DoesNotExist, Sponsor.DoesNotExist) as e:
        logger.error(f"Profile detail missing for user {user.username}: {str(e)}")
        messages.error(request, "Profile details are incomplete.")
        return redirect('marketplace:marketplace_home')

@login_required
def farmer_dashboard(request):
    try:
        profile = UserProfile.objects.get(user=request.user, role='farmer')
        farmer = Farmer.objects.get(profile=profile)
    except (UserProfile.DoesNotExist, Farmer.DoesNotExist):
        return redirect('marketplace:marketplace_home')
    
    crops = Produce.objects.filter(farmer=farmer, is_available=True)
    available_sponsorships = Sponsorship.objects.filter(status='pending', sponsor__isnull=True)
    orders = Order.objects.filter(produce__farmer=farmer, status__in=['pending', 'confirmed', 'paid'])
    unread_notifications_count = farmer.profile.user.notifications.filter(is_read=False).count()  # Precompute here

    context = {
        'farmer': farmer,
        'crops': crops,
        'available_sponsorships': available_sponsorships,
        'orders': orders,
        'unread_notifications_count': unread_notifications_count,  # Add to context
    }
    return render(request, 'marketplace/farmer_dashboard.html', context)

@login_required
def sponsor_dashboard(request):
    try:
        profile = UserProfile.objects.get(user=request.user, role='sponsor')
        sponsor = Sponsor.objects.get(profile=profile)
    except (UserProfile.DoesNotExist, Sponsor.DoesNotExist):
        return redirect('marketplace:marketplace_home')
    
    active_sponsorships = Sponsorship.objects.filter(sponsor=sponsor, status='active')
    farmers = Farmer.objects.all()
    location_filter = request.GET.get('location', '')
    crop_filter = request.GET.get('crop', '')
    if location_filter:
        farmers = farmers.filter(location__icontains=location_filter)
    if crop_filter:
        farmers = farmers.filter(produce__title__icontains=crop_filter).distinct()
    
    context = {
        'sponsor': sponsor,
        'active_sponsorships': active_sponsorships,
        'farmers': farmers,
        'location_filter': location_filter,
        'crop_filter': crop_filter,
    }
    return render(request, 'marketplace/sponsor_dashboard.html', context)

@login_required
def buyer_dashboard(request):
    try:
        profile = UserProfile.objects.get(user=request.user, role='buyer')
        buyer = Buyer.objects.get(profile=profile)
    except (UserProfile.DoesNotExist, Buyer.DoesNotExist):
        return redirect('marketplace:marketplace_home')
    
    active_orders = Order.objects.filter(buyer=buyer, status__in=['pending', 'confirmed', 'paid'])
    farmers = Farmer.objects.all()
    location_filter = request.GET.get('location', '')
    crop_filter = request.GET.get('crop', '')
    if location_filter:
        farmers = farmers.filter(location__icontains=location_filter)
    if crop_filter:
        farmers = farmers.filter(produce__title__icontains=crop_filter).distinct()
    
    context = {
        'buyer': buyer,
        'active_orders': active_orders,
        'farmers': farmers,
        'location_filter': location_filter,
        'crop_filter': crop_filter,
    }
    return render(request, 'marketplace/buyer_dashboard.html', context)

def sponsorship_list(request):
    user = request.user
    if not user.is_authenticated:
        sponsorships = Sponsorship.objects.filter(status='pending')
        context = {'sponsorships': sponsorships, 'user_type': 'guest'}
        return render(request, 'marketplace/sponsorship_list.html', context)
    
    try:
        profile = UserProfile.objects.get(user=user)
        if profile.role == 'farmer':
            sponsorships = Sponsorship.objects.filter(farmer__profile=profile)
            context = {'sponsorships': sponsorships, 'user_type': 'farmer'}
        elif profile.role == 'sponsor':
            sponsorships = Sponsorship.objects.filter(status='pending')
            my_sponsorships = Sponsorship.objects.filter(sponsor__profile=profile)
            context = {'sponsorships': sponsorships, 'my_sponsorships': my_sponsorships, 'user_type': 'sponsor'}
        else:
            sponsorships = Sponsorship.objects.filter(status='pending')
            context = {'sponsorships': sponsorships, 'user_type': 'guest'}
    except UserProfile.DoesNotExist:
        sponsorships = Sponsorship.objects.filter(status='pending')
        context = {'sponsorships': sponsorships, 'user_type': 'guest'}
    return render(request, 'marketplace/sponsorship_list.html', context)

@login_required
def sponsorship_detail(request, sponsorship_id):
    sponsorship = get_object_or_404(Sponsorship, id=sponsorship_id)
    milestones = SponsorshipMilestone.objects.filter(sponsorship=sponsorship)
    payments = SponsorshipPayment.objects.filter(sponsorship=sponsorship)
    try:
        profile = UserProfile.objects.get(user=request.user)
        is_farmer = profile.role == 'farmer' and sponsorship.farmer.profile == profile
        is_sponsor = profile.role == 'sponsor' and sponsorship.sponsor and sponsorship.sponsor.profile == profile
    except UserProfile.DoesNotExist:
        is_farmer = False
        is_sponsor = False
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
    try:
        profile = UserProfile.objects.get(user=request.user, role='farmer')
        farmer = Farmer.objects.get(profile=profile)
    except (UserProfile.DoesNotExist, Farmer.DoesNotExist):
        return redirect('marketplace:marketplace_home')
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        amount_requested = request.POST.get('amount_requested')
        expected_yield = request.POST.get('expected_yield')
        sponsorship = Sponsorship.objects.create(
            farmer=farmer,
            title=title,
            description=description,
            amount_requested=amount_requested,
            expected_yield=expected_yield,
            status='pending'
        )
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
    try:
        profile = UserProfile.objects.get(user=request.user, role='sponsor')
        sponsor = Sponsor.objects.get(profile=profile)
    except (UserProfile.DoesNotExist, Sponsor.DoesNotExist):
        return redirect('marketplace:marketplace_home')
    sponsorship = get_object_or_404(Sponsorship, id=sponsorship_id, status='pending')
    if request.method == 'POST':
        sponsorship.sponsor = sponsor
        sponsorship.status = 'active'
        sponsorship.save()
        SponsorshipPayment.objects.create(
            sponsorship=sponsorship,
            sponsor=sponsor,
            amount=sponsorship.amount_requested,
            payment_type='investment',
            transaction_id=request.POST.get('transaction_id', '')
        )
        return redirect('marketplace:sponsorship_detail', sponsorship_id=sponsorship.id)
    return render(request, 'marketplace/sponsor_project.html', {'sponsorship': sponsorship})

@login_required
def create_sponsorship_proposal(request):
    try:
        profile = UserProfile.objects.get(user=request.user, role='sponsor')
        sponsor = Sponsor.objects.get(profile=profile)
    except (UserProfile.DoesNotExist, Sponsor.DoesNotExist):
        return redirect('marketplace:marketplace_home')
    
    if request.method == 'POST':
        logger.debug("Processing POST request for sponsorship proposal")
        farmer_id = request.POST.get('farmer')
        title = request.POST.get('title')
        description = request.POST.get('description')
        amount_requested = request.POST.get('amount_requested')
        expected_yield = request.POST.get('expected_yield')
        expected_completion_date = request.POST.get('expected_completion_date')

        logger.debug(f"Form data: farmer_id={farmer_id}, title={title}, description={description}, "
                     f"amount={amount_requested}, yield={expected_yield}, date={expected_completion_date}")

        try:
            farmer = Farmer.objects.get(id=farmer_id)
            sponsorship = Sponsorship.objects.create(
                farmer=farmer,
                sponsor=sponsor,
                title=title,
                description=description,
                amount_requested=amount_requested,
                expected_yield=expected_yield,
                expected_completion_date=expected_completion_date,
                status='pending'
            )
            logger.debug(f"Sponsorship created with ID: {sponsorship.id}")

            messages.success(request, 'Sponsorship proposal created successfully!')

            # Platform Notification
            Notification.objects.create(
                user=farmer.profile.user,
                message=f"New sponsorship proposal '{title}' created by {sponsor.profile.user.get_full_name()}."
            )
            logger.debug(f"Platform notification created for user {farmer.profile.user.username}")
            messages.info(request, f"Notification sent to {farmer.profile.user.get_full_name()} on platform.")

            # Email Notification
            subject = f"New Sponsorship Proposal: {title}"
            message = f"Dear {farmer.profile.user.get_full_name()},\n\nA new sponsorship proposal has been created for you by {sponsor.profile.user.get_full_name()}.\nDetails:\n- Title: {title}\n- Amount Requested: {amount_requested} TND\n- Expected Yield: {expected_yield}\n- Expected Completion Date: {expected_completion_date}\n\nPlease log in to review and respond.\n\nBest,\nAgriTech Team"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [farmer.profile.user.email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            logger.debug(f"Email sent to {farmer.profile.user.email}")

            # SMS Notification
            sms_message = f"New sponsorship proposal '{title}' from {sponsor.profile.user.get_full_name()}. Log in to review. AgriTech"
            send_sms(farmer.phone_number, sms_message)
            logger.debug(f"SMS sent to {farmer.phone_number}")

            return redirect('marketplace:sponsorship_detail', sponsorship_id=sponsorship.id)
        except Farmer.DoesNotExist:
            logger.error(f"Invalid farmer ID: {farmer_id}")
            messages.error(request, 'Invalid farmer selected.')
        except ValueError as e:
            logger.error(f"Value error creating sponsorship: {str(e)}")
            messages.error(request, f"Invalid data provided: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating sponsorship: {str(e)}")
            messages.error(request, f'Error creating sponsorship: {str(e)}')
    
    farmers = Farmer.objects.all()
    yield_multiplier = 2.0
    context = {
        'farmers': farmers,
        'yield_multiplier': yield_multiplier,
    }
    return render(request, 'marketplace/create_sponsorship_proposal.html', context)

@login_required
def update_milestone(request, milestone_id):
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
    sponsorship = get_object_or_404(Sponsorship, id=sponsorship_id, status='active')
    if not request.user.is_staff:
        return redirect('marketplace:sponsorship_detail', sponsorship_id=sponsorship.id)
    if request.method == 'POST':
        actual_yield = request.POST.get('actual_yield')
        selling_price = request.POST.get('selling_price')
        total_revenue = float(actual_yield) * float(selling_price)
        investment = float(sponsorship.amount_requested)
        profit = total_revenue - investment
        if profit > 0:
            sponsor_return = investment + (profit * 0.4)
            farmer_return = profit * 0.4
            agritech_fee = profit * 0.2
            SponsorshipPayment.objects.create(
                sponsorship=sponsorship,
                sponsor=sponsorship.sponsor,
                amount=sponsor_return,
                payment_type='return',
                transaction_id=request.POST.get('sponsor_transaction_id', '')
            )
            sponsorship.status = 'completed'
            sponsorship.save()
        else:
            sponsorship.status = 'completed'
            sponsorship.save()
        return redirect('marketplace:sponsorship_detail', sponsorship_id=sponsorship.id)
    return render(request, 'marketplace/complete_sponsorship.html', {'sponsorship': sponsorship})

# Registration Views
def register_farmer(request):
    if request.method == 'POST':
        family_name = request.POST.get('family_name')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        farm_address = request.POST.get('farm_address')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'marketplace/register_farmer.html')
        if not re.match(r'^\d{8,}$', phone):
            messages.error(request, 'Phone number must be at least 8 digits.')
            return render(request, 'marketplace/register_farmer.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'marketplace/register_farmer.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'marketplace/register_farmer.html')

        user = User.objects.create_user(username=username, email=email, password=password1, first_name=name, last_name=family_name)
        user_profile = UserProfile.objects.create(user=user, role='farmer')
        Farmer.objects.create(
            profile=user_profile,
            phone_number=phone,
            location=farm_address
        )
        login(request, user)
        messages.success(request, 'Farmer account created successfully!')
        return redirect('marketplace:farmer_dashboard')
    return render(request, 'marketplace/register_farmer.html')

def register_sponsor(request):
    if request.method == 'POST':
        family_name = request.POST.get('family_name')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        home_address = request.POST.get('home_address')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'marketplace/register_sponsor.html')
        if not re.match(r'^\d{8,}$', phone):
            messages.error(request, 'Phone number must be at least 8 digits.')
            return render(request, 'marketplace/register_sponsor.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'marketplace/register_sponsor.html')

        user = User.objects.create_user(username=username, password=password1, first_name=name, last_name=family_name)
        user_profile = UserProfile.objects.create(user=user, role='sponsor')
        Sponsor.objects.create(
            profile=user_profile,
            phone_number=phone,
            organization=home_address
        )
        login(request, user)
        messages.success(request, 'Sponsor account created successfully!')
        return redirect('marketplace:sponsorship')
    return render(request, 'marketplace/register_sponsor.html')

def register_buyer(request):
    if request.method == 'POST':
        family_name = request.POST.get('family_name')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        home_address = request.POST.get('home_address')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'marketplace/register_buyer.html')
        if not re.match(r'^\d{8,}$', phone):
            messages.error(request, 'Phone number must be at least 8 digits.')
            return render(request, 'marketplace/register_buyer.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'marketplace/register_buyer.html')

        user = User.objects.create_user(username=username, password=password1, first_name=name, last_name=family_name)
        user_profile = UserProfile.objects.create(user=user, role='buyer')
        Buyer.objects.create(
            profile=user_profile,
            phone_number=phone,
            location=home_address
        )
        login(request, user)
        messages.success(request, 'Buyer account created successfully!')
        return redirect('marketplace:buyer_dashboard')
    return render(request, 'marketplace/register_buyer.html')

@login_required
def sponsorship_view(request):
    try:
        profile = UserProfile.objects.get(user=request.user, role='sponsor')
        sponsor = Sponsor.objects.get(profile=profile)
    except (UserProfile.DoesNotExist, Sponsor.DoesNotExist):
        return redirect('marketplace:marketplace_home')
    
    active_sponsorships = Sponsorship.objects.filter(sponsor=sponsor, status='active')
    context = {
        'sponsor': sponsor,
        'active_sponsorships': active_sponsorships,
    }
    return render(request, 'marketplace/sponsorship.html', context)

@login_required
def notification_list(request):
    if request.user.userprofile.role != 'farmer':
        return redirect('marketplace:marketplace_home')
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    for notification in notifications:
        notification.is_read = True
        notification.save()
    context = {'notifications': notifications}
    return render(request, 'marketplace/notification_list.html', context)