from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from marketplace.models import Farmer, Sponsor, Buyer, UserProfile  # Added UserProfile
import logging

# Set up logging
logger = logging.getLogger(__name__)

class CustomLoginView(LoginView):
    template_name = 'marketplace/login.html'
    success_url = reverse_lazy('marketplace:marketplace_home')

    def dispatch(self, request, *args, **kwargs):
        # Determine the role based on the URL path
        self.role = None
        if 'farmer' in request.path:
            self.role = 'farmer'
        elif 'sponsor' in request.path:
            self.role = 'sponsor'
        elif 'buyer' in request.path:
            self.role = 'buyer'
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        logger.info(f"User {user.username} logged in successfully")

        # Log the user in
        login(self.request, user)

        # Get the UserProfile instance for this user
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            messages.error(self.request, 'No user profile exists for this account.')
            return self.form_invalid(form)

        # Check role and redirect accordingly
        if self.role == 'farmer':
            if not Farmer.objects.filter(profile=user_profile).exists():
                messages.error(self.request, 'You are not authorized as a farmer.')
                return self.form_invalid(form)
            logger.info(f"User {user.username} identified as a farmer, redirecting to farmer_dashboard")
            return redirect('marketplace:farmer_dashboard')
        elif self.role == 'sponsor':
            if not Sponsor.objects.filter(profile=user_profile).exists():
                messages.error(self.request, 'You are not authorized as a sponsor.')
                return self.form_invalid(form)
            logger.info(f"User {user.username} identified as a sponsor, redirecting to sponsorship")
            return redirect('marketplace:sponsorship')  # Updated from 'sponsor_dashboard' to 'sponsorship'
        elif self.role == 'buyer':
            if not Buyer.objects.filter(profile=user_profile).exists():
                messages.error(self.request, 'You are not authorized as a buyer.')
                return self.form_invalid(form)
            logger.info(f"User {user.username} identified as a buyer, redirecting to buyer_dashboard")
            return redirect('marketplace:buyer_dashboard')
        else:
            logger.info(f"User {user.username} has no specific role, redirecting to marketplace_home")
            return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password, or unauthorized role.')
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['error'] = messages.get_messages(self.request)
        return context

# Root view
def home(request):
    return render(request, 'marketplace/home.html')