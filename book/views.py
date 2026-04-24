import logging
from io import BytesIO
from datetime import datetime, timedelta, date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.utils.crypto import get_random_string
from django.conf import settings
from django.urls import reverse_lazy
from twilio.rest import Client

from book.forms import BusForm, DepartureForm
from book.models import Bus, Destination, Booking, Seat, Book, Payment, Cancelled
from book.constants import TIME_SESSIONS, BOOKING_STATUS, PAYMENT_TYPES, COMPANY_STATUS
from book.templatetags.myapptags import todays_date, todays_time, url, get_company
from company.models import Company, Place
from user.models import ClientProfile

logger = logging.getLogger(__name__)

# Booking Constants
CANCELLATION_PERIOD_DAYS = 2
BOOK_EXPIRY_MINUTES = 5


def _search_buses(destination_id, departure_date=None, available_only=True):

    """
    Helper function to search buses by destination and optional date.
    Reduces code duplication in search view.
    """
    query = Bus.objects.filter(destination_id=destination_id)
    if available_only:
        query = query.filter(available=True)
    if departure_date:
        query = query.filter(departure_Date=departure_date)
    return query


def search(request):
    """Search for available buses by destination and optional date."""
    if request.method == 'POST':
        query = request.POST.get('q', '').strip()
        query2 = request.POST.get('q2', '').strip()
        query3 = request.POST.get('q3', '').strip()

        # Validation
        if not query or not query2:
            messages.warning(request, 'Please select both departure and destination.')
            return HttpResponseRedirect(url(request))
        
        if query == query2:
            messages.warning(request, 'Departure and destination cannot be the same place.')
            return HttpResponseRedirect(url(request))

        # Check if destination exists
        try:
            destination = Destination.objects.get(D_from_id=query, D_to=query2)
        except Destination.DoesNotExist:
            messages.warning(request, "Our service has not reached this route at the moment.")
            return HttpResponseRedirect(url(request))

        # Search buses
        searched_buses = _search_buses(destination.id, query3 if query3 else None)
        
        if not searched_buses.exists():
            messages.info(request, 'No buses available for this route at the moment.')
            return HttpResponseRedirect(url(request))

        context = {
            'companies': Company.objects.all(),
            'search': searched_buses,
        }
        return render(request, 'busbooking/listing.html', context)
    else:
        # GET request - show all available buses
        context = {
            'companies': Company.objects.all(),
            'buses': Bus.objects.filter(available=True)
        }
        return render(request, 'busbooking/listing.html', context)


def index(request):
    buses = Bus.objects.filter(available=True, departure_Date__gte=todays_date(request))
    place = Place.objects.all()
    company = Company.objects.all()

    context = { 'buses': buses,
                'place': place,
                'companies': company
               }
    return render(request, 'busbooking/index.html', context)


def about_us(request):
    return render(request, 'busbooking/about_us.html')


def contact_us(request):
    return render(request, 'busbooking/contact_us.html')


# Bus Functions Bus details, add bus, etc
@login_required(login_url='/login')
def bus_details(request, id):
    bus = get_object_or_404(Bus, id=id)
    return render(request, 'busbooking/bus_details.html', {
        'Bus': bus
    })


@login_required(login_url=reverse_lazy('login'))
def add_bus(request):
    """Add a new bus to the system."""
    if request.method == "POST":
        form_var = BusForm(request.POST, request.FILES)
        if form_var.is_valid():
            bus = form_var.save(commit=False)
            bus.available_Seat = bus.capacity
            bus.company = get_company(request)
            bus.save()
            
            # Create seat records if they don't exist
            if not Seat.objects.exists():
                seats_to_create = [Seat(number=i) for i in range(1, 121)]
                Seat.objects.bulk_create(seats_to_create)
                logger.info(f'Created {len(seats_to_create)} seat records')

            messages.success(request, 'Bus added successfully!')
            return HttpResponseRedirect('/company/panel/buses')
        else:
            messages.error(request, f'Error adding bus: {form_var.errors}')
            logger.warning(f'Bus form errors: {form_var.errors}')
    else:
        form_var = BusForm()
    
    return render(request, 'busbooking/add_bus.html', {'formBus': form_var})


