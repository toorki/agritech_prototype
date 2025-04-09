from rest_framework import serializers
from .models import Farmer, Buyer, ProduceCategory, Produce, Order, Rating
from django.contrib.auth.models import User
from .models import (
    Farmer, Buyer, ProduceCategory, Produce, Order, Rating,
    Sponsorship, SponsorshipMilestone, SponsorshipPayment,
)

# Add to your existing serializers.py file

class SponsorshipMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = SponsorshipMilestone
        fields = '__all__'

class SponsorshipSerializer(serializers.ModelSerializer):
    milestones = SponsorshipMilestoneSerializer(many=True, read_only=True)
    
    class Meta:
        model = Sponsorship
        fields = '__all__'

class SponsorshipSerializer(serializers.ModelSerializer):
    farmer_name = serializers.ReadOnlyField(source='farmer.user.get_full_name')
    sponsor_name = serializers.ReadOnlyField(source='sponsor.get_full_name')
    
    class Meta:
        model = Sponsorship
        fields = ['id', 'farmer', 'farmer_name', 'sponsor', 'sponsor_name', 'title', 
                  'description', 'amount_requested', 'expected_yield', 
                  'expected_completion_date', 'created_at', 'status']

class SponsorshipMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = SponsorshipMilestone
        fields = ['id', 'sponsorship', 'title', 'description', 'due_date', 
                  'status', 'verified_by', 'verification_date', 'verification_notes']

class SponsorshipPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SponsorshipPayment
        fields = ['id', 'sponsorship', 'amount', 'payment_type', 
                  'payment_date', 'transaction_id']
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class FarmerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Farmer
        fields = ['id', 'user', 'phone_number', 'location', 'rating', 'total_ratings', 'created_at', 'updated_at']

class BuyerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Buyer
        fields = ['id', 'user', 'phone_number', 'location', 'created_at', 'updated_at']

class ProduceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProduceCategory
        fields = ['id', 'name', 'description']

class ProduceSerializer(serializers.ModelSerializer):
    farmer = FarmerSerializer(read_only=True)
    category = ProduceCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ProduceCategory.objects.all(),
        source='category',
        write_only=True
    )
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Produce
        fields = [
            'id', 'farmer', 'category', 'category_id', 'title', 'description',
            'quantity', 'unit', 'price_per_unit', 'location', 'is_available',
            'total_price', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'farmer':
            farmer_profile = request.user.userprofile.farmer_profiles.first()
            if farmer_profile:
                validated_data['farmer'] = farmer_profile
                return super().create(validated_data)
        raise serializers.ValidationError("You must be a registered farmer to create produce listings")

class OrderSerializer(serializers.ModelSerializer):
    buyer = BuyerSerializer(read_only=True)
    produce = ProduceSerializer(read_only=True)
    produce_id = serializers.PrimaryKeyRelatedField(
        queryset=Produce.objects.all(),
        source='produce',
        write_only=True
    )
    
    class Meta:
        model = Order
        fields = [
            'id', 'buyer', 'produce', 'produce_id', 'quantity', 'unit_price',
            'platform_fee', 'total_amount', 'status', 'delivery_location',
            'delivery_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['unit_price', 'platform_fee', 'total_amount']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'buyer':
            buyer_profile = request.user.userprofile.buyer_profiles.first()
            if buyer_profile:
                validated_data['buyer'] = buyer_profile
                return super().create(validated_data)
        raise serializers.ValidationError("You must be a registered buyer to create orders")

class RatingSerializer(serializers.ModelSerializer):
    buyer = BuyerSerializer(read_only=True)
    farmer = FarmerSerializer(read_only=True)
    order = OrderSerializer(read_only=True)
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        source='order',
        write_only=True
    )
    
    class Meta:
        model = Rating
        fields = ['id', 'buyer', 'farmer', 'order', 'order_id', 'score', 'comment', 'created_at']
    
    def create(self, validated_data):
        request = self.context.get('request')
        order = validated_data.get('order')
        
        if not request or not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'buyer':
            raise serializers.ValidationError("You must be a registered buyer to create ratings")
        
        if order.buyer.user != request.user:
            raise serializers.ValidationError("You can only rate orders that you have placed")
        
        if order.status != 'completed':
            raise serializers.ValidationError("You can only rate completed orders")
        
        if Rating.objects.filter(order=order).exists():
            raise serializers.ValidationError("You have already rated this order")
        
        validated_data['buyer'] = request.user.userprofile.buyer_profiles.first()
        validated_data['farmer'] = order.produce.farmer
        return super().create(validated_data)