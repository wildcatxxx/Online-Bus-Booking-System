# Online Booking System - Fixes & Updates Checklist

## 🔴 CRITICAL SECURITY ISSUES (Do First)

### Credentials & Environment Variables
- [ ] Create `.env` file in project root with:
  - `SECRET_KEY=<generate-new-secure-key>`
  - `DEBUG=False`
  - `ALLOWED_HOSTS=localhost,127.0.0.1`
  - `PAYSTACK_PUBLIC_KEY=<move-here>`
  - `PAYSTACK_PRIVATE_KEY=<move-here>`
  - `ACCOUNT_SID=<move-here>`
  - `AUTH_TOKEN=<move-here>`

- [ ] Install `python-decouple`: `pip install python-decouple`

- [ ] Update `online_booking/settings.py`:
  - Import: `from decouple import config`
  - Change `SECRET_KEY = config('SECRET_KEY')`
  - Change `DEBUG = config('DEBUG', default=False, cast=bool)`
  - Change `ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')`
  - Update all API keys to use `config()`

- [ ] Create `.gitignore`:
  ```
  .env
  *.pyc
  __pycache__/
  *.sqlite3
  db.sqlite3
  .DS_Store
  venv/
  .idea/
  *.egg-info/
  /uploads/
  /static/
  ```

- [ ] Add `.gitignore` to git and remove tracked `.env`
  ```bash
  git rm --cached .env
  git add .gitignore
  ```

### XSS Vulnerability Fix
- [ ] Update `user/models.py` - `ClientProfile.image_tag()`:
  - Use template filter instead of `mark_safe()`
  - Or use Django's `format_html()` with escaped URL

---

## 🟠 MODEL DESIGN ISSUES

### company/models.py
- [ ] Remove `max_length` from ForeignKey fields:
  - Line 23: `userid` field - remove `max_length` param
  - Line 25: `contact_1/2/3/4` - Change from `PositiveIntegerField` to `CharField(max_length=20)`
  - Line 30: `phone_1/2` - Change from `PositiveIntegerField` to `CharField(max_length=20)`

- [ ] Remove malformed comment:
  - Line 4: Delete `# Create your models hereRandom.`

### book/models.py
- [ ] Fix `Book` model (Line ~75):
  - Change `ticket_user = models.CharField(max_length=50, default=client)`
  - To: `ticket_user = models.CharField(max_length=50, default='')`

- [ ] Fix multiple ForeignKey `max_length` issues:
  - Line ~47: Remove `max_length=50` from `destination` FK
  - Line ~50: Remove `max_length=50` from `driver` FK
  - Line ~109: Remove `max_length=100` from `driver` FK

- [ ] Fix `Bus.departure_Time`:
  - Change `departure_Time = models.TimeField(blank=True, default=time)`
  - To: `departure_Time = models.TimeField(blank=True, default='00:00:00')`

- [ ] Fix `Books.book_Date` and `book_Time`:
  - Change `auto_now=True` to `auto_now_add=True` (created once, not updated)
  - Or reconsider: do you need both creation date/time?

- [ ] Fix `Payment.client`:
  - Change `models.OneToOneField` to `models.ForeignKey`
  - Allows multiple payments per client

- [ ] Fix `Cancelled.client`:
  - Change `models.OneToOneField` to `models.ForeignKey`
  - Allows multiple cancellations per client

- [ ] Create `BusSeat` model (for better seat management):
  ```python
  class BusSeat(models.Model):
      bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='seats')
      seat_number = models.PositiveIntegerField()
      is_booked = models.BooleanField(default=False)
      
      class Meta:
          unique_together = ('bus', 'seat_number')
  ```

### user/models.py
- [ ] Remove unused regex validator:
  - Line 9: Delete `num = RegexValidator(r'^[0-9]*$', '')`
  - Line 9: Remove commented usage if any

- [ ] Refactor `userid` generation in both models (DRY principle):
  - Create utility function: `generate_unique_userid()`

- [ ] Change `emergency_contact_phone` from `PositiveIntegerField` to `CharField`

---

## 🟡 CODE QUALITY ISSUES

### book/views.py
- [ ] Remove unused import (Line 3):
  - `from typing: re` should be removed (typo/unused)

- [ ] Remove debug print statement (Line 62):
  - Delete: `print(f'destination id: {destination.id}')`
  - Replace with logging if needed

- [ ] Refactor search logic:
  - Consolidate repetitive destination checks
  - Extract to separate function/method

- [ ] Add logging instead of prints:
  ```python
  import logging
  logger = logging.getLogger(__name__)
  logger.info(f'destination id: {destination.id}')
  ```

### book/paystack.py
- [ ] Fix status code comparison (Line 19):
  - Change: `if response.status_code == '200':`
  - To: `if response.status_code == 200:`

### book/forms.py
- [ ] Update placeholder texts that say "phone" for non-phone fields