@login_required(login_url=reverse_lazy('login'))
def edit_bus(request, id):
    """Edit an existing bus."""
    bus = get_object_or_404(Bus, id=id)
    if request.method == "POST":
        form_var = BusForm(request.POST, instance=bus)
        if form_var.is_valid():
            updated_bus = form_var.save()
            messages.success(request, 'Bus updated successfully!')
            return render(request, 'busbooking/bus_details.html', {'Bus': updated_bus})
        else:
            messages.error(request, f'Error updating bus: {form_var.errors}')
            logger.warning(f'Bus edit form errors: {form_var.errors}')
    else:
        form_var = BusForm(instance=bus)
    
    return render(request, 'busbooking/add_bus.html', {'formBus': form_var, 'edit': bus})


@login_required(login_url=reverse_lazy('login'))
def delete_bus(request, id):
    """Delete a bus from the system."""
    bus = get_object_or_404(Bus, id=id)
    try:
        bus.delete()
        messages.success(request, 'Bus deleted successfully!')
        logger.info(f'Bus {id} deleted by {request.user.username}')
    except Exception as e:
        messages.error(request, f'Error deleting bus: {str(e)}')
        logger.error(f'Error deleting bus {id}: {str(e)}')
    
    return HttpResponseRedirect("/panel")


@login_required(login_url=reverse_lazy('login'))
def change_departure(request, id):
    """Change bus departure details."""
    bus = get_object_or_404(Bus, id=id)
    company = bus.company
    
    if request.method == "POST":
        formDep = DepartureForm(company, request.POST, instance=bus)
        if formDep.is_valid():
            updated_bus = formDep.save()
            messages.success(request, 'Departure details updated!')
            return render(request, 'busbooking/bus_details.html', {'Bus': updated_bus})
        else:
            messages.error(request, f'Error updating departure: {formDep.errors}')
            logger.warning(f'Departure form errors: {formDep.errors}')
    else:
        formDep = DepartureForm(company, instance=bus)
    
    return render(request, 'busbooking/departure.html', {'Bus': bus, 'form_dep': formDep})


