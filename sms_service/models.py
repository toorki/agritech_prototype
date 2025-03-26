from django.db import models
from marketplace.models import Farmer, Buyer, Produce, Order

class SMSMessage(models.Model):
    """Model for tracking SMS messages sent through the system"""
    MESSAGE_TYPES = [
        ('weather', 'Weather Alert'),
        ('price', 'Price Update'),
        ('order', 'Order Notification'),
        ('payment', 'Payment Notification'),
        ('system', 'System Notification'),
        ('marketing', 'Marketing Message'),
    ]
    
    recipient_number = models.CharField(max_length=15)
    message_content = models.TextField()
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    farmer = models.ForeignKey(Farmer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sms_messages')
    buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sms_messages')
    related_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='sms_messages')
    related_produce = models.ForeignKey(Produce, on_delete=models.SET_NULL, null=True, blank=True, related_name='sms_messages')
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')
    twilio_sid = models.CharField(max_length=50, blank=True, null=True)  # Twilio message ID
    
    def __str__(self):
        return f"{self.message_type} to {self.recipient_number} at {self.sent_at}"


class WeatherAlert(models.Model):
    """Model for weather alerts to be sent to farmers"""
    location = models.CharField(max_length=100)
    alert_type = models.CharField(max_length=50)  # e.g., rain, drought, frost
    description = models.TextField()
    severity = models.CharField(max_length=20)  # e.g., low, medium, high
    created_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.alert_type} alert for {self.location} - {self.severity}"


class PriceUpdate(models.Model):
    """Model for market price updates to be sent to farmers"""
    produce_category = models.ForeignKey('marketplace.ProduceCategory', on_delete=models.CASCADE, related_name='price_updates')
    location = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=10)  # e.g., kg, ton
    source = models.CharField(max_length=100)  # Source of price information
    created_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.produce_category} price: {self.price}/{self.unit} in {self.location}"


class SMSTemplate(models.Model):
    """Model for SMS templates to ensure consistent messaging"""
    name = models.CharField(max_length=50, unique=True)
    template_text = models.TextField(help_text="Use {variable} syntax for placeholders")
    description = models.TextField(blank=True)
    message_type = models.CharField(max_length=10, choices=SMSMessage.MESSAGE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def format_message(self, context_dict):
        """
        Format the template with the provided context variables
        
        Args:
            context_dict: Dictionary of variables to replace in the template
            
        Returns:
            Formatted message string
        """
        message = self.template_text
        for key, value in context_dict.items():
            placeholder = '{' + key + '}'
            message = message.replace(placeholder, str(value))
        return message


class SMSSubscription(models.Model):
    """Model for tracking which types of SMS alerts users are subscribed to"""
    SUBSCRIPTION_TYPES = [
        ('weather', 'Weather Alerts'),
        ('price', 'Price Updates'),
        ('order', 'Order Notifications'),
        ('system', 'System Notifications'),
        ('marketing', 'Marketing Messages'),
    ]
    
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, null=True, blank=True, related_name='sms_subscriptions')
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, null=True, blank=True, related_name='sms_subscriptions')
    subscription_type = models.CharField(max_length=10, choices=SUBSCRIPTION_TYPES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['farmer', 'subscription_type'], ['buyer', 'subscription_type']]
        
    def __str__(self):
        subscriber = self.farmer if self.farmer else self.buyer
        return f"{subscriber} - {self.subscription_type} subscription"
