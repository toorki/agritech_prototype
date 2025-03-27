from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Sponsorship(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    farmer = models.ForeignKey('Farmer', on_delete=models.CASCADE, related_name='sponsorships')
    sponsor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sponsored_projects', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    amount_requested = models.DecimalField(max_digits=10, decimal_places=2)
    expected_yield = models.DecimalField(max_digits=10, decimal_places=2)
    expected_completion_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"{self.title} - {self.farmer.user.username}"

class SponsorshipMilestone(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    sponsorship = models.ForeignKey(Sponsorship, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_milestones')
    verification_date = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.sponsorship.title}"
    
    def verify(self, user, notes=""):
        self.status = 'completed'
        self.verified_by = user
        self.verification_date = timezone.now()
        self.verification_notes = notes
        self.save()

class SponsorshipPayment(models.Model):
    TYPE_CHOICES = (
        ('investment', 'Investment'),
        ('return', 'Return'),
    )
    
    sponsorship = models.ForeignKey(Sponsorship, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.payment_type} - {self.amount} - {self.sponsorship.title}"
    
class Farmer(models.Model):
    """Model representing a farmer in the system"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    phone_number = models.CharField(max_length=15)
    location = models.CharField(max_length=100)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_ratings = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.location}"
    
    def update_rating(self, new_rating):
        """Update the farmer's rating with a new rating value"""
        if self.total_ratings == 0:
            self.rating = new_rating
        else:
            # Calculate weighted average
            self.rating = ((self.rating * self.total_ratings) + new_rating) / (self.total_ratings + 1)
        self.total_ratings += 1
        self.save()


class Buyer(models.Model):
    """Model representing a buyer in the system"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer_profile')
    phone_number = models.CharField(max_length=15)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.location}"


class ProduceCategory(models.Model):
    """Model representing categories of agricultural produce"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Produce Categories"


class Produce(models.Model):
    """Model representing agricultural produce listings"""
    UNIT_CHOICES = [
        ('kg', 'Kilograms'),
        ('g', 'Grams'),
        ('ton', 'Tons'),
        ('l', 'Liters'),
        ('unit', 'Units/Pieces'),
    ]
    
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='produce')
    category = models.ForeignKey(ProduceCategory, on_delete=models.SET_NULL, null=True, related_name='produce_items')
    title = models.CharField(max_length=100)
    description = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    unit = models.CharField(max_length=4, choices=UNIT_CHOICES, default='kg')
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    location = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.quantity} {self.unit} at {self.price_per_unit}/unit"
    
    @property
    def total_price(self):
        """Calculate the total price of the produce listing"""
        return self.quantity * self.price_per_unit


class Order(models.Model):
    """Model representing orders placed by buyers"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='orders')
    produce = models.ForeignKey(Produce, on_delete=models.CASCADE, related_name='orders')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2)  # 2% fee
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total including fee
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    delivery_location = models.CharField(max_length=100)
    delivery_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.buyer} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Calculate platform fee (2%) and total amount if not already set
        if not self.pk:  # Only on creation
            self.unit_price = self.produce.price_per_unit
            subtotal = self.quantity * self.unit_price
            self.platform_fee = subtotal * 0.02  # 2% fee
            self.total_amount = subtotal + self.platform_fee
        super().save(*args, **kwargs)


class Rating(models.Model):
    """Model representing ratings given by buyers to farmers"""
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='ratings_given')
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='ratings_received')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='rating')
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])  # 1-5 rating
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.buyer} rated {self.farmer}: {self.score}/5"
    
    def save(self, *args, **kwargs):
        # Update farmer's rating when a new rating is created
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.farmer.update_rating(self.score)
