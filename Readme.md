# Scheme & Commission Management System

## Overview

This module implements a **hierarchical, role-based commission management system** designed for fintech / multi-level platforms. It supports **scheme inheritance**, **service-wise commission configuration**, and **accurate commission settlement** during transactions.

The system ensures:

- No commission leakage
- No double payouts
- Strict hierarchy validation
- Full auditability via ledgers

---

## Problem Statement

In a multi-role fintech platform:

- Different users (Admin, White Label, Master Distributor, Distributor, Retailer, Customer) earn commissions
- Commissions vary per **service**
- Schemes are hierarchical (child schemes inherit from parent schemes)
- Some roles may **not be allowed** to configure commissions

The challenge is to:

- Resolve commissions correctly across scheme hierarchy
- Allow partial configuration using `NULL`
- Ensure Admin/root commissions are always respected
- Distribute only **margin commissions**, not absolute

---

## Core Concepts

### 1. Scheme Hierarchy

- Schemes can have parent schemes
- Root scheme (SuperAdmin) acts as the **final fallback**
- Child schemes inherit commissions from parents when values are `NULL`

```
SuperAdmin Scheme (root)
   └── White Label Scheme
         └── Master Distributor Scheme
               └── Distributor Scheme
```

---

### 2. Role-Based Commission Model

Supported roles:

- ADMIN
- WHITE_LABEL
- MASTER_DISTRIBUTOR
- DISTRIBUTOR
- RETAILER
- CUSTOMER

Each role has a **maximum absolute commission percentage** per service.

---

### 3. Commission Types

- **Percentage-based** (most common)
- Absolute values are converted to **margin earnings** during settlement

---

## Commission Resolution Logic

### Absolute Commission Resolution

- Start from the user's scheme
- For each role:

  - If value is `NULL`, move to parent scheme
  - First non-null value wins

- If no value is found, root scheme is used

This guarantees Admin commissions are never skipped.

---

### Margin Commission Calculation

Absolute commissions are converted into **earnings**:

```
Role Margin = Current Role % - Next Lower Role %
```

This prevents double payouts and ensures correct revenue sharing.

---

## Transaction Flow

1. User initiates transaction
2. Resolve absolute commission from scheme hierarchy
3. Convert absolute → margin commissions
4. Traverse user hierarchy (parent users)
5. Create CommissionLedger entries
6. Persist transaction + ledger atomically

---

## APIs Implemented

### Commission Management

- Create / Update commission per scheme & service
- Validate against parent scheme limits
- Partial updates supported using `NULL`

### Commission Chain View

- View full inheritance chain
- Shows scheme-by-scheme commission configuration
- Includes root scheme

### Transaction APIs

- Create transaction
- Auto-settle commissions
- View personal transaction & commission summary

### Deletion APIs (just for the clean up)

- Delete transaction → auto deletes ledgers
- Delete commission → deletes related transactions & ledgers

---

## Safety & Validation

- Only scheme creators or admins can configure commissions
- Child commissions cannot exceed parent limits
- Admin & SuperAdmin cannot initiate transactions
- Strict role hierarchy enforcement

---