### Constants / Magic Strings
- [ ] Create `book/constants.py`:
  ```python
  TIME_SESSIONS = (
      ('Morning', 'Morning'),
      ('Afternoon', 'Afternoon'),
      ('Evening', 'Evening'),
  )
  
  BOOKING_STATUS = (
      ('Active', 'Active'),
      ('In-use', 'In-use'),
      ('Cancelled', 'Cancelled'),
      ('Expired', 'Expired'),
  )
  
  PAYMENT_TYPES = (
      ('TP-Cash', 'TP-Cash'),
      ('MoMo', 'MoMo'),
  )
  
  COMPANY_STATUS = (
      ('Random', 'Random'),
      ('Selected', 'Selected'),
  )
  ```

- [ ] Update all models to import and use these constants

---

## 📁 PROJECT STRUCTURE ISSUES

### Configuration Files
- [ ] Create `requirements.txt`:
  ```
  Django==3.2.4
  python-decouple==3.8
  Pillow==9.0.0
  qrcode==7.3.1
  requests==2.28.0
  twilio==8.9.0
  django-environ==0.9.0
  ```

- [ ] Create `README.md` with:
  - Project description
  - Setup instructions
  - Environment variables needed
  - Database setup
  - How to run server

- [ ] Create `.env.example`:
  ```
  SECRET_KEY=your-secret-key-here
  DEBUG=False
  ALLOWED_HOSTS=localhost,127.0.0.1
  PAYSTACK_PUBLIC_KEY=your-key
  PAYSTACK_PRIVATE_KEY=your-key
  ACCOUNT_SID=your-sid
  AUTH_TOKEN=your-token
  DATABASE_URL=sqlite:///db.sqlite3
  ```

### Duplicate/Cleanup
- [ ] Verify which is active: `online_booking/` or `ticket_booking/`
  - Delete the unused one or document why both exist

- [ ] Review and document why there are duplicate templates in:
  - `templates/busbooking/` vs `templates/busreserv/`

### Database Migrations
- [ ] List duplicates:
  - `0002_auto_20210421_2351.py` AND `0002_book_ticket_user.py`
  - `0003_auto_20210422_0047.py` AND `0003_auto_20210831_2353.py`
  - `0004_auto_20210901_0000.py` AND `0004_remove_reservation_departuredate.py`
  - `0005_auto_20210901_0004.py` AND `0005_reservation_depdate.py`
  - `0006_alter_reservation_time_session.py` AND `0006_auto_20210901_0006.py`

- [ ] Squash and clean migrations (after backup):
  ```bash
  python manage.py squashmigrations book <first_migration> <last_migration>
  ```

- [ ] Rename conflicting migrations to have sequential prefixes

---

## ✅ CODE STANDARDS

### Naming Conventions
- [ ] Standardize field names to lowercase with underscores:
  - `plate_No` → `plate_number`
  - `departure_Date` → `departure_date`
  - `departure_Time` → `departure_time`
  - `seats_Sold` → `seats_sold`
  - `available_Seat` → `available_seats`
  - `book_Date` → `book_date`
  - `book_Time` → `book_time`
  - `time_Session` → `time_session`
  - `qr_code` → `qr_code` (OK)
  - `book_code` → `book_code` (OK)
  - `D_from` → `from_place`
  - `D_to` → `to_place`

- [ ] Add docstrings to all models

- [ ] Add docstrings to all view functions

### Documentation
- [ ] Add model docstrings explaining purpose
- [ ] Add relationship diagrams in README
- [ ] Document API endpoints

---

## 🚀 DEPLOYMENT CHECKLIST

- [ ] Set `DEBUG = False` in production
- [ ] Update `ALLOWED_HOSTS` with actual domain
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure static files for production (collectstatic)
- [ ] Set up media files handling
- [ ] Configure email backend
- [ ] Enable HTTPS/SSL
- [ ] Set secure headers (CSRF, clickjacking, etc.)
- [ ] Review `CORS` settings if API
- [ ] Set up logging/monitoring
- [ ] Create admin user
- [ ] Test backup/restore process

---

## 📊 PRIORITY LEVELS

```
IMMEDIATE (Security - This Week):
  ✓ Move credentials to .env
  ✓ Create .gitignore
  ✓ Fix Book.ticket_user default
  ✓ Remove XSS vulnerability

SHORT TERM (This Month):
  ✓ Fix model field issues
  ✓ Create requirements.txt
  ✓ Fix code quality issues
  ✓ Add logging

MEDIUM TERM (Next Month):
  ✓ Rename fields for consistency
  ✓ Squash migrations
  ✓ Create comprehensive documentation

LONG TERM (Later):
  ✓ Upgrade Django version
  ✓ Add tests
  ✓ API documentation
```

---

**Last Updated:** April 23, 2026
**Status:** Ready for implementation
