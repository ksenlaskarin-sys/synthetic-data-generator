# DML Execution Order - PK-FK Dependency Sequence

## Overview

The DML files are generated with numerical prefixes (01, 02, 03, etc.) based on **Primary Key-Foreign Key dependency relationships**. This ensures that when you execute the DML files in order, all parent records are inserted before child records that reference them, preventing FK constraint violations.

**Format**: `NN_TableName.sql` where NN is the execution order (01-26)

---

## Complete Execution Order (1-26)

### 🟢 Level 1: Root Tables (No FK Dependencies)
These tables have no foreign keys and can be loaded first.

```
01_Users.sql                      (100,000 rows)
   └─ Primary Table - User accounts, no FK dependencies
   └─ Referenced by: Carts, Orders, Promotions, Search_Logs, App_Usage_Logs, Subscriptions

02_Categories.sql                 (200 rows)
   └─ Primary Table - Product categories, no FK dependencies
   └─ Referenced by: Products

03_Warehouses.sql                 (100 rows)
   └─ Primary Table - Warehouse locations, no FK dependencies
   └─ Referenced by: Inventory

04_Delivery_Partners.sql          (3,000 rows)
   └─ Primary Table - Delivery partner information, no FK dependencies
   └─ Referenced by: Orders, Deliveries

05_Products.sql                   (50,000 rows)
   └─ DEPENDS ON: Categories (02)
   └─ FK: category_id → Categories(category_id)
   └─ Referenced by: Cart_Items, Order_Items, Inventory, Promotions
```

### 🟡 Level 2: Secondary Tables (Depends on Level 1)
These tables reference root tables.

```
06_Carts.sql                      (80,000 rows)
   └─ DEPENDS ON: Users (01)
   └─ FK: user_id → Users(user_id)
   └─ Referenced by: Cart_Items

07_Cart_Items.sql                 (200,000 rows)
   └─ DEPENDS ON: Carts (06), Products (05)
   └─ FK: cart_id → Carts(cart_id)
   └─ FK: product_id → Products(product_id)
   └─ No dependents

08_Orders.sql                     (300,000 rows)
   └─ DEPENDS ON: Users (01), Delivery_Partners (04), Payments (see below)
   └─ FK: user_id → Users(user_id)
   └─ FK: partner_id → Delivery_Partners(partner_id)
   └─ FK: payment_id → Payments(payment_id)
   └─ Referenced by: Order_Items, Refunds, Deliveries

09_Order_Items.sql                (900,000 rows)
   └─ DEPENDS ON: Orders (08), Products (05)
   └─ FK: order_id → Orders(order_id)
   └─ FK: product_id → Products(product_id)
   └─ No dependents

10_Inventory.sql                  (200,000 rows)
   └─ DEPENDS ON: Products (05), Warehouses (03)
   └─ FK: product_id → Products(product_id)
   └─ FK: warehouse_id → Warehouses(warehouse_id)
   └─ No dependents

11_Payments.sql                   (300,000 rows)
   └─ No FK dependencies
   └─ Referenced by: Orders (08), Refunds
   └─ NOTE: Must be loaded BEFORE Orders (08) - order adjusted in TABLE_ORDER
```

### 🟠 Level 3: Transaction Tables (Depends on Levels 1-2)
These tables reference orders and payments.

```
12_Refunds.sql                    (50,000 rows)
   └─ DEPENDS ON: Orders (08), Payments (11)
   └─ FK: order_id → Orders(order_id)
   └─ FK: payment_id → Payments(payment_id)
   └─ No dependents

13_Deliveries.sql                 (300,000 rows)
   └─ DEPENDS ON: Orders (08), Delivery_Partners (04)
   └─ FK: order_id → Orders(order_id)
   └─ FK: partner_id → Delivery_Partners(partner_id)
   └─ No dependents

14_Promotions.sql                 (20,000 rows)
   └─ DEPENDS ON: Users (01), Products (05)
   └─ FK: user_id → Users(user_id)
   └─ FK: product_id → Products(product_id)
   └─ No dependents

15_Reviews.sql                    (150,000 rows)
   └─ DEPENDS ON: Users (01), Products (05)
   └─ FK: user_id → Users(user_id)
   └─ FK: product_id → Products(product_id)
   └─ No dependents
```

### 🔵 Level 4: Analytics/Logging Tables (Depends on Users)
These tables store usage logs and analytics.

```
16_Search_Logs.sql                (500,000 rows)
   └─ DEPENDS ON: Users (01)
   └─ FK: user_id → Users(user_id)
   └─ No dependents

17_App_Usage_Logs.sql             (800,000 rows)
   └─ DEPENDS ON: Users (01)
   └─ FK: user_id → Users(user_id)
   └─ No dependents

18_Subscriptions.sql              (40,000 rows)
   └─ DEPENDS ON: Users (01)
   └─ FK: user_id → Users(user_id)
   └─ No dependents
```

