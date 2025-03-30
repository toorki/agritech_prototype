from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import logout
from marketplace.models import Farmer, Sponsor, Buyer

# Custom login view with role-based redirection
class CustomLoginView(LoginView):
    template_name = 'marketplace/login.html'
    success_url = reverse_lazy('marketplace:marketplace_home')

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
            return redirect('marketplace:marketplace_home')

    def get_success_url(self):
        return self.success_url

# Root view
def home(request):
    return render(request, 'marketplace/home.html')