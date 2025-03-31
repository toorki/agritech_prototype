from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import logout
from marketplace.models import Farmer, Sponsor, Buyer
import logging  # Added logging import

# Set up logging
logger = logging.getLogger(__name__)

# Custom login view with role-based redirection
class CustomLoginView(LoginView):
    template_name = 'marketplace/login.html'
    success_url = reverse_lazy('marketplace:marketplace_home')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        logger.info(f"User {user.username} logged in successfully")
        return response

    def get_success_url(self):
        user = self.request.user
        if Farmer.objects.filter(user=user).exists():
            logger.info(f"User {user.username} identified as a farmer, redirecting to farmer_dashboard")
            return reverse_lazy('marketplace:farmer_dashboard')
        elif Sponsor.objects.filter(user=user).exists():
            logger.info(f"User {user.username} identified as a sponsor, redirecting to sponsor_dashboard")
            return reverse_lazy('marketplace:sponsor_dashboard')
        elif Buyer.objects.filter(user=user).exists():
            logger.info(f"User {user.username} identified as a buyer, redirecting to buyer_dashboard")
            return reverse_lazy('marketplace:buyer_dashboard')
        else:
            logger.info(f"User {user.username} has no specific role, redirecting to marketplace_home")
            return reverse_lazy('marketplace:marketplace_home')

# Root view
def home(request):
    return render(request, 'marketplace/home.html')