# BOOKING
@login_required(login_url=reverse_lazy('login'))
def book(request, id: int) -> HttpResponse:
    """
    Handle bus booking process.
    Supports both random and selected seat booking models.
    """
    bus = get_object_or_404(Bus, id=id)
    
    try:
        bus_company = Company.objects.get(id=bus.company_id)
    except Company.DoesNotExist:
        messages.error(request, "Company information not found.")
        logger.error(f"Company not found for bus {id}")
        return HttpResponseRedirect('/')
    
    # Get already booked seats
    booked_seats = list(
        Booking.objects.filter(bus=bus).values_list('seat', flat=True)
    )
    booked_seat_set = set(booked_seats)
    
    # Cleanup expired bookings (older than expiry period)
    expiry_time = datetime.now() - timedelta(minutes=BOOK_EXPIRY_MINUTES)
    deleted_count, _ = Book.objects.filter(book_Time__lt=expiry_time).delete()
    if deleted_count > 0:
        logger.info(f'Deleted {deleted_count} expired bookings for bus {id}')

    if request.method == "POST":
        ticket_user = request.POST.get('username', '').strip()
        booking_seat = request.POST.get('seats', '').strip()
        selected_seats = request.POST.getlist('seatNo')
        
        # Validate user input
        if not ticket_user:
            messages.warning(request, 'Please enter a passenger name.')
            return HttpResponseRedirect(url(request))
        
        # Check if any selected seats are already booked
        duplicate_seats = [s for s in selected_seats if s in booked_seat_set]
        if duplicate_seats:
            messages.warning(request, f'Seats {", ".join(duplicate_seats)} are already booked.')
            logger.warning(f'Duplicate seat attempt: {duplicate_seats}')
            return HttpResponseRedirect(url(request))
        
        # Validate booking qty
        if bus_company.seat_selection == "Random":
            if not booking_seat:
                messages.warning(request, 'Please select number of seats.')
                return HttpResponseRedirect(url(request))
            try:
                seat_qty = int(booking_seat)
                if seat_qty <= 0 or seat_qty > bus.available_Seat:
                    messages.warning(request, f'Invalid seat quantity. Available: {bus.available_Seat}')
                    return HttpResponseRedirect(url(request))
            except ValueError:
                messages.warning(request, 'Invalid seat quantity.')
                return HttpResponseRedirect(url(request))
        else:
            if not selected_seats:
                messages.warning(request, 'Please select at least one seat.')
                return HttpResponseRedirect(url(request))
        
        # Verify booking time
        get_date = todays_date(request)
        get_time = todays_time(request)
        
        if get_date >= bus.departure_Date and get_time >= bus.departure_Time:
            bus.available = False
            bus.save()
            messages.warning(request, "Cannot book this bus - departure time has passed.")
            logger.warning(f'Late booking attempt for bus {id}')
            return HttpResponseRedirect('/')
        
        if bus.seats_Sold >= bus.capacity:
            bus.available = False
            bus.save()
            messages.warning(request, "Bus is full. Cannot complete booking.")
            logger.info(f'Bus {id} is full')
            return HttpResponseRedirect('/')
        
        # Create booking
        try:
            user = request.user
            client = ClientProfile.objects.get(user=user)
        except ClientProfile.DoesNotExist:
            messages.error(request, "Client profile not found.")
            logger.error(f'ClientProfile not found for user {user.id}')
            return HttpResponseRedirect('/')
        
        new_book = Book()
        new_book.client = client
        new_book.company = bus_company
        new_book.driver = bus.driver
        new_book.bus = bus
        new_book.destination = bus.destination
        new_book.departure_Date = bus.departure_Date
        new_book.time_Session = bus.time_Session
        new_book.ticket_user = ticket_user
        
        # Calculate amount and seat string
        if bus_company.seat_selection == "Random":
            new_book.seat = booking_seat
            try:
                new_book.amount = float(bus.price) * int(booking_seat)
            except (ValueError, TypeError):
                messages.error(request, 'Invalid price calculation.')
                logger.error(f'Price calculation error for bus {id}')
                return HttpResponseRedirect(url(request))
        else:
            new_book.seat = ','.join(selected_seats)
            new_book.amount = float(bus.price) * len(selected_seats)
        
        new_book.save()
        logger.info(f'Book created: {new_book.id} for user {user.username}')
        
        # Handle payment
        try:
            tp_cash = Cancelled.objects.filter(client=client).first()
            cash_available = tp_cash and tp_cash.TP_cash >= new_book.amount
            
            payment = Payment()
            payment.client = client
            payment.bus = new_book.bus
            payment.amount = int(new_book.amount)
            payment.email = user.email or ''
            
            if cash_available:
                payment.payment_type = "TP-Cash"
            else:
                payment.payment_type = "MoMo"
            
            payment.save()
            logger.info(f'Payment created: {payment.ref}')
            
            return render(request, "busbooking/book/make_payment.html", {
                'Reservation': new_book,
                'cash': cash_available,
                'payment': payment,
                'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY
            })
        except Exception as e:
            messages.error(request, 'Error processing payment. Please try again.')
            logger.error(f'Payment processing error: {str(e)}')
            new_book.delete()
            return HttpResponseRedirect(url(request))
    
    else:  # GET request - show booking form
        check_seats = Seat.objects.values_list('number', flat=True).order_by('number')
        bus_cap = bus.capacity
        available_seats = list(range(1, bus_cap + 1))
        
        context = {
            'bus': bus,
            'seats': available_seats,
            'is_booked': booked_seats,
            'random': bus_company.seat_selection == "Random"
        }
        return render(request, 'busbooking/book/new.html', context)


