from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Farmer, Sponsor, Buyer, Sponsorship, Produce, Order, Rating

# Existing views (assumed based on URLs)
def home(request):
    return render(request, 'marketplace/home.html')

def sponsorship_list(request):
    sponsorships = Sponsorship.objects.all()
    return render(request, 'marketplace/sponsorship_list.html', {'sponsorships': sponsorships})

def produce_list(request):
    produce_items = Produce.objects.all()
    return render(request, 'marketplace/produce_list.html', {'produce_items': produce_items})

def user_profile(request):
    return render(request, 'marketplace/user_profile.html')

# Custom login view with role-based redirection
class CustomLoginView(LoginView):
    template_name = 'marketplace/login.html'
    success_url = reverse_lazy('marketplace:home')

    def form_valid(self, form):
        # Log the user in
        response = super().form_valid(form)
        user = self.request.user

        # Check user role and redirect accordingly
        if Farmer.objects.filter(user=user).exists():
            return redirect('marketplace:farmer_dashboard')
        elif Sponsor.objects.filter(user=user).exists():
            return redirect('marketplace:sponsor_dashboard')
        elif Buyer.objects.filter(user=user).exists():
            return redirect('marketplace:buyer_dashboard')
        else:
            return redirect('marketplace:home')

    def get_success_url(self):
        return self.success_url

# Dashboard views for each role
@login_required
def farmer_dashboard(request):
    return render(request, 'marketplace/farmer_dashboard.html', {'user': request.user})

@login_required
def sponsor_dashboard(request):
    return render(request, 'marketplace/sponsor_dashboard.html', {'user': request.user})

@login_required
def buyer_dashboard(request):
    return render(request, 'marketplace/buyer_dashboard.html', {'user': request.user})

# Logout view
def logout_view(request):
    logout(request)
    return redirect('marketplace:home')