# CENRO Admin System - Quick Reference Guide

## 🚀 Quick Start

### Installation (One-Time)
```bash
# Navigate to project
cd c:\Users\JanJan\.cursor\wetland

# Create migrations for new models
python manage.py makemigrations dashboard

# Apply migrations
python manage.py migrate

# Initialize system with sample data
python setup_admin_system.py

# Start server
python manage.py runserver
```

## 🔑 Default Test Accounts

| Account   | Username  | Password      | Role    |
|-----------|-----------|---------------|---------|
| Admin     | admin     | admin123      | ADMIN   |
| Staff 1   | staff1    | staff1123     | STAFF   |
| Consumer  | consumer1 | consumer1123  | CONSUMER|

## 🌐 Key URLs

| Feature          | URL                              | Requires Role |
|------------------|----------------------------------|---------------|
| Home             | /                                | None          |
| Login            | /accounts/login/                 | None          |
| Admin Dashboard  | /dashboard/admin/                | ADMIN         |
| Requests         | /dashboard/admin/requests/       | ADMIN         |
| Membership       | /dashboard/admin/membership/     | ADMIN         |
| Computation      | /dashboard/admin/computation/    | ADMIN         |
| Declogging App   | /dashboard/admin/declogging-app/ | ADMIN         |
| Django Admin     | /admin/                          | SUPERUSER     |

## 📊 Main Features

### 1. Dashboard Overview
- Monthly trends graph
- Weekly statistics
- Barangay rankings
- Service distribution
- Efficiency metrics

### 2. Service Requests
- **Pending Tab:** New requests awaiting action
- **Approved Tab:** Requests with computed fees
- **Schedule Tab:** Organized by barangay (10-person limit)
- **Completed Tab:** Historical services

### 3. Membership Management
- **Registration Tab:** Pending member registrations
- **Account Management Tab:** Active member accounts
- **Service History Tab:** Complete service records with balances

### 4. Service Computation
```
Select Category (Residential/Commercial)
↓
Enter Cubic Meters
↓
[Optional] Enter Distance if Outside Bayawan
↓
System Calculates:
  - Base charge (category × m³)
  - Tipping fee (₱500/m³)
  - Inspection fee (₱150)
  - [If outside] Distance × 2 × ₱20
  - [If outside] Wear & Tear (20%)
  - [If outside] Meals/Transport allowance
↓
View Breakdown & Print Receipt
```

### 5. Declogging Application
1. Enter applicant name and date
2. Upload applicant signature
3. Select CENRO representative
4. Upload CENRO signature and approval date
5. Print official letter with both signatures

## 💰 Charge Formula Reference

### Basic Charges (All Services)
```
Tipping Fee = ₱500 per cubic meter
Inspection Fee = ₱150 (flat)
```

### Outside Bayawan Addition
```
Distance Cost = Distance (km) × 2 × ₱20
Wear & Tear = Base Charge × 20%
Meals/Transport = Variable (configurable)
```

### Example Calculation
```
Service: Residential, Inside Bayawan, 2 m³
- Tipping Fee: 2 m³ × ₱500 = ₱1,000
- Inspection Fee = ₱150
- TOTAL = ₱1,150

Service: Residential, Outside Bayawan, 2 m³, 15 km
- Base: 2 × ₱100 = ₱200
- Tipping: 2 × ₱500 = ₱1,000
- Inspection: ₱150
- Distance: 15 × 2 × ₱20 = ₱600
- Wear & Tear: ₱200 × 20% = ₱40
- Meals/Transport: ₱500 (example)
- TOTAL = ₱2,490
```

## 📋 Member Service History

Tracks for each member:
- Service date
- Service type (Declogging/Grass Cutting)
- Cubic meters used
- Payment status (Paid/Free)
- Remaining balance

**4-Year Cycle Limit:**
- Members can use up to 5 m³ in any 4-year period
- System tracks and calculates remaining balance
- Prevents violations of declogging frequency rules

## 🖨️ Printing Features

### What's Printable
- ✓ Service computation receipts (with full breakdown)
- ✓ Member service history reports
- ✓ Declogging application letters
- ✓ Dashboard statistics
- ✓ Admin summaries

### How to Print
1. Navigate to any page
2. Use browser Print button (Ctrl+P or ⌘+P)
3. Select "Print to PDF" or printer
4. Save or print

## 🔐 Important Security Notes

### Admin Access
- Only users with role = "ADMIN" can access admin panel
- All admin views require login
- Actions are logged with timestamps

### User Approval
- New registrations require approval
- Staff accounts must be approved before use
- Consumers are auto-approved but can be disabled

### File Uploads
- Signatures stored in `/media/signatures/`
- Receipts in `/media/bawad_receipts/`
- All uploads validated for security

## ⚙️ Common Tasks

### Creating a New Staff Member
1. Login as Admin
2. Go to Accounts → Register Staff
3. Fill form with staff details
4. Staff account created (pending approval)
5. Go to Staff Approvals → Approve

### Processing a Service Request
1. Go to Requests → Pending tab
2. Click request to view details
3. Go to Computation → Calculate charges
4. Review breakdown
5. Approve request
6. Assign to staff and schedule

### Tracking Member Balance
1. Go to Membership → Service History
2. Select member from dropdown
3. View complete service record
4. See remaining balance (4-year cycle)
5. Print report if needed

### Generating Receipt
1. Go to Computation
2. Enter service details
3. Click "Calculate Charges"
4. View breakdown on right
5. Click "Print Receipt"
6. Select print destination

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't login | Verify username/password, check if account is approved |
| Admin panel shows 404 | Ensure user role is set to "ADMIN" |
| Computation not working | Check if ChargeCategory objects exist in database |
| Can't upload files | Verify media directory permissions |
| Charges look wrong | Review calculation formula and inputs |
| Templates not loading | Run `python manage.py collectstatic` |

## 📞 Quick Commands

```bash
# Start server
python manage.py runserver

# Create superuser
python manage.py createsuperuser

# Run shell
python manage.py shell

# Migrations
python manage.py makemigrations
python manage.py migrate

# Reset database (careful!)
python manage.py flush

# Initialize admin system
python setup_admin_system.py
```

## 📚 Documentation Files

- **IMPLEMENTATION_SUMMARY.md** - What was built and why
- **ADMIN_SYSTEM_GUIDE.md** - Detailed feature documentation
- **DEPLOYMENT_CHECKLIST.md** - Production setup steps
- **README.md** - Project overview
- **QUICKSTART.md** - Getting started guide

## ✨ Tips & Tricks

- Use Tab key to navigate between form fields quickly
- All dates can be typed as YYYY-MM-DD or selected via calendar
- Computation results are immediately visible for review
- All reports are printer-friendly
- Logout button appears in top-right corner
- Filter/search works across all list views
- Remember to approve new staff before they can work

## 🎓 Learning Path

1. Start → Login as Admin
2. Explore → Dashboard Overview
3. Create → Sample Service Request
4. Compute → Calculate Charges
5. Report → Generate Receipt
6. Manage → View Member History
7. Apply → Create Declogging App

---

**Last Updated:** January 29, 2026  
**Status:** ✅ Production Ready  
**Questions?** Refer to detailed guides or Django documentation