@login_required(login_url=reverse_lazy('login'))
def book_details(request: HttpRequest, id: int, ref: str) -> HttpResponse:
    """
    Process booking payment and create confirmed reservation.
    Handles both cash and online payment methods.
    """
    try:
        payment = get_object_or_404(Payment, ref=ref)
        book = get_object_or_404(Book, id=id)
        
        # Payment already verified
        if payment.verified:
            return HttpResponseRedirect('/userbookings')
        
        user = request.user
        try:
            client = ClientProfile.objects.get(user=user)
        except ClientProfile.DoesNotExist:
            messages.error(request, "Client profile not found.")
            logger.error(f'ClientProfile not found for user {user.id}')
            return HttpResponseRedirect('/')
        
        try:
            bus_company = Company.objects.get(id=book.bus.company_id)
        except Company.DoesNotExist:
            messages.error(request, "Company information not found.")
            logger.error(f'Company not found for book {id}')
            return HttpResponseRedirect('/')
        
        # Handle TP-Cash payment
        if payment.payment_type == 'TP-Cash':
            try:
                user_cash = Cancelled.objects.get(client=client)
                if user_cash.TP_cash < book.amount:
                    messages.error(request, "Insufficient cash balance.")
                    return HttpResponseRedirect('/')
                user_cash.TP_cash -= book.amount
                user_cash.save()
                logger.info(f'TP-Cash payment: {book.amount} deducted')
            except Cancelled.DoesNotExist:
                messages.error(request, "No cash account found.")
                return HttpResponseRedirect('/')
        
        # Mark payment as verified
        payment.verified = True
        payment.save()
        
        # Generate unique booking code
        booking_code = None
        for _ in range(10):  # Prevent infinite loop
            code = get_random_string(10).upper()
            if not Booking.objects.filter(book_code=code).exists():
                booking_code = code
                break
        
        if not booking_code:
            messages.error(request, "Error generating booking code.")
            logger.error('Failed to generate unique booking code')
            return HttpResponseRedirect('/')
        
        # Create confirmed booking
        booking = Booking()
        booking.client = client
        booking.ticket_user = book.ticket_user
        booking.company = book.company
        booking.driver = book.driver
        booking.amount = book.amount
        booking.bus = book.bus
        booking.destination = book.destination
        booking.departure_Date = book.departure_Date
        booking.time_Session = book.time_Session
        booking.book_code = booking_code
        
        # Handle seat assignment based on company preference
        if bus_company.seat_selection == "Random":
            booking.seat = book.seat
        else:
            booking.seat = book.seat
        
        booking.status = 'Active'
        booking.save()
        logger.info(f'Booking confirmed: {booking_code} for user {user.username}')
        
        # Update bus seat counts
        try:
            bus = book.bus
            seat_count = book.amount / bus.price
            bus.seats_Sold += int(seat_count)
            bus.available_Seat -= int(seat_count)
            
            # Mark bus as unavailable if full
            if bus.seats_Sold >= bus.capacity:
                bus.available = False
            
            bus.save()
            logger.info(f'Bus {bus.id} updated: {int(seat_count)} seats booked')
        except Exception as e:
            messages.error(request, "Error updating bus seats.")
            logger.error(f'Error updating bus seats: {str(e)}')
            return HttpResponseRedirect('/userbookings')
        
        # Send SMS confirmation
        try:
            client_account = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
            
            if bus_company.seat_selection == "Random":
                msg = (f"You have successfully booked with {booking.company}. "
                       f"Seats: {booking.seat}. Code: {booking.book_code}. "
                       f"Thank you!")
            else:
                msg = (f"You have successfully booked with {booking.company}. "
                       f"Seat(s): {booking.seat}. Code: {booking.book_code}. "
                       f"Thank you!")
            
            phone = f"+233{client.phone}" if str(client.phone).startswith("0") else f"+{client.phone}"
            client_account.messages.create(
                body=msg,
                from_=settings.TWILIO_FROM_NUMBER,
                to=phone
            )
            logger.info(f'SMS sent to {phone}')
        except Exception as e:
            logger.warning(f'SMS send failed: {str(e)}')
            # Don't fail the booking if SMS fails
        
        messages.success(request, f'Booking confirmed! Code: {booking_code}')
        return render(request, 'busbooking/book/details.html', {'Reservation': booking})
    
    except Exception as e:
        messages.error(request, f"Booking error: {str(e)}")
        logger.error(f'Booking details error: {str(e)}', exc_info=True)
        return HttpResponseRedirect('/')


