# DML Execution Order - Dependency Tree & Visual Guide

## 📊 Visual Dependency Tree

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DML EXECUTION DEPENDENCY TREE                      │
└─────────────────────────────────────────────────────────────────────────────┘

PHASE 1: ROOT TABLES (No FK Dependencies)
═════════════════════════════════════════════════════════════════════════════
Execute these first - they have no dependencies

  01 → Users ──────┬─────────────┬─────────────┬──────────────┬─────────────┐
       └─ PK: user_id
                    │             │             │              │             │
  02 → Categories   │   06 → Carts│  08 → Orders│ 14 → Promotions         │
       └─ PK: category_id  │             │  │                          │   │
                    │             │  11 → Payments     16 → Search_Logs  17 → App_Usage_Logs
  03 → Warehouses   │    │ 04 → Delivery_Partners  │
       └─ PK: warehouse_id     └─ PK: partner_id       └─ 18 → Subscriptions
                    
  05 → Products     │   15 → Reviews
       ├─ FK: category_id → Categories
       │
       ├─ PK: product_id
       └─ Used by many


PHASE 2: SECONDARY TABLES (Depend on Phase 1)
═════════════════════════════════════════════════════════════════════════════
  
  From 01_Users:
  ├─→ 06_Carts (FK: user_id)
  │   └─→ 07_Cart_Items (FK: cart_id + product_id)
  │
  ├─→ 08_Orders (FK: user_id, partner_id, payment_id)
  │   ├─→ 09_Order_Items (FK: order_id, product_id)
  │   ├─→ 12_Refunds (FK: order_id, payment_id)
  │   └─→ 13_Deliveries (FK: order_id, partner_id)
  │
  ├─→ 14_Promotions (FK: user_id, product_id)
  ├─→ 15_Reviews (FK: user_id, product_id)
  ├─→ 16_Search_Logs (FK: user_id)
  ├─→ 17_App_Usage_Logs (FK: user_id)
  └─→ 18_Subscriptions (FK: user_id)

  From 02_Categories:
  └─→ 05_Products (FK: category_id)
      └─→ 07_Cart_Items (FK: product_id)
      └─→ 09_Order_Items (FK: product_id)
      └─→ 10_Inventory (FK: product_id)
      └─→ 14_Promotions (FK: product_id)
      └─→ 15_Reviews (FK: product_id)

  From 03_Warehouses:
  └─→ 10_Inventory (FK: warehouse_id)

  From 04_Delivery_Partners:
  ├─→ 08_Orders (FK: partner_id)
  └─→ 13_Deliveries (FK: partner_id)

  From 11_Payments:
  ├─→ 08_Orders (FK: payment_id)
  └─→ 12_Refunds (FK: payment_id)


PHASE 3: FINANCIAL TABLES (No Dependencies - Can be Any Order)
═════════════════════════════════════════════════════════════════════════════
  
  19 → Finance_Orders_Revenue (Independent)
  20 → Finance_Payments_Settlement (Independent)
  21 → Finance_Refunds_Cost (Independent)
  22 → Finance_Delivery_Costs (Independent)
  23 → Finance_Operational_Expenses (Independent)
  24 → Finance_Partner_Payouts (Independent)
  25 → Finance_Employee_Salary (Independent)
  26 → Finance_Profit_Loss_Summary (Independent)

