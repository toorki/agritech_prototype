from rest_framework import serializers
from .models import SMSMessage, WeatherAlert, PriceUpdate, SMSTemplate, SMSSubscription
from marketplace.models import Farmer, Buyer, Produce, Order
from marketplace.serializers import FarmerSerializer, BuyerSerializer, ProduceSerializer, OrderSerializer

class SMSMessageSerializer(serializers.ModelSerializer):
    farmer = FarmerSerializer(read_only=True)
    buyer = BuyerSerializer(read_only=True)
    related_order = OrderSerializer(read_only=True)
    related_produce = ProduceSerializer(read_only=True)
    
    class Meta:
        model = SMSMessage
        fields = [
            'id', 'recipient_number', 'message_content', 'message_type',
            'farmer', 'buyer', 'related_order', 'related_produce',
            'sent_at', 'status', 'twilio_sid'
        ]
        read_only_fields = ['sent_at', 'status', 'twilio_sid']

class WeatherAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherAlert
        fields = [
            'id', 'location', 'alert_type', 'description', 'severity',
            'created_at', 'is_sent', 'sent_at'
        ]
        read_only_fields = ['created_at', 'is_sent', 'sent_at']

class PriceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceUpdate
        fields = [
            'id', 'produce_category', 'location', 'price', 'unit',
            'source', 'created_at', 'is_sent', 'sent_at'
        ]
        read_only_fields = ['created_at', 'is_sent', 'sent_at']

class SMSTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSTemplate
        fields = [
            'id', 'name', 'template_text', 'description', 'message_type',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_template_text(self, value):
        """
        Validate that the template text contains valid placeholders
        """
        # Simple validation to check for matching braces
        open_braces = value.count('{')
        close_braces = value.count('}')
        
        if open_braces != close_braces:
            raise serializers.ValidationError("Template has mismatched braces")
        
        return value

class SMSSubscriptionSerializer(serializers.ModelSerializer):
    farmer = FarmerSerializer(read_only=True)
    buyer = BuyerSerializer(read_only=True)
    
    class Meta:
        model = SMSSubscription
        fields = [
            'id', 'farmer', 'buyer', 'subscription_type', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        """
        Check that either farmer or buyer is provided
        """
        request = self.context.get('request')
        if request:
            user = request.user
            if hasattr(user, 'farmer_profile'):
                data['farmer'] = user.farmer_profile
            elif hasattr(user, 'buyer_profile'):
                data['buyer'] = user.buyer_profile
            else:
                raise serializers.ValidationError("User must be either a farmer or a buyer")
        return data
