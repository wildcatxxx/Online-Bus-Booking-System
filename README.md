# Online Booking System

A professional Django-based bus booking system with advanced seat management, payment processing, and SMS notifications.

## 🎯 Features

- **Advanced Bus Search**: Search buses by destination, date, and availability
- **Flexible Seat Management**: Support for both random seat allocation and specific seat selection
- **Payment Integration**: Integrated Paystack for online payments with cash alternative
- **QR Code Tickets**: Auto-generated QR codes for booking confirmation
- **SMS Notifications**: Real-time SMS updates via Twilio for bookings and cancellations
- **Company Management**: Multi-company support with independent configurations
- **Booking Cancellation**: Refund processing with 2-day cancellation window
- **User Profiles**: Comprehensive user management for customers, companies, and staff
- **Comprehensive Logging**: Request and error logging for debugging and monitoring

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Django 3.2.4 |
| **Database** | SQLite (dev), PostgreSQL (prod) |
| **Authentication** | Django Auth + Custom Profiles |
| **Payment** | Paystack API |
| **SMS** | Twilio |
| **Media Handling** | Pillow + ImageField |
| **QR Codes** | qrcode library |
| **Configuration** | python-decouple |
| **Logging** | Python logging + RotatingFileHandler |

## 📋 Prerequisites

- Python 3.8+
- pip package manager
- Virtual environment support
- Paystack account (for payments)
- Twilio account (for SMS)

## 🚀 Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/wildcatxxx/Online-Bus-Booking-System.git
cd Online-Bus-Booking-System
```

### 2. Create Virtual Environment

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy example to actual config
cp .env.example .env
```

Edit `.env` file with your values:

```env
# Security
SECRET_KEY=your-secure-secret-key-here
DEBUG=True  # Set to False in production
ALLOWED_HOSTS=localhost,127.0.0.1

# Payment Gateway (Paystack)
PAYSTACK_PUBLIC_KEY=pk_test_xxxxxxxxxxxxxxxx
PAYSTACK_PRIVATE_KEY=sk_test_xxxxxxxxxxxxxxxx

# SMS Service (Twilio)
ACCOUNT_SID=ACxxxxxxxxxxxxxxxxx
AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxx
TWILIO_FROM_NUMBER=+1234567890

# Database
DATABASE_URL=sqlite:///db.sqlite3
```

### 5. Initialize Database

```bash
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
# Enter username, email, password
```

### 7. Prepare Logging Directory

```bash
mkdir -p logs
```

### 8. Collect Static Files (Production)

```bash
python manage.py collectstatic
```

## ▶️ Running the Application

### Development Server

```bash
# Activate virtual environment first
source venv/bin/activate

# Run server
python manage.py runserver

# Or specify host/port
python manage.py runserver 0.0.0.0:8000
```

Server will be available at: `http://localhost:8000`

Admin panel: `http://localhost:8000/admin`

### Production Server

Use Gunicorn:

```bash
pip install gunicorn
gunicorn online_booking.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## 📁 Project Architecture

```
online_booking_system/
├── book/                           # Booking & bus management
│   ├── models.py                  # Bus, Booking, Payment models
│   ├── views.py                   # Refactored booking views (IMPROVED)
│   ├── forms.py                   # Booking & bus forms
│   ├── urls.py                    # Booking URL patterns
│   ├── constants.py               # Centralized choice definitions
│   ├── paystack.py                # Payment gateway integration
│   └── templates/book/            # Booking templates
│
├── company/                        # Company management
│   ├── models.py                  # Company, Driver, Place models
│   ├── views.py                   # Company operations
│   ├── forms.py                   # Company forms
│   └── templates/company/         # Company templates
│
├── user/                           # User management
│   ├── models.py                  # User profiles (ClientProfile, etc)
│   ├── views.py                   # Authentication views
│   └── templates/user/            # User templates
│
├── online_booking/                # Project settings
│   ├── settings.py                # Django configuration (UPDATED)
│   ├── urls.py                    # Main URL routing
│   ├── wsgi.py                    # WSGI configuration
│   └── asgi.py                    # ASGI configuration
│
├── templates/                      # Base templates
├── static/                         # CSS, JS, images
├── logs/                           # Application logs
├── uploads/                        # User uploads
│
├── manage.py                       # Django management script
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (not tracked)
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
└── IMPLEMENTATION_SUMMARY.md       # Recent changes documentation
```

## 🔄 Key Improvements (Recent Refactoring)

### Views Enhancement (`book/views.py`)

✅ **Search Optimization**
- Refactored repetitive search logic into `_search_buses()` helper
- Better validation and error messages
- Eliminated code duplication

✅ **Booking Flow**
- Comprehensive input validation
- Proper error handling with try/except blocks
- Clear duplicate seat detection
- Improved payment processing flow

✅ **Cancellation Logic**
- Fixed date comparison for cancellation deadline
- Proper refund processing
- Clear status checking before cancellation
- SMS notification on cancellation

✅ **Error Handling**
- All database queries wrapped in try/except
- User-friendly error messages
- Detailed logging for debugging
- Graceful degradation (SMS failure doesn't block booking)

✅ **Logging & Monitoring**
- Comprehensive logging configuration in settings
- RotatingFileHandler for log file management
- Different log levels for different modules
- Request tracking for debugging

### Configuration Improvements (`online_booking/settings.py`)

✅ **Security**
- All credentials moved to environment variables
- Uses `python-decouple` for safe configuration
- Secret key, API keys, tokens all externalized

✅ **Logging Configuration**
- Console and file logging
- Log rotation (15MB per file, 10 backups)
- Different formatters for verbose and simple output
- Separated loggers for Django and booking app

✅ **Constants Management**
- Centralized choice definitions in `book/constants.py`
- No magic strings in models/views
- Easy to maintain and update

## 🔐 Security Checklist

| Item | Status |
|------|--------|
| Secret key externalized | ✅ |
| Debug mode configurable | ✅ |
| Credentials in .env | ✅ |
| .gitignore configured | ✅ |
| CSRF protection | ✅ |
| SQL injection prevention | ✅ |
| Input validation | ✅ |
| Error logging | ✅ |

## 📊 Database Models

### Core Models

- **Bus**: Bus inventory with capacity, pricing, schedule
- **Destination**: Route definition (from/to places)
- **Booking**: Confirmed reservations with QR codes
- **Payment**: Payment records with verification
- **Seat**: Available seat inventory
- **Company**: Bus operator information
- **Driver**: Driver details
- **ClientProfile**: Customer information
- **CompanyProfile**: Company user account
- **Cancelled**: Cancellation & refund tracking

## 🧪 Testing the Application

### Manual Testing

```bash
# 1. Verify server starts
python manage.py runserver

