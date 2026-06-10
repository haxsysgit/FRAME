# PharmaX Adoption Guide

This guide covers how to deploy, install, and onboard a pharmacy onto PharmaX. The system is designed for a single-pharmacy environment with minimal IT overhead.

---

## 1) Hardware Recommendations

### Primary Workstation (Admin/Billing Counter)
**Recommended: Laptop or Desktop PC**

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Screen | 14" | 15.6"+ (larger helps reduce scrolling) |
| RAM | 4GB | 8GB |
| Storage | 128GB SSD | 256GB SSD |
| OS | Windows 10/11, Ubuntu 22.04+ | Any modern browser-based OS works |

**Why laptop/desktop over tablet for the main station:**
- Easier keyboard entry for product lookup, invoicing, and stock management
- Larger screen shows more products at once (faster checkout)
- More reliable for all-day operation
- Better for printing (USB receipt printers work best on desktops)

### Secondary Stations (Stock Entry / Price Checking)
**Recommended: Android Tablet (10"+) or Chromebook**

- Tablets work well for staff doing stock counts or price checks
- Touch-friendly PharmaX interface supports quick PIN login
- Wi-Fi connectivity sufficient; no need for cellular

### Receipt Printer
- Any 58mm or 80mm thermal receipt printer with USB connection
- Alternative: Network receipt printer if multiple stations print

### Barcode Scanner (Optional but Recommended)
- USB wired scanner (~₦10,000-15,000)
- Plugs into laptop USB, acts as keyboard input
- Speeds up product lookup during checkout

---

## 2) Network Requirements

PharmaX is a web application. All devices connect to the same backend server.

**Option A: Local Server (Best for Unreliable Internet)**
- Run backend on one dedicated laptop/PC on local network
- Other devices connect via local IP (e.g., `192.168.1.100:8000`)
- Works offline; data stays in-house

**Option B: Cloud Deployment (Simpler but Needs Internet)**
- Deploy backend to Render, Railway, or similar
- All devices access via public URL
- Requires stable internet for all operations

**Recommendation:** Start with Option A if internet is unreliable in the area. Migrate to cloud later if needed.

---

## 3) Initial Data Entry Strategy

The biggest challenge when adopting any inventory system is entering existing product data without disrupting daily sales.

### Phased Entry Approach (Recommended)

**Week 1: Core Products Only**
1. Enter your top 100-200 most-sold products
2. Include: Name, SKU (or barcode), unit prices, current quantity
3. Staff can start selling these items immediately in PharmaX
4. For unlisted products, continue with manual receipt (paper backup)

**Week 2-3: Expand Product List**
1. Add remaining products during slow hours (early morning or late evening)
2. Use staff downtime for batch entry
3. Run parallel systems: PharmaX for entered products, paper for others

**Week 4+: Full Cutover**
1. All products in system
2. Paper receipts phased out
3. PharmaX becomes primary

### Bulk Import Option
If you have product data in Excel/CSV:
1. Prepare file with columns: `sku`, `name`, `brand_name`, `quantity_on_hand`, `reorder_level`
2. Admin can import via Products > Import Products
3. Review and assign units/pricing after import

### Stock Count During Entry
- When adding a product, physically count what's on shelf
- Enter this as starting `quantity_on_hand`
- PharmaX will track changes from that point forward

---

## 4) Staff Training Plan

PharmaX is designed for users with limited computer experience. Training should be hands-on and repeated.

### Training Session 1: Basic Navigation (30 minutes)
- How to log in with PIN
- Where main sections are (Products, Sales, Stock)
- How to log out

### Training Session 2: Making a Sale (45 minutes)
- Finding a product (search by name or barcode scan)
- Adding items to cart
- Completing checkout
- Printing receipt

### Training Session 3: Stock Tasks (30 minutes)
- How to view low-stock alerts
- How to request stock adjustment
- Understanding "Out of Stock" vs "Low Stock"

### Training Session 4: Admin Only (60 minutes)
- User management (adding/approving staff)
- Product management (add, edit, pricing)
- Reports overview
- Daily reconciliation

### Ongoing Support
- Post "Quick Reference Cards" near each workstation
- First 2 weeks: be physically present during peak hours
- Create WhatsApp group for staff questions

---

## 5) Cutover Day Checklist

Before going live:

- [ ] All frequently-sold products entered
- [ ] All staff accounts created with PINs set
- [ ] Receipt printer tested
- [ ] Barcode scanner tested (if using)
- [ ] Opening stock counts verified
- [ ] Backup manual receipt books available (fallback)
- [ ] Wi-Fi/network connectivity confirmed at all stations
- [ ] Admin password stored securely
- [ ] Training completed for all staff

---

## 6) Daily Operations Routine

### Opening
1. Admin logs in, reviews any overnight alerts
2. Cashier logs in via PIN
3. Quick check: receipt printer has paper

### During Business Hours
1. Sales processed through PharmaX
2. Stock alerts checked periodically
3. End of shift: Cashier logs out

### Closing
1. Admin triggers daily reconciliation (if not auto at 10 PM)
2. Review daily sales summary
3. Note any discrepancies for next-day follow-up
4. Lock system (auto or manual)

---

## 7) Troubleshooting Quick Reference

| Problem | Quick Fix |
|---------|-----------|
| Can't log in | Check PIN (4 digits) or password; ask Admin to reset |
| Product not found | Try different spelling; check if product was added |
| Receipt not printing | Check printer power, paper, USB cable |
| Page won't load | Refresh browser; check Wi-Fi connection |
| System locked (after 10 PM) | Admin can manually unlock for urgent tasks |

---

## 8) Backup and Data Safety

- **Daily:** PharmaX auto-tracks all changes (audit logs)
- **Weekly:** Export sales report to USB/cloud storage
- **Monthly:** Full database backup (Admin task)

If using local server: Keep backup on separate USB drive stored off-site.

---

## 9) Support Contacts

- **System Owner/Developer:** [Your contact info]
- **Hardware Issues:** Local computer repair shop
- **Internet Issues:** ISP customer service

---

*This guide should be printed and kept near the main workstation for reference during the first month of operation.*