@login_required(login_url=reverse_lazy('login'))
def cancel(request, id: int):
    """
    Cancel a booking with refund.
    Checks if cancellation is within allowed period (2 days before departure).
    """
    try:
        booking = Booking.objects.get(id=id)
    except Booking.DoesNotExist:
        messages.error(request, "Booking not found.")
        return HttpResponseRedirect(url(request))
    
    # Check if booking is still cancellable
    if booking.status != 'Active':
        messages.error(request, f"Cannot cancel {booking.status} booking.")
        logger.warning(f'Cancellation attempt on {booking.status} booking {id}')
        return HttpResponseRedirect(url(request))
    
    # Check cancellation period (must be 2+ days before departure)
    cancellation_deadline = booking.bus.departure_Date - timedelta(days=CANCELLATION_PERIOD_DAYS)
    today = date.today()
    
    if today > cancellation_deadline:
        messages.error(request, "Cancellation period has passed (must be 2+ days before departure).")
        logger.info(f'Late cancellation attempt for booking {id}')
        return HttpResponseRedirect(url(request))
    
    try:
        # Update booking status
        booking.status = 'Cancelled'
        booking.save()
        logger.info(f'Booking {id} cancelled by {request.user.username}')
        
        # Process refund
        try:
            cancelled_record = Cancelled.objects.filter(client=booking.client).first()
            
            if cancelled_record:
                cancelled_record.TP_cash += booking.amount
                cancelled_record.save()
            else:
                cancelled_record = Cancelled()
                cancelled_record.client = booking.client
                cancelled_record.TP_cash = booking.amount
                cancelled_record.save()
            
            logger.info(f'Refund processed: {booking.amount} for user {booking.client.user.username}')
        except Exception as e:
            logger.error(f'Refund processing error: {str(e)}')
            messages.warning(request, 'Cancellation processed but refund may need manual review.')
        
        # Update bus seat availability
        try:
            bus = booking.bus
            seat_count = int(booking.amount / bus.price)
            bus.seats_Sold -= seat_count
            bus.available_Seat += seat_count
            
            # Make bus available again if seats freed up
            if bus.available_Seat > 0:
                bus.available = True
            
            bus.save()
            logger.info(f'Bus {bus.id}: {seat_count} seats released')
        except Exception as e:
            logger.error(f'Bus update error during cancellation: {str(e)}')
        
        # Send SMS notification
        try:
            client_account = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
            phone = f"+233{booking.client.phone}" if str(booking.client.phone).startswith("0") else f"+{booking.client.phone}"
            
            msg = f"Your booking {booking.book_code} has been cancelled. Refund of {booking.amount} will be credited."
            client_account.messages.create(
                body=msg,
                from_=settings.TWILIO_FROM_NUMBER,
                to=phone
            )
            logger.info(f"Cancellation SMS sent to {phone}")
        except Exception as e:
            logger.warning(f"SMS notification failed: {str(e)}")
        
        messages.success(request, f'Booking cancelled successfully. Refund: {booking.amount}')
        return HttpResponseRedirect(url(request))
    
    except Exception as e:
        messages.error(request, f"Error processing cancellation: {str(e)}")
        logger.error(f'Cancellation error for booking {id}: {str(e)}', exc_info=True)
        return HttpResponseRedirect(url(request))


@login_required(login_url=reverse_lazy('login'))
def user_booking(request):
    """Display user bookings and cancellations."""
    try:
        user_profile = ClientProfile.objects.get(user=request.user)
    except ClientProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        logger.error(f'ClientProfile not found for user {request.user.id}')
        return HttpResponseRedirect('/')
    
    # Get recent bookings
    try:
        bookings = Booking.objects.filter(
            client=user_profile
        ).select_related(
            'bus', 'company', 'client'
        ).order_by('-book_Date')[:10]
    except Exception as e:
        bookings = []
        logger.error(f'Error retrieving bookings: {str(e)}')
        messages.warning(request, 'Error loading bookings. Please try again.')
    
    context = {
        'bookings': bookings,
        'active_status': 'Active',
        'cancelled_status': 'Cancelled'
    }
    
    return render(request, 'busbooking/book/user_bookings.html', context)