# 2. Check admin panel
# Visit http://localhost:8000/admin
# Login with superuser credentials

# 3. Test booking flow
# - Search buses
# - Attempt booking
# - Verify logs in logs/booking.log

# 4. Check logging
tail -f logs/booking.log
```

### Automated Testing

```bash
# Run full test suite
python manage.py test

# Run specific app tests
python manage.py test book
python manage.py test company
python manage.py test user

# Run with verbosity
python manage.py test -v 2
```

## 📝 Logging

Application logs are stored in `logs/booking.log` with rotation:

- **Max size**: 15MB per file
- **Backup count**: 10 files
- **Format**: `LEVEL TIMESTAMP MODULE MESSAGE`

### View Logs

```bash
# Real-time log watching
tail -f logs/booking.log

# Last 100 lines
tail -100 logs/booking.log

# Search logs
grep ERROR logs/booking.log
grep "user_id:123" logs/booking.log
```

## 🚢 Deployment Checklist

### Pre-Deployment

- [ ] Set `DEBUG=False` in .env
- [ ] Update `ALLOWED_HOSTS` with domain
- [ ] Generate new `SECRET_KEY`
- [ ] Configure PostgreSQL database
- [ ] Set up email backend
- [ ] Enable HTTPS/SSL
- [ ] Configure static file storage (S3, Cloudinary)
- [ ] Set up media file storage
- [ ] Configure CDN for static files

### Environment Setup

```bash
# Copy .env to server
scp .env user@server:/app/

# Ensure permissions
chmod 600 /app/.env

# Run migrations on server
python manage.py migrate --settings=online_booking.settings
```

### Using Gunicorn + Nginx

```bash
# Install Gunicorn
pip install gunicorn

# Create systemd service
sudo nano /etc/systemd/system/booking.service
```

Service file example:
```ini
[Unit]
Description=Booking System
After=network.target

[Service]
User=www-data
WorkingDirectory=/app
ExecStart=/app/venv/bin/gunicorn online_booking.wsgi --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🐛 Troubleshooting

### Django Not Found

```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### Database Errors

```bash
# Reset database (development only)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Static Files Not Loading

```bash
python manage.py collectstatic --clear
```

### Port 8000 Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
python manage.py runserver 8001
```

### Logging Directory Missing

```bash
# Create logs directory
mkdir -p logs
chmod 755 logs
```

## 📞 Support & Troubleshooting

### Enable Debug Logging

Edit `.env`:
```env
DEBUG=True
```

Then check `logs/booking.log` for detailed errors.

### Clear Django Cache

```bash
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

### Database Backup

```bash
# Backup database
python manage.py dumpdata > backup.json

# Restore database
python manage.py loaddata backup.json
```

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Paystack API Docs](https://paystack.com/docs/api/)
- [Twilio SMS Docs](https://www.twilio.com/docs/sms)
- [Python Logging](https://docs.python.org/3/library/logging.html)

## 👥 Contributing

1. Create a feature branch
2. Make changes
3. Run tests
4. Submit pull request

## 👤 Authors

- **Wildcatxxx** - Project Lead & Development

---

**Created On**: June 16, 2021  
**Last Updated**: April 24, 2026  
**Status**: ✅ Production Ready  
**Version**: 2.0 (Refactored)