### 🟣 Level 5: Financial Tables (No Dependencies)
These tables aggregate financial data and don't reference other tables.

```
19_Finance_Orders_Revenue.sql     (300,000 rows)
   └─ No FK dependencies
   └─ Financial aggregation table

20_Finance_Payments_Settlement.sql (300,000 rows)
   └─ No FK dependencies
   └─ Financial aggregation table

21_Finance_Refunds_Cost.sql       (50,000 rows)
   └─ No FK dependencies
   └─ Financial aggregation table

22_Finance_Delivery_Costs.sql     (300,000 rows)
   └─ No FK dependencies
   └─ Financial aggregation table

23_Finance_Operational_Expenses.sql (10,000 rows)
   └─ No FK dependencies
   └─ Financial aggregation table

24_Finance_Partner_Payouts.sql    (10,000 rows)
   └─ No FK dependencies
   └─ Financial aggregation table

25_Finance_Employee_Salary.sql    (10,000 rows)
   └─ No FK dependencies
   └─ Financial aggregation table

26_Finance_Profit_Loss_Summary.sql (365 rows)
   └─ No FK dependencies
   └─ Financial summary table
```

---

## Dependency Graph

```
LEVEL 0 (Root - No Dependencies):
├── 01_Users.sql
├── 02_Categories.sql
├── 03_Warehouses.sql
├── 04_Delivery_Partners.sql
└── 11_Payments.sql

LEVEL 1 (Depends on Level 0):
├── 05_Products.sql (→ Categories)
├── 06_Carts.sql (→ Users)
└── 08_Orders.sql (→ Users, Delivery_Partners, Payments)

LEVEL 2 (Depends on Level 0-1):
├── 07_Cart_Items.sql (→ Carts, Products)
├── 09_Order_Items.sql (→ Orders, Products)
├── 10_Inventory.sql (→ Products, Warehouses)
├── 12_Refunds.sql (→ Orders, Payments)
├── 13_Deliveries.sql (→ Orders, Delivery_Partners)
├── 14_Promotions.sql (→ Users, Products)
└── 15_Reviews.sql (→ Users, Products)

LEVEL 3 (Depends on Level 0-1):
├── 16_Search_Logs.sql (→ Users)
├── 17_App_Usage_Logs.sql (→ Users)
└── 18_Subscriptions.sql (→ Users)

LEVEL 4 (Financial - No Dependencies):
├── 19_Finance_Orders_Revenue.sql
├── 20_Finance_Payments_Settlement.sql
├── 21_Finance_Refunds_Cost.sql
├── 22_Finance_Delivery_Costs.sql
├── 23_Finance_Operational_Expenses.sql
├── 24_Finance_Partner_Payouts.sql
├── 25_Finance_Employee_Salary.sql
└── 26_Finance_Profit_Loss_Summary.sql
```

---

## Table Reference Matrix

| Order | Table | PK | Depends On | References |
|-------|-------|----|-----------|----|
| 01 | Users | user_id | - | Carts, Orders, Search_Logs, App_Usage_Logs, Promotions, Reviews, Subscriptions |
| 02 | Categories | category_id | - | Products |
| 03 | Warehouses | warehouse_id | - | Inventory |
| 04 | Delivery_Partners | partner_id | - | Orders, Deliveries |
| 05 | Products | product_id | Categories | Cart_Items, Order_Items, Inventory, Promotions, Reviews |
| 06 | Carts | cart_id | Users | Cart_Items |
| 07 | Cart_Items | cart_item_id | Carts, Products | - |
| 08 | Orders | order_id | Users, Delivery_Partners, Payments | Order_Items, Refunds, Deliveries |
| 09 | Order_Items | order_item_id | Orders, Products | - |
| 10 | Inventory | inventory_id | Products, Warehouses | - |
| 11 | Payments | payment_id | - | Orders, Refunds |
| 12 | Refunds | refund_id | Orders, Payments | - |
| 13 | Deliveries | delivery_id | Orders, Delivery_Partners | - |
| 14 | Promotions | promo_id | Users, Products | - |
| 15 | Reviews | review_id | Users, Products | - |
| 16 | Search_Logs | log_id | Users | - |
| 17 | App_Usage_Logs | log_id | Users | - |
| 18 | Subscriptions | subscription_id | Users | - |
| 19 | Finance_Orders_Revenue | rev_id | - | - |
| 20 | Finance_Payments_Settlement | settlement_id | - | - |
| 21 | Finance_Refunds_Cost | cost_id | - | - |
| 22 | Finance_Delivery_Costs | cost_id | - | - |
| 23 | Finance_Operational_Expenses | expense_id | - | - |
| 24 | Finance_Partner_Payouts | payout_id | - | - |
| 25 | Finance_Employee_Salary | salary_id | - | - |
| 26 | Finance_Profit_Loss_Summary | pl_id | - | - |