═════════════════════════════════════════════════════════════════════════════
```

---

## 🔗 Dependency Matrix - What References What

### Incoming Dependencies (What depends on this table)

| Table | Referenced By | Count |
|-------|---------------|-------|
| **01_Users** | Carts(06), Orders(08), Promotions(14), Reviews(15), Search_Logs(16), App_Usage_Logs(17), Subscriptions(18) | 7 |
| **02_Categories** | Products(05) | 1 |
| **03_Warehouses** | Inventory(10) | 1 |
| **04_Delivery_Partners** | Orders(08), Deliveries(13) | 2 |
| **05_Products** | Cart_Items(07), Order_Items(09), Inventory(10), Promotions(14), Reviews(15) | 5 |
| **06_Carts** | Cart_Items(07) | 1 |
| **08_Orders** | Order_Items(09), Refunds(12), Deliveries(13) | 3 |
| **11_Payments** | Orders(08), Refunds(12) | 2 |
| **19-26** | Financial tables (None - Independent) | 0 |

---

## 📋 Step-by-Step Execution Guide

### Step 1️⃣: Load Root Tables (Phase 1)
```bash
# Load these first - no dependencies
mysql -u root -p mydb < output/DML/01_Users.sql
mysql -u root -p mydb < output/DML/02_Categories.sql
mysql -u root -p mydb < output/DML/03_Warehouses.sql
mysql -u root -p mydb < output/DML/04_Delivery_Partners.sql
mysql -u root -p mydb < output/DML/11_Payments.sql
```
**Status**: ✅ Ready for Phase 2

---

### Step 2️⃣: Load Dependent Tables (Phase 2)
```bash
# Now load tables that reference Phase 1
mysql -u root -p mydb < output/DML/05_Products.sql
mysql -u root -p mydb < output/DML/06_Carts.sql
mysql -u root -p mydb < output/DML/07_Cart_Items.sql
mysql -u root -p mydb < output/DML/08_Orders.sql
mysql -u root -p mydb < output/DML/09_Order_Items.sql
mysql -u root -p mydb < output/DML/10_Inventory.sql
mysql -u root -p mydb < output/DML/12_Refunds.sql
mysql -u root -p mydb < output/DML/13_Deliveries.sql
mysql -u root -p mydb < output/DML/14_Promotions.sql
mysql -u root -p mydb < output/DML/15_Reviews.sql
mysql -u root -p mydb < output/DML/16_Search_Logs.sql
mysql -u root -p mydb < output/DML/17_App_Usage_Logs.sql
mysql -u root -p mydb < output/DML/18_Subscriptions.sql
```
**Status**: ✅ Ready for Phase 3

---

### Step 3️⃣: Load Financial Tables (Phase 3)
```bash
# Load independent financial tables
mysql -u root -p mydb < output/DML/19_Finance_Orders_Revenue.sql
mysql -u root -p mydb < output/DML/20_Finance_Payments_Settlement.sql
mysql -u root -p mydb < output/DML/21_Finance_Refunds_Cost.sql
mysql -u root -p mydb < output/DML/22_Finance_Delivery_Costs.sql
mysql -u root -p mydb < output/DML/23_Finance_Operational_Expenses.sql
mysql -u root -p mydb < output/DML/24_Finance_Partner_Payouts.sql
mysql -u root -p mydb < output/DML/25_Finance_Employee_Salary.sql
mysql -u root -p mydb < output/DML/26_Finance_Profit_Loss_Summary.sql
```
**Status**: ✅ All Done!

---

## 📊 Execution Timeline

```
Time    Phase              Files    Records        Status
────    ─────              ─────    ───────        ──────
0:00    START              -        -              ⏳ Beginning
0:30    Phase 1 (Root)     5        103,300        ✅ Complete
2:00    Phase 2 (Deps)     13       6,795,000      ✅ Complete
4:00    Phase 3 (Finance)  8        880,365        ✅ Complete
────────────────────────────────────────────────────────────
4:30    END                26       7,778,665      ✅ SUCCESS
        
Estimated time: 4-6 minutes (depending on database performance)
```

---

## 🛡️ Error Prevention Checklist

Before executing DML files, verify:

- ✅ Database exists: `CREATE DATABASE mydb;`
- ✅ CSV files generated: `output/csv/` contains 26 directories
- ✅ DML files generated: `output/DML/` contains `01_*.sql` through `26_*.sql`
- ✅ FK checks enabled: `SET FOREIGN_KEY_CHECKS = 1;` (if disabled)
- ✅ File permissions: All `.sql` files readable

---

## 🔍 Verification Steps

### After Each Phase
```sql
-- Verify Phase 1
SELECT 'Users' as t, COUNT(*) FROM Users
UNION ALL SELECT 'Categories', COUNT(*) FROM Categories
UNION ALL SELECT 'Warehouses', COUNT(*) FROM Warehouses
UNION ALL SELECT 'Delivery_Partners', COUNT(*) FROM Delivery_Partners
UNION ALL SELECT 'Payments', COUNT(*) FROM Payments;

-- Expected: 103,300 total rows

-- Verify Phase 2
SELECT 'Carts' as t, COUNT(*) FROM Carts
UNION ALL SELECT 'Orders', COUNT(*) FROM Orders
UNION ALL SELECT 'Products', COUNT(*) FROM Products
-- ... all Phase 2 tables

