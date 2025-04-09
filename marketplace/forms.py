from django import forms
from .models import Produce, ProduceCategory

class ProduceForm(forms.ModelForm):
    class Meta:
        model = Produce
        fields = ['title', 'category', 'description', 'quantity', 'unit', 'price_per_unit', 'location', 'is_available']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ProduceCategory.objects.all()
        self.fields['unit'].choices = Produce.UNIT_CHOICES  # Ensure unit choices match the model