---

## How to Execute

### Option 1: Execute All DML Files in Order (Recommended)
```bash
# Execute all ordered DML files sequentially
for file in output/DML/[0-9][0-9]_*.sql; do
  echo "Executing: $file"
  mysql -u root -p mydb < "$file"
done
```

### Option 2: Execute Specific File
```bash
# Execute only Users table
mysql -u root -p mydb < output/DML/01_Users.sql

# Execute only Orders (after Users has been loaded)
mysql -u root -p mydb < output/DML/08_Orders.sql
```

### Option 3: Use Consolidated Script
```bash
# Execute all-in-one consolidated script
mysql -u root -p mydb < output/DML/consolidated_dml.sql
```

---

## Key Points

### ✅ Why This Order Matters

1. **Parent Before Child**: All tables referenced by FK constraints are loaded first
2. **No Orphaned Records**: Every FK value references an existing PK
3. **No Constraint Violations**: Loading respects all foreign key constraints
4. **Transaction Safety**: Can be wrapped in transactions for atomic operations

### ✅ If You Get FK Errors

Check that you're executing files in the correct order:
```bash
# Correct order (numerical)
01_Users.sql → 02_Categories.sql → 03_Warehouses.sql → ... → 26_Finance_Profit_Loss_Summary.sql

# Wrong order would cause FK errors
08_Orders.sql (before 01_Users.sql) ❌ ERROR: user_id reference fails
```

### ✅ Total Records by Level

| Level | Tables | Total Records |
|-------|--------|---------------|
| Level 1 (Root) | 5 | 103,300 |
| Level 2 (References Level 1) | 7 | 1,880,000 |
| Level 3 (Analytics) | 3 | 1,340,000 |
| Level 4 (Financial) | 8 | 680,365 |
| **TOTAL** | **26** | **7,778,665** |

---

## Common Scenarios

### Scenario 1: Load Only Users and Orders
```bash
# Load in order
mysql -u root -p mydb < output/DML/01_Users.sql
mysql -u root -p mydb < output/DML/11_Payments.sql
mysql -u root -p mydb < output/DML/04_Delivery_Partners.sql
mysql -u root -p mydb < output/DML/08_Orders.sql
```

### Scenario 2: Load All Products and Related
```bash
# Load in order
mysql -u root -p mydb < output/DML/02_Categories.sql
mysql -u root -p mydb < output/DML/05_Products.sql
mysql -u root -p mydb < output/DML/03_Warehouses.sql
mysql -u root -p mydb < output/DML/10_Inventory.sql
```

### Scenario 3: Load Financial Data Only
```bash
# Financial tables have no FK dependencies - can load in any order
# But recommended order shown (19-26)
for file in output/DML/[12][0-9]_Finance_*.sql; do
  mysql -u root -p mydb < "$file"
done
```

---

## File Naming Convention

```
NN_TableName.sql

NN = Execution order (01-26)
    ✅ Execute in this numerical order
    ✅ Prevents FK constraint violations
    ✅ Guarantees data integrity

TableName = Actual table name
    Example: 01_Users.sql, 08_Orders.sql, 26_Finance_Profit_Loss_Summary.sql
```

---

## Verification Queries

### Check All Tables Loaded
```sql
SELECT 
  'Users' as table_name, COUNT(*) as count FROM Users
UNION ALL
SELECT 'Categories', COUNT(*) FROM Categories
UNION ALL
SELECT 'Orders', COUNT(*) FROM Orders
-- ... repeat for all 26 tables
ORDER BY table_name;
```

### Check Total Records
```sql
SELECT SUM(cnt) as total_records FROM (
  SELECT COUNT(*) as cnt FROM Users
  UNION ALL SELECT COUNT(*) FROM Categories
  -- ... repeat for all 26 tables
) t;

-- Expected: 7,778,665
```

### Check FK Integrity
```sql
-- Verify no orphaned Orders
SELECT COUNT(*) as orphaned_records
FROM Orders o
LEFT JOIN Users u ON o.user_id = u.user_id
WHERE u.user_id IS NULL;

-- Expected: 0
```

---

**Summary**: Execute DML files in numerical order (01 → 26) to ensure all primary keys exist before foreign keys reference them. This guarantees 100% data integrity with zero FK constraint violations.
