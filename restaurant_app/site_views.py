from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from .forms import BookingForm
from .models import Restaurant, Customer, Booking


def home(request):
    """Landing page: lists every location with its hours and a Book button."""
    restaurants = Restaurant.objects.all().order_by('restaurant_name')
    return render(request, 'restaurant_app/home.html', {'restaurants': restaurants})


def send_confirmation_email(booking):
    """
    Booking confirmation (deliverable 4). With the console email backend in
    settings.py this prints in the runserver terminal instead of sending.
    """
    body = (
        f"Hi {booking.customer.first_name},\n\n"
        f"Your reservation is confirmed.\n\n"
        f"Reference: #{booking.id}\n"
        f"Location:  {booking.restaurant.restaurant_name}\n"
        f"Date:      {booking.booking_date:%A %d %B %Y}\n"
        f"Time:      {booking.booking_time:%H:%M}\n"
        f"Guests:    {booking.guest_count}\n\n"
        f"We look forward to seeing you."
    )
    send_mail(
        subject=f"Booking confirmed at {booking.restaurant.restaurant_name}",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.customer.email],
    )


def book(request):
    """
    Guest booking form.
      GET  -> empty form (pre-selects ?restaurant=<id> if given)
      POST -> validate, find or create the Customer, create the Booking
              (runs Booking.clean(): hours, double booking, capacity),
              email the guest, redirect to the confirmation page.
    """
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            try:
                # atomic: if the booking is rejected, a newly created
                # customer is rolled back too, so nothing is half-saved.
                with transaction.atomic():
                    customer = Customer.objects.filter(email__iexact=d['email']).first()
                    if customer is None:
                        customer = Customer.objects.create(
                            first_name=d['first_name'], last_name=d['last_name'],
                            email=d['email'], phone=d['phone'],
                            marketing_consent=d['marketing_consent'])
                    else:
                        # Returning guest: keep the stored name, only fill in
                        # a missing phone, and only ever opt IN to marketing.
                        if not customer.phone and d['phone']:
                            customer.phone = d['phone']
                        if d['marketing_consent']:
                            customer.marketing_consent = True
                        customer.save()

                    booking = Booking.objects.create(
                        restaurant=d['restaurant'], customer=customer,
                        booking_date=d['booking_date'], booking_time=d['booking_time'],
                        guest_count=d['guest_count'], occasion=d['occasion'],
                        customer_notes=d['customer_notes'], status='CONFIRMED')
            except ValidationError as e:
                # Booking.clean() messages appear at the top of the form.
                form.add_error(None, e.messages)
            else:
                send_confirmation_email(booking)
                # Only this browser may open the confirmation page.
                request.session['last_booking_id'] = booking.id
                return redirect('booking_confirmed', booking_id=booking.id)
    else:
        initial = {}
        if request.GET.get('restaurant'):
            initial['restaurant'] = request.GET['restaurant']
        form = BookingForm(initial=initial)

    return render(request, 'restaurant_app/book.html', {'form': form})


def booking_confirmed(request, booking_id):
    """Confirmation page. Only visible to the browser that made the booking."""
    if request.session.get('last_booking_id') != booking_id:
        return redirect('home')
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'restaurant_app/confirmed.html', {'booking': booking})
