from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, permissions
from decimal import Decimal
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

def logout_view(request):
    logout(request)
    return redirect('marketplace:marketplace_home')

def produce_detail(request, produce_id):
    produce = get_object_or_404(Produce, id=produce_id)
    related_items = Produce.objects.filter(category=produce.category, is_available=True).exclude(id=produce_id)[:4]
    MIN_QUANTITY = {
        'kg': 50.0,
        'g': 50000.0,
        'ton': 0.05,
        'l': 50.0,
        'unit': 50.0
    }
    min_quantity = MIN_QUANTITY.get(produce.unit, 50.0)
    context = {
        'produce': produce,
        'related_items': related_items,
        'min_quantity': min_quantity,
    }
    return render(request, 'marketplace/produce_detail.html', context)

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
            active_sponsorships = Sponsorship.objects.filter(sponsor=sponsor, status='active')
            context = {'profile': sponsor, 'active_sponsorships': active_sponsorships, 'profile_type': 'sponsor'}
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
    sponsorships = Sponsorship.objects.filter(farmer=farmer)
    orders = Order.objects.filter(produce__farmer=farmer, status__in=['pending', 'confirmed', 'paid'])
    unread_notifications_count = farmer.profile.user.notifications.filter(is_read=False).count()

    context = {
        'farmer': farmer,
        'crops': crops,
        'sponsorships': sponsorships,
        'orders': orders,
        'unread_notifications_count': unread_notifications_count,
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

        if not (is_farmer or is_sponsor):
            logger.warning(f"Unauthorized access to sponsorship {sponsorship_id} by {request.user.username}")
            messages.error(request, "You are not authorized to view this sponsorship.")
            return redirect('marketplace:farmer_dashboard')
    except UserProfile.DoesNotExist:
        logger.error(f"User {request.user.username} has no UserProfile while accessing sponsorship {sponsorship_id}")
        messages.error(request, "Profile not found.")
        return redirect('marketplace:farmer_dashboard')

    # Handle approval or rejection by farmer
    if request.method == 'POST' and is_farmer:
        action = request.POST.get('action')
        if action == 'approve' and sponsorship.status == 'pending':
            sponsorship.status = 'active'
            sponsorship.save()
            messages.success(request, "Sponsorship proposal approved successfully!")
            # Notify sponsor
            Notification.objects.create(
                user=sponsorship.sponsor.profile.user,
                message=f"Your sponsorship proposal '{sponsorship.title}' has been approved by {sponsorship.farmer.profile.user.get_full_name()}."
            )
        elif action == 'reject' and sponsorship.status == 'pending':
            sponsorship.delete()  # Delete the sponsorship instead of changing status
            messages.success(request, "Sponsorship proposal rejected and removed.")
            # Notify sponsor via platform
            Notification.objects.create(
                user=sponsorship.sponsor.profile.user,
                message=f"Your sponsorship proposal '{sponsorship.title}' has been rejected by {sponsorship.farmer.profile.user.get_full_name()}."
            )
            # Notify sponsor via email
            subject = f"Sponsorship Proposal Rejected: {sponsorship.title}"
            message = f"Dear {sponsorship.sponsor.profile.user.get_full_name()},\n\nYour sponsorship proposal '{sponsorship.title}' has been rejected by {sponsorship.farmer.profile.user.get_full_name()}.\n\nBest,\nAgriTech Team"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [sponsorship.sponsor.profile.user.email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            logger.debug(f"Email sent to {sponsorship.sponsor.profile.user.email}")
            # Notify sponsor via SMS
            sms_message = f"Your sponsorship proposal '{sponsorship.title}' has been rejected by {sponsorship.farmer.profile.user.get_full_name()}. AgriTech"
            send_sms(sponsorship.sponsor.phone_number, sms_message)
            logger.debug(f"SMS sent to {sponsorship.sponsor.phone_number}")
        return redirect('marketplace:farmer_dashboard')  # Redirect to dashboard to refresh sponsorships

    # Prepare sponsor information
    sponsor_info = {
        'name': sponsorship.sponsor.profile.user.get_full_name() if sponsorship.sponsor else "Not assigned yet",
        'contact': sponsorship.sponsor.phone_number if sponsorship.sponsor else "Not available",
        'organization': sponsorship.sponsor.organization if sponsorship.sponsor else "Not specified",
    }

    context = {
        'sponsorship': sponsorship,
        'milestones': milestones,
        'payments': payments,
        'is_farmer': is_farmer,
        'is_sponsor': is_sponsor,
        'sponsor_info': sponsor_info,
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
                message=f"New sponsorship proposal '{sponsorship.id}' created by {sponsor.profile.user.get_full_name()}."
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

@login_required
def delete_produce(request, produce_id):
    produce = get_object_or_404(Produce, id=produce_id)
    try:
        profile = UserProfile.objects.get(user=request.user)
        farmer = Farmer.objects.get(profile=profile)
        if produce.farmer != farmer:
            messages.error(request, "You are not authorized to delete this produce.")
            return redirect('marketplace:farmer_dashboard')
    except (UserProfile.DoesNotExist, Farmer.DoesNotExist):
        messages.error(request, "Profile not found.")
        return redirect('marketplace:farmer_dashboard')

    if request.method == 'POST':
        produce.delete()
        messages.success(request, "Produce deleted successfully!")
        return redirect('marketplace:farmer_dashboard')

    context = {'produce': produce}
    return render(request, "marketplace/confirm_delete_produce.html", context)

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
    # Mark all notifications as read
    notifications.filter(is_read=False).update(is_read=True)
    
    # Prepare notifications with order IDs and sponsorship IDs
    processed_notifications = []
    for notification in notifications:
        order_id = None
        sponsorship_id = None
        # Check for order notifications
        if "New order placed" in notification.message:
            logger.debug(f"Processing order notification: {notification.message}")
            match = re.search(r'\[Order ID: (\d+)\]', notification.message)
            if match:
                order_id = match.group(1)
                logger.debug(f"Extracted order_id: {order_id}")
            else:
                logger.warning(f"Failed to extract order_id from message: {notification.message}")
        # Check for sponsorship notifications
        elif "New sponsorship proposal" in notification.message:
            logger.debug(f"Processing sponsorship notification: {notification.message}")
            match = re.search(r"New sponsorship proposal '(\d+)'", notification.message)
            if match:
                sponsorship_id = match.group(1)
                logger.debug(f"Extracted sponsorship_id: {sponsorship_id}")
            else:
                logger.warning(f"Failed to extract sponsorship_id from message: {notification.message}")
        processed_notifications.append({
            'id': notification.id,
            'message': notification.message,
            'created_at': notification.created_at,
            'order_id': order_id,
            'sponsorship_id': sponsorship_id,
        })
    
    # Debug: Log the processed notifications to verify
    logger.debug(f"Processed notifications: {processed_notifications}")
    
    context = {
        'notifications': processed_notifications,
    }
    return render(request, 'marketplace/notification_list.html', context)

@login_required
def create_order(request, produce_id):
    produce = get_object_or_404(Produce, id=produce_id)
    user_profile = getattr(request.user, 'userprofile', None)

    if not user_profile or user_profile.role != 'buyer':
        logger.error(f"Unauthorized order attempt by {request.user.username} (role: {user_profile.role if user_profile else 'None'})")
        messages.error(request, "You must be logged in as a buyer to place an order.")
        return redirect('marketplace:produce_detail', produce_id=produce.id)

    try:
        buyer = Buyer.objects.get(profile=user_profile)
    except Buyer.DoesNotExist:
        logger.error(f"No buyer profile found for user {request.user.username}")
        messages.error(request, "No buyer profile found. Please matters.")
        return redirect('marketplace:produce_detail', produce_id=produce.id)

    if request.method == 'POST':
        quantity_str = request.POST.get('quantity', '')
        delivery_location = request.POST.get('delivery_location', '')
        delivery_notes = request.POST.get('delivery_notes', '')

        try:
            quantity = Decimal(quantity_str)
        except ValueError:
            logger.error(f"Invalid quantity value: {quantity_str}")
            messages.error(request, "Please enter a valid quantity.")
            return redirect('marketplace:produce_detail', produce_id=produce.id)

        MIN_QUANTITY = {
            'kg': Decimal('50.0'),
            'g': Decimal('50000.0'),
            'ton': Decimal('0.05'),
            'l': Decimal('50.0'),
            'unit': Decimal('50.0')
        }
        min_quantity = MIN_QUANTITY.get(produce.unit, Decimal('50.0'))

        if quantity < min_quantity:
            messages.error(request, f"Minimum order quantity is {min_quantity} {produce.unit}. Please enter a valid quantity.")
            return redirect('marketplace:produce_detail', produce_id=produce.id)
        if quantity <= Decimal('0') or quantity > produce.quantity:
            messages.error(request, f"Invalid quantity. Please enter a value between {min_quantity} and {produce.quantity} {produce.unit}.")
            return redirect('marketplace:produce_detail', produce_id=produce.id)

        unit_price = produce.price_per_unit
        subtotal = quantity * unit_price
        platform_fee = subtotal * Decimal('0.02')
        total_amount = subtotal + platform_fee

        order = Order.objects.create(
            buyer=buyer,
            produce=produce,
            quantity=quantity,
            unit_price=unit_price,
            platform_fee=platform_fee,
            total_amount=total_amount,
            status='pending',
            delivery_location=delivery_location,
            delivery_notes=delivery_notes
        )

        produce.quantity -= quantity
        produce.save()

        # Notify the farmer with order ID in the message
        farmer_user = produce.farmer.profile.user
        notification_message = f"New order placed for {produce.title} by {buyer.profile.user.get_full_name()} for {quantity} {produce.unit} [Order ID: {order.id}]"
        Notification.objects.create(
            user=farmer_user,
            message=notification_message
        )

        # Email notification
        subject = f"New Order for {produce.title}"
        message = f"Dear {farmer_user.get_full_name()},\n\nA new order has been placed for your produce '{produce.title}' by {buyer.profile.user.get_full_name()}.\n\nDetails:\n- Quantity: {quantity} {produce.unit}\n- Delivery Location: {delivery_location}\n- Total Amount: {total_amount} TND\n- Order ID: {order.id}\n\nPlease log in to manage this order.\n\nBest,\nAgriTech Team"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [farmer_user.email]
        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=True)
            logger.debug(f"Email sent to {farmer_user.email}")
        except Exception as e:
            logger.error(f"Failed to send email to {farmer_user.email}: {str(e)}")
            messages.warning(request, "Order placed, but email notification to farmer failed. Please contact support.")

        # SMS notification
        sms_message = f"New order for {produce.title} by {buyer.profile.user.get_full_name()} for {quantity} {produce.unit} [Order ID: {order.id}]. Log in to manage. AgriTech"
        try:
            send_sms(produce.farmer.phone_number, sms_message)
            logger.debug(f"SMS sent to {produce.farmer.phone_number}")
        except Exception as e:
            logger.error(f"Failed to send SMS to {produce.farmer.phone_number}: {str(e)}")
            messages.warning(request, "Order placed, but SMS notification to farmer failed. Please contact support.")

        messages.success(request, "Order placed successfully! You will be notified of the status.")
        return redirect('marketplace:order_detail', order_id=order.id)

    return redirect('marketplace:produce_detail', produce_id=produce.id)