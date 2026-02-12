# School Management System - Accountant Mode

## Overview
This is a streamlined Django-based school management system configured specifically for **accountant/financial staff only**. All unnecessary modules have been removed, leaving only billing, accounting, and financial reporting capabilities.

---

## System Configuration

### Installed Applications
- **accounts** - User authentication and role management
- **dashboard** - Main dashboard and statistics
- **schools** - Multi-school/organization management
- **students** - Minimal student registry (for billing purposes only)
- **accounting** - Advanced accounting with general ledger and journal entries
- **billing** - Invoice management and payment processing
- **reports** - Financial reports and analytics
- **settings_app** - System settings and configuration

### Removed Applications
All non-financial modules have been removed:
- academic, teachers, courses, batches, evaluation
- transport, hostel, zatca, enrollment, timetable
- attendance, marks, homework, leave, inventory
- workflow, maintenance, chatbot

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL database
- Virtual environment (recommended)

### Initial Setup

1. **Activate Virtual Environment**
   ```bash
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Configuration**
   The system is configured to use PostgreSQL:
   - Database: `mydb2`
   - User: `myuser`
   - Password: `mypassword`
   - Host: `localhost`
   - Port: `5432`

4. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start Development Server**
   ```bash
   python manage.py runserver 8001
   ```

6. **Access Application**
   - URL: http://127.0.0.1:8001/accounts/login/

---

## User Credentials

### Accountant User
- **Username:** `accountant`
- **Password:** `accountant123`
- **Email:** accountant@school.edu
- **Name:** Omar Al-Farouk
- **Employee ID:** ACC001
- **Department:** Finance
- **Role:** Accountant

### Permissions
Accountants have access to:
- ✅ Dashboard (view financial statistics)
- ✅ Billing (invoices, payments, fee categories)
- ✅ Accounting (journal entries, general ledger, fiscal years)
- ✅ Reports (financial reports only)
- ✅ Schools (organization and school management)

---

## Module Details

### 1. Dashboard
**URL:** `/`

**Features:**
- Financial overview and key metrics
- Monthly revenue statistics
- Pending payments summary
- Outstanding invoices count
- Quick access to all financial modules

**Available Stats:**
- Total invoices and payments
- Monthly/yearly revenue
- Outstanding balances
- Payment status breakdown

---

### 2. Billing Module
**URL:** `/billing/`

**Features:**
- **Fee Categories**: Define tuition, transport, books, etc.
- **Discounts**: Percentage or fixed amount discounts with validity periods
- **Invoices**: Create, edit, and manage student invoices
- **Payments**: Record and track payment transactions
- **Invoice Items**: Line items for each invoice

**Invoice Management:**
- Generate invoices for students
- Apply discounts
- Calculate VAT automatically
- Track payment status (pending, partial, paid, overdue)
- Payment history per invoice

**Payment Methods Supported:**
- Cash
- Bank Transfer
- Credit Card
- Cheque
- Online Payment

**Status Tracking:**
- Draft
- Pending Payment
- Partially Paid
- Fully Paid
- Overdue
- Cancelled

---

### 3. Accounting Module
**URL:** `/accounting/`

**Features:**
- **Chart of Accounts**: Manage account hierarchy
- **Fiscal Years**: Define and manage accounting periods
- **Journal Entries**: Double-entry bookkeeping
- **General Ledger**: View account balances and transactions
- **Accounting Periods**: Monthly/quarterly period management
- **Budget Lines**: Budget planning and tracking

**Account Types:**
- Assets
- Liabilities
- Equity
- Revenue
- Expenses

**Journal Entry Process:**
1. Create draft entry
2. Add debit and credit lines (must balance)
3. Review and post
4. Automatically updates general ledger

**Integration:**
- Auto-creates journal entries from invoices
- Links payments to accounting records
- Tracks student and payment references

---

### 4. Reports Module
**URL:** `/reports/`

**Features:**
- **Financial Reports**: Revenue, expenses, profit/loss
- **Fee Collection Reports**: Collection by period, category
- **Outstanding Reports**: Overdue invoices and balances
- **Payment Reports**: Payment history and methods
- **Report Templates**: Predefined report formats
- **Scheduled Reports**: Automated report generation
- **Export Options**: PDF, Excel, CSV formats

**Available Report Types:**
- Student financial reports
- Fee collection summaries
- Outstanding fees analysis
- Payment transaction logs
- Account-wise reports
- Period-wise comparisons

---

### 5. Schools Module
**URL:** `/schools/`

**Features:**
- **Organizations**: Manage parent organizations
- **Schools**: Individual school management under organizations
- **Academic Configuration**: Academic years, terms, calendars
- **School Branding**: Logos, colors, official information
- **School Admins**: Assign administrative users to schools

**Multi-School Support:**
- Separate financial records per school
- Consolidated reporting across schools
- Organization-level overview
- School-specific branding and settings

---

## Database Models

### Student (Minimal - Billing Only)
```python
- student_id: Unique identifier
- first_name, last_name: Student name
- email, phone: Contact information
- school: School association
- is_active: Active status
```

### Invoice
```python
- invoice_number: Auto-generated
- student: Student reference
- academic_year: Academic year
- invoice_date, due_date: Dates
- subtotal, discount_amount, vat_amount: Financial fields
- total_amount, paid_amount, balance_amount: Amounts
- status: Payment status
```

### Payment
```python
- payment_number: Auto-generated
- invoice: Invoice reference
- payment_date: Date of payment
- amount: Payment amount
- payment_method: Cash, transfer, card, etc.
- status: Completed, pending, cancelled
```

### Account (Chart of Accounts)
```python
- code: Account code
- name: Account name
- account_type: Asset, liability, equity, revenue, expense
- parent: Parent account (for hierarchy)
- is_active: Active status
```

### Journal Entry
```python
- entry_number: Auto-generated
- date: Transaction date
- description: Entry description
- status: Draft, posted, cancelled
- total_debit, total_credit: Must balance
```

---

## Common Tasks

### Creating an Invoice
1. Navigate to Billing → Invoices → Add Invoice
2. Select student
3. Set academic year and dates
4. Add invoice items (fee categories)
5. Apply discount if needed
6. VAT calculated automatically
7. Save and issue invoice

### Recording a Payment
1. Navigate to Billing → Payments → Add Payment
2. Select invoice
3. Enter payment amount
4. Choose payment method
5. Add reference number (if applicable)
6. Record payment

### Creating Journal Entries
1. Navigate to Accounting → Journal Entries → Add Entry
2. Select fiscal year and date
3. Add description
4. Add debit line(s)
5. Add credit line(s) (must balance)
6. Review totals
7. Post entry

### Generating Reports
1. Navigate to Reports
2. Choose report type
3. Select date range
4. Apply filters (school, status, etc.)
5. Preview report
6. Export to PDF/Excel

---

## API Endpoints

### Authentication
- `POST /accounts/login/` - User login
- `GET /accounts/logout/` - User logout

### Billing
- `GET /billing/invoices/` - List all invoices
- `POST /billing/invoices/create/` - Create invoice
- `GET /billing/invoices/{id}/` - View invoice details
- `GET /billing/payments/` - List all payments
- `POST /billing/payments/create/` - Record payment

### Accounting
- `GET /accounting/accounts/` - Chart of accounts
- `GET /accounting/journal-entries/` - List entries
- `POST /accounting/journal-entries/create/` - Create entry
- `GET /accounting/ledger/` - General ledger view

### Reports
- `GET /reports/financial/` - Financial reports
- `GET /reports/fee-collection/` - Fee collection reports
- `GET /reports/outstanding/` - Outstanding reports

---

## Security & Permissions

### Role-Based Access Control (RBAC)
- Only users with `accountant` role can access financial modules
- Admins have full access
- Other roles are blocked from financial data

### Permission Levels
```python
accountant_permissions = {
    'dashboard': 'view',
    'billing': 'full',
    'accounting': 'full',
    'reports': 'view',
    'schools': 'view',
}
```

### Data Protection
- Password hashing with Django's built-in system
- CSRF protection enabled
- Session-based authentication
- PostgreSQL role-based security

---

## Maintenance

### Creating Additional Accountant Users
```bash
python create_accountant_only.py
```

Or manually in Django admin or shell:
```python
from accounts.models import CustomUser

