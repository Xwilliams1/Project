from django import forms
from django.utils import timezone

from .models import Restaurant


class BookingForm(forms.Form):
    """
    Guest-facing reservation form (proposal deliverable 1).
    A plain Form (not ModelForm) because it collects data for TWO models,
    Customer and Booking. site_views.book() saves both.
    """

    OCCASION_CHOICES = [
        ('', 'None'),
        ('Birthday', 'Birthday'),
        ('Anniversary', 'Anniversary'),
        ('Business', 'Business'),
        ('Celebration', 'Celebration'),
        ('Other', 'Other'),
    ]

    # --- Booking details ---
    restaurant = forms.ModelChoiceField(
        queryset=Restaurant.objects.all().order_by('restaurant_name'),
        empty_label='Select a location', label='Location')
    booking_date = forms.DateField(
        label='Date', widget=forms.DateInput(attrs={'type': 'date'}))
    booking_time = forms.TimeField(
        label='Time', widget=forms.TimeInput(attrs={'type': 'time'}))
    # Larger parties should phone the restaurant (adjust as needed).
    guest_count = forms.IntegerField(
        label='Number of guests', min_value=1, max_value=20)
    occasion = forms.ChoiceField(
        choices=OCCASION_CHOICES, required=False, label='Occasion')
    customer_notes = forms.CharField(
        required=False, label='Special requests',
        widget=forms.Textarea(attrs={'rows': 3}))

    # --- Contact details ---
    first_name = forms.CharField(max_length=100, label='First name')
    last_name = forms.CharField(max_length=100, label='Last name')
    email = forms.EmailField(label='Email')
    phone = forms.CharField(max_length=20, required=False, label='Phone')
    marketing_consent = forms.BooleanField(
        required=False,
        label='I agree to receive news and offers from the restaurant')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Browsers grey out past dates in the date picker.
        self.fields['booking_date'].widget.attrs['min'] = timezone.localdate().isoformat()

    def clean_booking_date(self):
        """Server-side check (the browser 'min' can be bypassed)."""
        date = self.cleaned_data['booking_date']
        if date < timezone.localdate():
            raise forms.ValidationError('Please choose a date today or later.')
        return date
