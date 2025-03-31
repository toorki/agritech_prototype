from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import logout, authenticate, login
from marketplace.models import Farmer, Sponsor, Buyer
import logging  # Added logging import

# Set up logging
logger = logging.getLogger(__name__)

# Custom login view with role-based redirection
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

        # Authenticate and login the user
        login(self.request, user)

        # Enforce role-specific redirection
        if self.role == 'farmer' and not Farmer.objects.filter(user=user).exists():
            logger.warning(f"User {user.username} attempted to log in as farmer but has no farmer profile")
            return render(self.request, self.template_name, {'form': form, 'error': 'You are not authorized as a farmer.'})
        elif self.role == 'sponsor' and not Sponsor.objects.filter(user=user).exists():
            logger.warning(f"User {user.username} attempted to log in as sponsor but has no sponsor profile")
            return render(self.request, self.template_name, {'form': form, 'error': 'You are not authorized as a sponsor.'})
        elif self.role == 'buyer' and not Buyer.objects.filter(user=user).exists():
            logger.warning(f"User {user.username} attempted to log in as buyer but has no buyer profile")
            return render(self.request, self.template_name, {'form': form, 'error': 'You are not authorized as a buyer.'})

        # Redirect based on the detected or enforced role
        if Farmer.objects.filter(user=user).exists():
            logger.info(f"User {user.username} identified as a farmer, redirecting to farmer_dashboard")
            return redirect('marketplace:farmer_dashboard')
        elif Sponsor.objects.filter(user=user).exists():
            logger.info(f"User {user.username} identified as a sponsor, redirecting to sponsor_dashboard")
            return redirect('marketplace:sponsor_dashboard')
        elif Buyer.objects.filter(user=user).exists():
            logger.info(f"User {user.username} identified as a buyer, redirecting to buyer_dashboard")
            return redirect('marketplace:buyer_dashboard')
        else:
            logger.info(f"User {user.username} has no specific role, redirecting to marketplace_home")
            return redirect('marketplace:marketplace_home')

    def get_success_url(self):
        # This will be overridden by form_valid's return
        return self.success_url

# Root view
def home(request):
    return render(request, 'marketplace/home.html')