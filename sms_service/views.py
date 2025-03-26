from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    SMSMessage, WeatherAlert, PriceUpdate, 
    SMSTemplate, SMSSubscription
)
from .serializers import (
    SMSMessageSerializer, WeatherAlertSerializer, PriceUpdateSerializer,
    SMSTemplateSerializer, SMSSubscriptionSerializer
)
from marketplace.models import Farmer, Buyer
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# Initialize Twilio client
twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID', '')
twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN', '')
twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER', '')
twilio_client = Client(twilio_account_sid, twilio_auth_token) if twilio_account_sid and twilio_auth_token else None

# API ViewSets
class SMSMessageViewSet(viewsets.ModelViewSet):
    queryset = SMSMessage.objects.all().order_by('-sent_at')
    serializer_class = SMSMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'farmer_profile'):
            return SMSMessage.objects.filter(farmer=user.farmer_profile).order_by('-sent_at')
        elif hasattr(user, 'buyer_profile'):
            return SMSMessage.objects.filter(buyer=user.buyer_profile).order_by('-sent_at')
        return SMSMessage.objects.none()
    
    @action(detail=False, methods=['post'])
    def send_sms(self, request):
        """Send an SMS message"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save()
            
            # Send the SMS via Twilio
            if twilio_client:
                try:
                    twilio_message = twilio_client.messages.create(
                        body=message.message_content,
                        from_=twilio_phone_number,
                        to=message.recipient_number
                    )
                    message.twilio_sid = twilio_message.sid
                    message.status = 'sent'
                    message.save()
                    return Response({'status': 'success', 'message_id': message.id}, status=status.HTTP_201_CREATED)
                except TwilioRestException as e:
                    message.status = 'failed'
                    message.save()
                    return Response({'status': 'error', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # For development without Twilio credentials
                message.status = 'simulated'
                message.save()
                return Response({'status': 'simulated', 'message_id': message.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WeatherAlertViewSet(viewsets.ModelViewSet):
    queryset = WeatherAlert.objects.all().order_by('-created_at')
    serializer_class = WeatherAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def send_alert(self, request, pk=None):
        """Send this weather alert to all farmers in the location"""
        alert = self.get_object()
        if alert.is_sent:
            return Response({'status': 'error', 'detail': 'Alert already sent'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get template
        template = SMSTemplate.objects.filter(message_type='weather').first()
        if not template:
            return Response({'status': 'error', 'detail': 'No weather alert template found'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get farmers in the location who are subscribed to weather alerts
        farmers = Farmer.objects.filter(location__icontains=alert.location)
        subscribed_farmers = []
        for farmer in farmers:
            if SMSSubscription.objects.filter(farmer=farmer, subscription_type='weather', is_active=True).exists():
                subscribed_farmers.append(farmer)
        
        # Send SMS to each farmer
        messages_sent = 0
        for farmer in subscribed_farmers:
            context = {
                'farmer_name': farmer.user.first_name,
                'alert_type': alert.alert_type,
                'location': alert.location,
                'description': alert.description,
                'severity': alert.severity
            }
            message_content = template.format_message(context)
            
            sms = SMSMessage.objects.create(
                recipient_number=farmer.phone_number,
                message_content=message_content,
                message_type='weather',
                farmer=farmer
            )
            
            # Send via Twilio
            if twilio_client:
                try:
                    twilio_message = twilio_client.messages.create(
                        body=message_content,
                        from_=twilio_phone_number,
                        to=farmer.phone_number
                    )
                    sms.twilio_sid = twilio_message.sid
                    sms.status = 'sent'
                    sms.save()
                    messages_sent += 1
                except TwilioRestException:
                    sms.status = 'failed'
                    sms.save()
            else:
                # For development without Twilio credentials
                sms.status = 'simulated'
                sms.save()
                messages_sent += 1
        
        # Update alert status
        alert.is_sent = True
        alert.sent_at = timezone.now()
        alert.save()
        
        return Response({
            'status': 'success', 
            'messages_sent': messages_sent,
            'total_farmers': len(subscribed_farmers)
        })

class PriceUpdateViewSet(viewsets.ModelViewSet):
    queryset = PriceUpdate.objects.all().order_by('-created_at')
    serializer_class = PriceUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def send_update(self, request, pk=None):
        """Send this price update to all farmers in the location"""
        price_update = self.get_object()
        if price_update.is_sent:
            return Response({'status': 'error', 'detail': 'Price update already sent'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get template
        template = SMSTemplate.objects.filter(message_type='price').first()
        if not template:
            return Response({'status': 'error', 'detail': 'No price update template found'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get farmers in the location who are subscribed to price updates
        farmers = Farmer.objects.filter(location__icontains=price_update.location)
        subscribed_farmers = []
        for farmer in farmers:
            if SMSSubscription.objects.filter(farmer=farmer, subscription_type='price', is_active=True).exists():
                subscribed_farmers.append(farmer)
        
        # Send SMS to each farmer
        messages_sent = 0
        for farmer in subscribed_farmers:
            context = {
                'farmer_name': farmer.user.first_name,
                'produce': price_update.produce_category.name,
                'price': price_update.price,
                'unit': price_update.unit,
                'location': price_update.location
            }
            message_content = template.format_message(context)
            
            sms = SMSMessage.objects.create(
                recipient_number=farmer.phone_number,
                message_content=message_content,
                message_type='price',
                farmer=farmer
            )
            
            # Send via Twilio
            if twilio_client:
                try:
                    twilio_message = twilio_client.messages.create(
                        body=message_content,
                        from_=twilio_phone_number,
                        to=farmer.phone_number
                    )
                    sms.twilio_sid = twilio_message.sid
                    sms.status = 'sent'
                    sms.save()
                    messages_sent += 1
                except TwilioRestException:
                    sms.status = 'failed'
                    sms.save()
            else:
                # For development without Twilio credentials
                sms.status = 'simulated'
                sms.save()
                messages_sent += 1
        
        # Update price update status
        price_update.is_sent = True
        price_update.sent_at = timezone.now()
        price_update.save()
        
        return Response({
            'status': 'success', 
            'messages_sent': messages_sent,
            'total_farmers': len(subscribed_farmers)
        })

class SMSTemplateViewSet(viewsets.ModelViewSet):
    queryset = SMSTemplate.objects.all()
    serializer_class = SMSTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

class SMSSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = SMSSubscription.objects.all()
    serializer_class = SMSSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'farmer_profile'):
            return SMSSubscription.objects.filter(farmer=user.farmer_profile)
        elif hasattr(user, 'buyer_profile'):
            return SMSSubscription.objects.filter(buyer=user.buyer_profile)
        return SMSSubscription.objects.none()

# Web UI Views
@login_required
def sms_dashboard(request):
    """Dashboard for SMS service"""
    user = request.user
    
    if hasattr(user, 'farmer_profile'):
        profile = user.farmer_profile
        subscriptions = SMSSubscription.objects.filter(farmer=profile)
        messages = SMSMessage.objects.filter(farmer=profile).order_by('-sent_at')[:10]
    elif hasattr(user, 'buyer_profile'):
        profile = user.buyer_profile
        subscriptions = SMSSubscription.objects.filter(buyer=profile)
        messages = SMSMessage.objects.filter(buyer=profile).order_by('-sent_at')[:10]
    else:
        return redirect('marketplace_home')
    
    context = {
        'profile': profile,
        'subscriptions': subscriptions,
        'messages': messages,
        'profile_type': 'farmer' if hasattr(user, 'farmer_profile') else 'buyer',
    }
    return render(request, 'sms_service/dashboard.html', context)

@login_required
def send_sms(request):
    """Form to send SMS messages"""
    if request.method == 'POST':
        recipient_number = request.POST.get('recipient_number')
        message_content = request.POST.get('message_content')
        message_type = request.POST.get('message_type')
        
        user = request.user
        farmer = getattr(user, 'farmer_profile', None)
        buyer = getattr(user, 'buyer_profile', None)
        
        sms = SMSMessage.objects.create(
            recipient_number=recipient_number,
            message_content=message_content,
            message_type=message_type,
            farmer=farmer,
            buyer=buyer
        )
        
        # Send via Twilio
        if twilio_client:
            try:
                twilio_message = twilio_client.messages.create(
                    body=message_content,
                    from_=twilio_phone_number,
                    to=recipient_number
                )
                sms.twilio_sid = twilio_message.sid
                sms.status = 'sent'
                sms.save()
                return redirect('sms_history')
            except TwilioRestException:
                sms.status = 'failed'
                sms.save()
        else:
            # For development without Twilio credentials
            sms.status = 'simulated'
            sms.save()
            return redirect('sms_history')
    
    templates = SMSTemplate.objects.all()
    context = {'templates': templates}
    return render(request, 'sms_service/send_sms.html', context)

@login_required
def sms_history(request):
    """View SMS message history"""
    user = request.user
    
    if hasattr(user, 'farmer_profile'):
        messages = SMSMessage.objects.filter(farmer=user.farmer_profile).order_by('-sent_at')
    elif hasattr(user, 'buyer_profile'):
        messages = SMSMessage.objects.filter(buyer=user.buyer_profile).order_by('-sent_at')
    else:
        messages = SMSMessage.objects.none()
    
    context = {'messages': messages}
    return render(request, 'sms_service/sms_history.html', context)

@login_required
def template_list(request):
    """List SMS templates"""
    templates = SMSTemplate.objects.all()
    context = {'templates': templates}
    return render(request, 'sms_service/template_list.html', context)

@login_required
def template_detail(request, template_id):
    """Detail view for a specific SMS template"""
    template = get_object_or_404(SMSTemplate, id=template_id)
    context = {'template': template}
    return render(request, 'sms_service/template_detail.html', context)

@login_required
def weather_alert_list(request):
    """List weather alerts"""
    alerts = WeatherAlert.objects.all().order_by('-created_at')
    context = {'alerts': alerts}
    return render(request, 'sms_service/weather_alert_list.html', context)

@login_required
def price_update_list(request):
    """List price updates"""
    updates = PriceUpdate.objects.all().order_by('-created_at')
    context = {'updates': updates}
    return render(request, 'sms_service/price_update_list.html', context)

@login_required
def subscription_management(request):
    """Manage SMS subscriptions"""
    user = request.user
    
    if hasattr(user, 'farmer_profile'):
        profile = user.farmer_profile
        subscriptions = SMSSubscription.objects.filter(farmer=profile)
        profile_type = 'farmer'
    elif hasattr(user, 'buyer_profile'):
        profile = user.buyer_profile
        subscriptions = SMSSubscription.objects.filter(buyer=profile)
        profile_type = 'buyer'
    else:
        return redirect('marketplace_home')
    
    if request.method == 'POST':
        subscription_types = request.POST.getlist('subscription_types')
        
        # Deactivate all subscriptions
        subscriptions.update(is_active=False)
        
        # Activate selected subscriptions
        for sub_type in subscription_types:
            subscription, created = SMSSubscription.objects.get_or_create(
                farmer=profile if profile_type == 'farmer' else None,
                buyer=profile if profile_type == 'buyer' else None,
                subscription_type=sub_type,
                defaults={'is_active': True}
            )
            if not created:
                subscription.is_active = True
                subscription.save()
        
        return redirect('subscription_management')
    
    context = {
        'profile': profile,
        'subscriptions': subscriptions,
        'profile_type': profile_type,
        'subscription_types': SMSSubscription.SUBSCRIPTION_TYPES,
    }
    return render(request, 'sms_service/subscription_management.html', context)
