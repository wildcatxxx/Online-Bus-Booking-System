"""
Constants for the booking system.
Centralized configuration and choices for models and forms.
"""

# Time session choices for bus departures
TIME_SESSIONS = (
    ('Morning', 'Morning'),
    ('Afternoon', 'Afternoon'),
    ('Evening', 'Evening'),
)

# Booking status choices
BOOKING_STATUS = (
    ('Active', 'Active'),
    ('In-use', 'In-use'),
    ('Cancelled', 'Cancelled'),
    ('Expired', 'Expired'),
)

# Payment type choices
PAYMENT_TYPES = (
    ('TP-Cash', 'TP-Cash'),
    ('MoMo', 'MoMo'),
)

# Company seat selection status
COMPANY_STATUS = (
    ('Random', 'Random'),
    ('Selected', 'Selected'),
)