user = CustomUser.objects.create_user(
    username='accountant2',
    email='accountant2@school.edu',
    password='secure_password',
    first_name='First',
    last_name='Last',
    role='accountant',
    employee_id='ACC002',
    department='Finance'
)
```

### Database Backup
```bash
pg_dump -U myuser mydb2 > backup_$(date +%Y%m%d).sql
```

### Database Restore
```bash
psql -U myuser mydb2 < backup_20260211.sql
```

### Clearing Cache
```bash
python manage.py clear_cache  # If cache is configured
```

---

## Troubleshooting

### Cannot Login
- Verify username and password
- Check if user has `accountant` role
- Ensure user is active: `is_active=True`

### Module Access Denied
- Verify user role in admin panel
- Check ROLE_PERMISSIONS in `accounts/permissions.py`
- Clear browser cache and cookies

### Migration Errors
```bash
# Reset migrations (dev only)
python manage.py migrate --fake accounting zero
python manage.py migrate accounting
```

### Server Won't Start
```bash
# Check if port is already in use
lsof -i :8001

# Kill existing process
kill -9 <PID>

# Restart server
python manage.py runserver 8001
```

---

## Development

### Project Structure
```
Database1/
├── accounts/           # User authentication
├── accounting/         # Accounting system
├── billing/            # Billing & invoices
├── dashboard/          # Main dashboard
├── reports/            # Financial reports
├── schools/            # School management
├── settings_app/       # Settings
├── students/           # Minimal student model
├── theme/              # UI theme
├── templates/          # HTML templates
├── media/              # Uploaded files
├── Database1/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