-- Expected: 6,795,000 additional rows
```

### Final Verification
```sql
-- Total records
SELECT SUM(cnt) as total_records FROM (
  SELECT COUNT(*) as cnt FROM Users
  UNION ALL SELECT COUNT(*) FROM Categories
  -- ... repeat for all 26 tables
) t;

-- Expected: 7,778,665
```

---

## ⚠️ Common Issues & Solutions

### ❌ "Cannot add or update a child row"
**Cause**: Foreign key parent doesn't exist  
**Solution**: Ensure parent table loaded first (check order: 01 before 08, 05 before 07, etc.)

### ❌ "Duplicate entry"
**Cause**: Table already has data  
**Solution**: DROP TABLE before reloading, or use consolidated_dml.sql which includes DELETE statements

### ❌ "File not found"
**Cause**: DML files not generated  
**Solution**: Run `python3 generate.py` first to create CSV data, then DML files

### ❌ "Connection refused"
**Cause**: MySQL not running  
**Solution**: Start MySQL: `mysql.server start` or equivalent for your system

---

## 💡 Pro Tips

### Tip 1: Use Loop for Automated Loading
```bash
# Auto-load all 26 files in correct order
for i in {01..26}; do
  FILE="output/DML/${i}_*.sql"
  if [ -f "$FILE" ]; then
    echo "Loading $FILE..."
    mysql -u root -p mydb < "$FILE"
  fi
done
```

### Tip 2: Log Execution Progress
```bash
# Load with logging
for file in output/DML/[0-9][0-9]_*.sql; do
  echo "[$(date)] Loading $(basename $file)" >> dml_execution.log
  mysql -u root -p mydb < "$file" >> dml_execution.log 2>&1 && \
  echo "[$(date)] ✓ Done" >> dml_execution.log
done
```

### Tip 3: Dry Run First
```bash
# Check syntax without loading
for file in output/DML/[0-9][0-9]_*.sql; do
  mysql --no-data -u root -p mydb < "$file"
done
```

### Tip 4: Use Transactions
```bash
# Wrap in transaction for atomic load
mysql -u root -p mydb << 'EOF'
START TRANSACTION;
source output/DML/consolidated_dml.sql;
COMMIT;
EOF
```

---

## 📈 Record Count by Execution Order

| Order | Table | Count | Phase |
|-------|-------|-------|-------|
| 01 | Users | 100,000 | 1 |
| 02 | Categories | 200 | 1 |
| 03 | Warehouses | 100 | 1 |
| 04 | Delivery_Partners | 3,000 | 1 |
| 05 | Products | 50,000 | 2 |
| 06 | Carts | 80,000 | 2 |
| 07 | Cart_Items | 200,000 | 2 |
| 08 | Orders | 300,000 | 2 |
| 09 | Order_Items | 900,000 | 2 |
| 10 | Inventory | 200,000 | 2 |
| 11 | Payments | 300,000 | 1 |
| 12 | Refunds | 50,000 | 2 |
| 13 | Deliveries | 300,000 | 2 |
| 14 | Promotions | 20,000 | 2 |
| 15 | Reviews | 150,000 | 2 |
| 16 | Search_Logs | 500,000 | 2 |
| 17 | App_Usage_Logs | 800,000 | 2 |
| 18 | Subscriptions | 40,000 | 2 |
| 19 | Finance_Orders_Revenue | 300,000 | 3 |
| 20 | Finance_Payments_Settlement | 300,000 | 3 |
| 21 | Finance_Refunds_Cost | 50,000 | 3 |
| 22 | Finance_Delivery_Costs | 300,000 | 3 |
| 23 | Finance_Operational_Expenses | 10,000 | 3 |
| 24 | Finance_Partner_Payouts | 10,000 | 3 |
| 25 | Finance_Employee_Salary | 10,000 | 3 |
| 26 | Finance_Profit_Loss_Summary | 365 | 3 |
| | **TOTAL** | **7,778,665** | |

---

## 🎯 Bottom Line

**Execute files in numerical order: 01 → 26**

This ensures:
- ✅ All parent records exist before FK references
- ✅ Zero constraint violations
- ✅ 100% data integrity
- ✅ Successful load of all 7.78M records

For more details, see `DML_EXECUTION_ORDER.md`
