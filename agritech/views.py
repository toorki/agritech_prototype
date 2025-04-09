from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from marketplace.models import Farmer, Sponsor, Buyer, UserProfile, Produce
from marketplace.forms import ProduceForm
import logging

logger = logging.getLogger(__name__)

class CustomLoginView(LoginView):
    template_name = 'marketplace/login.html'
    success_url = reverse_lazy('marketplace:marketplace_home')

    def dispatch(self, request, *args, **kwargs):
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
        login(self.request, user)
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            messages.error(self.request, 'No user profile exists for this account.')
            return self.form_invalid(form)
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
            return redirect('marketplace:sponsorship')
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

def home(request):
    return render(request, 'marketplace/home.html')

class AddProduceView(LoginRequiredMixin, CreateView):
    model = Produce
    form_class = ProduceForm
    template_name = 'marketplace/add_produce.html'
    success_url = reverse_lazy('marketplace:marketplace_home')

    def form_valid(self, form):
        logger.debug(f"Form data: {form.cleaned_data}")
        # Get the farmer associated with the current user
        try:
            user_profile = self.request.user.userprofile
            farmer = Farmer.objects.get(profile=user_profile)
            form.instance.farmer = farmer
        except (UserProfile.DoesNotExist, Farmer.DoesNotExist):
            messages.error(self.request, 'You are not authorized as a farmer or your profile is incomplete.')
            return self.form_invalid(form)
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.error(f"Form invalid: {form.errors}")
        messages.error(self.request, f"Error adding produce: {form.errors}")
        return self.render_to_response(self.get_context_data(form=form))