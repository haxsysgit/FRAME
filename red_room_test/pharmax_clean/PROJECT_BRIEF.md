# PHARMAX — Project Brief

## What Is This?

**PHARMAX** is a web-based pharmacy management system built as a Final Year Project (CST3990). It replaces manual paper-based pharmacy operations with a fast, digital platform.

---

## The Problem

Nigerian community pharmacies still rely on:
- Handwritten invoices (slow, error-prone)
- Manual stock counting (theft goes unnoticed)
- Paper ledgers for debtors (records get lost)
- No real-time visibility into daily sales

**Result:** Lost revenue, inventory shrinkage, poor customer experience.

---

## The Solution

A role-based web application where:

| Role | What They Do |
|------|--------------|
| **Staff** | Create invoices, search products, recommend alternatives |
| **Cashier** | Confirm payments, print receipts, track payment methods |
| **Admin** | View reports, manage inventory, track debtors, full control |

---

## Core Features (Must Have)

### 1. Invoice System
- Create draft invoices → Add products → Finalize payment → Dispense goods
- Search products by name with keyboard shortcuts
- Automatic stock deduction on dispense
- Payment methods: Cash, POS, Bank Transfer

### 2. Inventory Management
- Product catalog with categories, brands, units
- Stock levels with low-stock alerts
- Stock adjustment with audit trail
- Reorder level tracking

### 3. Dashboard & Analytics
- Today's sales, revenue, pending invoices
- Low stock alerts
- Payment method breakdown
- Charts and visualizations

### 4. User Management
- Role-based access (Admin, Cashier, Staff)
- Secure login with JWT authentication
- Activity logging

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Vue 3, Vite, Pinia |
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| Auth | JWT tokens |
| Analytics | Streamlit (embedded dashboards) |

---

## Key Principles

1. **Speed** — Staff must complete an invoice in under 30 seconds
2. **Simplicity** — Minimal clicks, keyboard-first design
3. **Reliability** — Never lose a transaction
4. **Auditability** — Every action is logged

---

## What Success Looks Like

- [ ] Staff can create and finalize an invoice in < 30 seconds
- [ ] Admin can see today's revenue at a glance
- [ ] Low stock items are flagged automatically
- [ ] All payments are tracked by method
- [ ] System handles 100+ invoices/day without slowdown

---

## Project Scope Boundaries

**In Scope:**
- Invoice lifecycle (create → pay → dispense)
- Basic inventory management
- Role-based access
- Simple reporting dashboard

**Out of Scope (for now):**
- Multi-branch support
- Customer accounts / loyalty
- Prescription management
- Mobile app