### Key Configuration Files
- `Database1/settings.py` - Django settings
- `Database1/urls.py` - URL routing
- `accounts/permissions.py` - RBAC configuration
- `requirements.txt` - Python dependencies

### Running Tests
```bash
python manage.py test
```

### Creating Superuser
```bash
python manage.py createsuperuser
```

---

## Support & Documentation

### Django Admin
- URL: http://127.0.0.1:8001/admin/
- Full database access for superusers
- Model management interface

### Language Support
- English (default)
- Arabic (RTL support enabled)
- Switch language: `/set-language/`

### Date/Time Configuration
- Timezone: `Asia/Riyadh`
- Date format: DD/MM/YYYY
- Currency: SAR (Saudi Riyal)

---

## Version Information

**Django Version:** 5.2.8  
**Python Version:** 3.13+  
**Database:** PostgreSQL  
**Mode:** Accountant Only  
**Last Updated:** February 11, 2026

---

## Quick Reference Commands

```bash
# Start server
python manage.py runserver 8001

# Create accountant user
python create_accountant_only.py

# Check system
python manage.py check

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Create superuser
python manage.py createsuperuser

# Shell access
python manage.py shell

# Collect static files
python manage.py collectstatic
```

---

## License & Credits

**Developer:** Inam Khan  
**Created:** June 1, 2024  
**Modified:** February 11, 2026  
**Purpose:** School Financial Management System (Accountant Mode)

---

## Contact & Support

For technical support or feature requests, please contact the system administrator.

**Login URL:** http://127.0.0.1:8001/accounts/login/  
**Username:** accountant  
**Password:** accountant123

---

**END OF DOCUMENTATION**
