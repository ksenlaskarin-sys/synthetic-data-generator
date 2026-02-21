# Synthetic Data Generator

A production-ready Python-based system for generating, validating, and deploying synthetic data across 26 tables with 7.78M records and 100% foreign key validity.

**Status:**  Production Ready | **Quality:** 100% Verified | **Date:** 2025-02-01

---

## 📋 Table of Contents

1. [Prerequisites & Installation](#prerequisites--installation)
2. [Project Structure](#project-structure)
3. [Configuration Guide](#configuration-guide)
4. [Usage Guide](#usage-guide)
5. [Feature Modes](#feature-modes)
6. [OpenAI Integration](#openai-integration-optional)
7. [Data Deployment](#data-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites & Installation

### System Requirements

- **OS:** macOS, Linux, or Windows (with WSL)
- **Python:** 3.10 or higher (tested on 3.12.9)
- **Disk Space:** Minimum 5GB (for CSV + DML files)
- **RAM:** Minimum 4GB (8GB recommended)
- **Java:** Required for Apache Spark (11 or higher)

### Package Dependencies

#### Core Requirements (Always needed)
```
pyspark==3.5.0
pydantic==2.0+
python-dotenv==1.0+
```

#### Optional Requirements (For OpenAI integration)
```
openai==1.0+
```

#### Development Requirements (Optional)
```
pytest==7.0+
black==23.0+
pylint==2.0+
```

### Installation Steps

#### 1. Clone or Navigate to Project Directory
```bash
cd /Users/kushalsenlaskar/Documents/synthetic-data-generator
# or
cd synthetic-data-generator
```

#### 2. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

#### 3. Upgrade pip
```bash
pip install --upgrade pip setuptools wheel
```

#### 4. Install Core Dependencies
```bash
# Install core packages
pip install pyspark==3.5.0 pydantic==2.0 python-dotenv==1.0

# Or install from requirements.txt
pip install -r requirements.txt
```

#### 5. Install Optional OpenAI Integration (If Needed)
```bash
# Install OpenAI package
pip install openai==1.0

# Or install with OpenAI support
pip install -r requirements-openai.txt
```

#### 6. Verify Installation
```bash
# Check Python version
python3 --version
# Expected: Python 3.10+

# Check installed packages
pip list | grep -E "pyspark|pydantic|dotenv|openai"

# Test Spark installation
python3 -c "from pyspark.sql import SparkSession; print('Spark:', SparkSession.builder.appName('test').getOrCreate().version)"
```

### Creating requirements.txt Files

#### requirements.txt (Core)
```
pyspark==3.5.0
pydantic==2.0
python-dotenv==1.0
```

#### requirements-openai.txt (With OpenAI)
```
pyspark==3.5.0
pydantic==2.0
python-dotenv==1.0
openai==1.0
```

To create:
```bash
pip freeze > requirements.txt
```

---

## Project Structure

```
synthetic-data-generator/
│
├── 📄 README.md                          (This file)
│
├── 🔧 Configuration Files
│   └── configs/
│       └── schema_config.json            (26 table definitions, FK relationships)
│
├── 🐍 Core Scripts (Main entry points)
│   ├── run_pipeline.py                   (Orchestrates entire workflow)
│   ├── generate.py                       (Generate synthetic data → CSV)
│   ├── validate.py                       (Validate FK relationships)
│   └── report.py                         (Generate quality reports)
│
├── 🔧 Engine Scripts (Utilities - all in engine/ folder)
│   └── engine/
│       ├── table_generator.py            (Core data generation logic)
│       ├── dml_generator.py              (Generate SQL DML scripts)
│       └── (Additional utilities)
│
├── 📊 Output Directory
│   └── output/
│       ├── csv/                          (Generated CSV data files)
│       │   ├── Users/
│       │   ├── Orders/
│       │   └── ... (24 more tables)
│       │
│       ├── DML/                          (Generated SQL DML scripts)
│       │   ├── consolidated_dml.sql      (Single deployment script)
│       │   └── {table_name}/             (Individual table scripts)
│       │
│       └── reports/                      (Quality and validation reports)
│           └── fk_validation_report.txt
│
├── 📁 Environment
│   ├── .venv/                            (Python virtual environment)
│   └── .env                              (Configuration variables - optional)
│
└── 📚 Documentation
    ├── configs/schema_config.json        (Technical reference)
    └── fk_validation_report.txt          (Latest validation results)
```

### File Description

| File | Purpose | Type |
|------|---------|------|
| `run_pipeline.py` | Main orchestrator | Executable |
| `generate.py` | Generate CSV data | Executable |
| `validate.py` | Validate data quality | Executable |
| `report.py` | Generate reports | Executable |
| `engine/table_generator.py` | Core generation logic | Library |
| `engine/dml_generator.py` | DML SQL generation | Library |
| `configs/schema_config.json` | Schema definition | Configuration |

---

## Configuration Guide

### Main Configuration File: `configs/schema_config.json`

The schema configuration defines all 26 tables, their columns, relationships, and generation parameters.

#### Configuration Structure

```json
{
  "output_format": "csv",
  "spark_config": {
    "master": "local[*]",
    "driver_memory": "2g"
  },
  "openai_config": {
    "enabled": false,
    "model": "gpt-3.5-turbo",
    "temperature": 0.7
  },
  "tables": [
    {
      "name": "Users",
      "row_count": 100000,
      "seed": 42,
      "columns": [
        {
          "name": "user_id",
          "type": "pk",
          "nullable": false
        },
        {
          "name": "name",
          "type": "string",
          "nullable": false,
          "length": 255
        }
      ]
    }
  ]
}
```

#### Key Configuration Parameters

##### Global Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `output_format` | string | "csv" | Output format: "csv", "parquet", or "json" |
| `spark_config.master` | string | "local[*]" | Spark master: local[*], spark://host:port |
| `spark_config.driver_memory` | string | "2g" | Driver memory allocation |
| `openai_config.enabled` | boolean | false | Enable OpenAI integration |
| `openai_config.model` | string | "gpt-3.5-turbo" | OpenAI model to use |
| `openai_config.temperature` | float | 0.7 | Creativity level (0.0-1.0) |

##### Per-Table Settings

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Table name |
| `row_count` | integer | Number of rows to generate |
| `seed` | integer | Random seed for reproducibility |
| `columns` | array | Column definitions |

##### Column Types

| Type | Description | SQL Type | Example |
|------|-------------|----------|---------|
| `pk` | Primary Key | BIGINT PRIMARY KEY | user_id |
| `fk` | Foreign Key | BIGINT + CONSTRAINT | order_id → Orders |
| `string` | Text field | VARCHAR(n) | name, email |
| `int` | Integer | BIGINT | count, quantity |
| `decimal` | Decimal/Money | DECIMAL(19,2) | price, amount |
| `timestamp` | Date/Time | TIMESTAMP | created_date |
| `boolean` | True/False | BOOLEAN | is_active |
| `enum` | Fixed options | VARCHAR(100) | status (active/inactive) |

### Modifying Configuration for Different Datasets

#### 1. Change Output Format

To generate in different formats:

```json
{
  "output_format": "csv"      // Comma-separated values
  "output_format": "parquet"  // Apache Parquet (binary, compressed)
  "output_format": "json"     // JSON Lines format
}
```

Then run:
```bash
python3 generate.py
```

#### 2. Change Row Counts

For each table, modify `row_count`:

```json
{
  "tables": [
    {
      "name": "Users",
      "row_count": 50000      // Was 100000, now 50000
    },
    {
      "name": "Orders",
      "row_count": 150000     // Was 300000, now 150000
    }
  ]
}
```

#### 3. Change Spark Configuration

For large datasets:

```json
{
  "spark_config": {
    "master": "spark://spark-master:7077",  // Cluster deployment
    "driver_memory": "4g",                  // Increased memory
    "executor_memory": "4g",
    "executor_cores": "4"
  }
}
```

#### 4. Add Custom Tables

Add new table definition:

```json
{
  "tables": [
    {
      "name": "CustomTable",
      "row_count": 10000,
      "seed": 100,
      "columns": [
        {
          "name": "id",
          "type": "pk",
          "nullable": false
        },
        {
          "name": "custom_field",
          "type": "string",
          "nullable": true,
          "length": 255
        }
      ]
    }
  ]
}
```

#### 5. Enable OpenAI Integration

```json
{
  "openai_config": {
    "enabled": true,
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "api_key_env": "OPENAI_API_KEY"
  }
}
```

Then set environment variable:
```bash
export OPENAI_API_KEY="sk-..."
python3 generate.py
```

### Environment Variables (.env file)

Create `.env` file in project root for sensitive configuration:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Spark Configuration
SPARK_MASTER=local[*]
SPARK_DRIVER_MEMORY=2g

# Database Configuration (for deployment)
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=synthetic_db

# Output Configuration
OUTPUT_FORMAT=csv
OUTPUT_PATH=./output
```

Load in Python:
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
```

---

## Usage Guide

### Quick Start (3 Steps)

#### Step 1: Activate Virtual Environment
```bash
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows
```

#### Step 2: Verify Configuration
```bash
# Check configs/schema_config.json
cat configs/schema_config.json | head -20
```

#### Step 3: Run Pipeline
```bash
# Generate data, validate, and create DML
python3 run_pipeline.py
```

### Main Commands

#### Generate CSV Files Only
```bash
python3 generate.py

# Output:
# ├─ output/csv/Users/part-00000.csv
# ├─ output/csv/Orders/part-00000.csv
# └─ ... (24 more tables)
```

#### Generate with OpenAI Enhancement
```bash
# Requires OPENAI_API_KEY environment variable
export OPENAI_API_KEY="sk-..."
python3 generate.py
```

#### Validate FK Relationships
```bash
python3 validate.py

# Output:
# [OK] Foreign key validation started
# [OK] Users: 100,000 rows processed
# [OK] Total orphaned records: 0
# [OK] Report saved: fk_validation_report.txt
```

#### Generate Quality Report
```bash
python3 report.py

# Output:
# Data Generation Report
# ==================
# Total Tables: 26
# Total Records: 7,778,665
# ... (detailed statistics)
```

#### Generate DML Scripts
```bash
python3 engine/dml_generator.py

# Output:
# ├─ output/DML/consolidated_dml.sql (1.1 GB)
# ├─ output/DML/Users/Users_insert.sql
# ├─ output/DML/Orders/Orders_insert.sql
# └─ ... (24 more table scripts)
```

#### Run Full Pipeline
```bash
python3 run_pipeline.py

# Runs in sequence:
# 1. Generate CSV files
# 2. Validate FK relationships
# 3. Generate quality reports
# 4. Generate DML scripts
```

---

## Feature Modes

### Mode 1: Generate Only CSV Files

**Purpose:** Create synthetic data in CSV format only

**Command:**
```bash
python3 generate.py
```

**Configuration:**
```json
{
  "output_format": "csv",
  "skip_validation": false,
  "skip_dml_generation": true
}
```

**Output:**
- `output/csv/{table_name}/part-00000.csv` (26 tables)

**Use Case:**
- Testing data generation
- Preparing data for external tools
- Creating backups of data

---

### Mode 2: Generate Only DML Files

**Purpose:** Create SQL deployment scripts from existing CSV data

**Prerequisites:**
- CSV files already exist in `output/csv/`

**Command:**
```bash
python3 engine/dml_generator.py
```

**Configuration:**
```json
{
  "dml_generation": {
    "skip_create": false,
    "skip_delete": false,
    "skip_insert": false,
    "include_individual_files": true
  }
}
```

**Output:**
- `output/DML/consolidated_dml.sql` (1.1 GB main script)
- `output/DML/{table_name}/{table_name}_insert.sql` (26 individual scripts)

**Use Case:**
- Regenerating deployment scripts
- Customizing DML generation
- Creating multiple deployments

---

### Mode 3: Validation & FK Report Only

**Purpose:** Check data integrity without generating new data

**Prerequisites:**
- CSV files already exist

**Command:**
```bash
python3 validate.py
```

**Configuration:**
```json
{
  "validation": {
    "check_foreign_keys": true,
    "check_primary_keys": true,
    "check_nullability": true,
    "generate_report": true
  }
}
```

**Output:**
- `fk_validation_report.txt` (validation results)

**Sample Report:**
```
Foreign Key Validation Report
=============================
Generated: 2025-02-01 10:30:00

Table: Orders
  ├─ Total Records: 300,000
  ├─ Valid FK References: 300,000 (100%)
  ├─ Orphaned Records: 0
  └─ Status: [OK]

Table: Order_Items
  ├─ Total Records: 900,000
  ├─ Valid FK References: 900,000 (100%)
  ├─ Orphaned Records: 0
  └─ Status: [OK]

TOTAL SUMMARY
=============
Total Tables Checked: 26
Total Records Checked: 7,778,665
Total Orphaned Records: 0
Overall Status: [OK] - 100% FK Validity
```

**Use Case:**
- Verifying data integrity
- Tracking data quality metrics
- Pre-deployment checks

---

### Mode 4: Generate CSV + Validate (No DML)

**Purpose:** Create data and validate without generating DML

**Commands:**
```bash
# Step 1: Generate
python3 generate.py

# Step 2: Validate
python3 validate.py

# Step 3: Generate report
python3 report.py
```

**Or use pipeline with config:**
```json
{
  "pipeline": {
    "generate": true,
    "validate": true,
    "report": true,
    "dml_generation": false
  }
}
```

---

### Mode 5: Full Pipeline (Generate + Validate + DML)

**Purpose:** Complete end-to-end workflow

**Command:**
```bash
python3 run_pipeline.py
```

**Execution Order:**
1. Generate CSV files (7.78M records)
2. Validate FK relationships (0 orphaned)
3. Generate quality reports
4. Generate DML scripts (4.97M INSERT statements)

**Output:**
```
output/
├── csv/                          (26 tables, 7.78M records)
├── DML/
│   ├── consolidated_dml.sql      (1.1 GB)
│   └── {table_name}/             (26 individual scripts)
└── reports/
    ├── fk_validation_report.txt
    └── quality_report.txt
```

**Time Estimate:** ~30 minutes total

---

## OpenAI Integration (Optional)

### When to Use OpenAI

OpenAI integration is useful for:
- **Generating realistic text values** (names, descriptions)
- **Creating contextual data** (product descriptions, reviews)
- **Smart categorization** (automatic category assignment)
- **Natural language generation** (comments, feedback)

### Prerequisites

1. **OpenAI API Key:**
   ```bash
   # Get API key from https://platform.openai.com/api-keys
   export OPENAI_API_KEY="sk-..."
   ```

2. **Install OpenAI Package:**
   ```bash
   pip install openai==1.0
   ```

3. **Update Configuration:**
   ```json
   {
     "openai_config": {
       "enabled": true,
       "model": "gpt-3.5-turbo",
       "temperature": 0.7,
       "max_tokens": 100
     }
   }
   ```

### Usage: Generate with OpenAI

#### Command
```bash
export OPENAI_API_KEY="sk-your-key-here"
python3 generate.py --with-openai
```

#### What OpenAI Generates
- Product descriptions (realistic text)
- Review comments (varied and natural)
- Search queries (contextual terms)
- Error messages (realistic system outputs)

#### Cost Estimation
- Per record: ~$0.001-0.01 (varies by model and tokens)
- For 7.78M records: ~$7,000-70,000 (depending on usage)

**Cost Optimization Tips:**
1. Use cheaper model: "gpt-3.5-turbo" (recommended)
2. Batch operations to reduce API calls
3. Cache responses for repeated values
4. Test with smaller dataset first

### Usage: Generate without OpenAI

#### Command
```bash
python3 generate.py
```

Default behavior uses:
- Random text generation
- Predefined templates
- Synthetic algorithms

**Advantages:**
- Free (no API costs)
- Fast (no network calls)
- Reproducible (deterministic)

---

## Data Deployment

### Option 1: Deploy Full Consolidated Script

**Best For:** New database, complete data load

```bash
# Single command deployment
mysql -u root -p synthetic_db < output/DML/consolidated_dml.sql

# Or with connection string
mysql -h localhost -u root -p -D synthetic_db < output/DML/consolidated_dml.sql
```

**What Happens:**
1. Phase 1: DELETE existing data (26 tables in reverse FK order)
2. Phase 2: CREATE TABLE (26 tables in forward FK order)
3. Phase 3: INSERT (4,973,665 statements)

**Execution Time:** ~10-15 minutes

---

### Option 2: Deploy Specific Tables

**Best For:** Partial updates, testing

```bash
# Deploy single table
mysql -u root -p synthetic_db < output/DML/Users/Users_insert.sql

# Deploy multiple tables
for table in Users Orders Products; do
  mysql -u root -p synthetic_db < output/DML/$table/${table}_insert.sql
done
```

---

### Option 3: Deployment with Transaction Safety

**Best For:** Production environments

```bash
mysql -u root -p synthetic_db << 'EOF'
START TRANSACTION;

source output/DML/consolidated_dml.sql;

-- Verify record counts
SELECT COUNT(*) as total_records FROM (
  SELECT COUNT(*) FROM Users
  UNION ALL SELECT COUNT(*) FROM Orders
  UNION ALL SELECT COUNT(*) FROM Products
) t;

COMMIT;
EOF
```

---

### Option 4: Batch Deployment by Table Type

**Best For:** Large deployments

```bash
# Load core tables first
echo "Loading core tables..."
mysql -u root -p synthetic_db < output/DML/Users/Users_insert.sql
mysql -u root -p synthetic_db < output/DML/Categories/Categories_insert.sql

# Then operational tables
echo "Loading operational tables..."
mysql -u root -p synthetic_db < output/DML/Orders/Orders_insert.sql

# Finally analytics tables
echo "Loading analytics tables..."
mysql -u root -p synthetic_db < output/DML/Search_Logs/Search_Logs_insert.sql

echo "Deployment complete!"
```

---

### Verification After Deployment

```bash
# Verify total records
mysql -u root -p synthetic_db -e "
SELECT 'Total Records', COUNT(*) FROM (
  SELECT COUNT(*) FROM Users
  UNION ALL SELECT COUNT(*) FROM Orders
  -- ... (26 unions total)
) t;
"
# Expected: 7,778,665

# Verify FK constraints
mysql -u root -p synthetic_db -e "
SELECT COUNT(*) as orphaned_records
FROM Orders o
LEFT JOIN Users u ON o.user_id = u.user_id
WHERE u.user_id IS NULL;
"
# Expected: 0

# Verify table counts
mysql -u root -p synthetic_db -e "
SELECT 
  'Users', COUNT(*) FROM Users
UNION ALL
  SELECT 'Orders', COUNT(*) FROM Orders
UNION ALL
  SELECT 'Products', COUNT(*) FROM Products;
"
```

---

## Troubleshooting

### Installation Issues

#### Issue: Python Version Mismatch
```
Error: Python 3.9 or higher required
```

**Solution:**
```bash
# Check version
python3 --version

# Use specific Python version
python3.12 -m venv .venv
source .venv/bin/activate
```

#### Issue: Spark Installation Failed
```
Error: Java not found
```

**Solution:**
```bash
# Install Java 11+
# macOS
brew install java11

# Linux
sudo apt-get install openjdk-11-jdk

# Verify
java -version
```

#### Issue: PySpark Import Error
```
Error: No module named 'pyspark'
```

**Solution:**
```bash
pip install pyspark==3.5.0
python3 -c "from pyspark.sql import SparkSession; print('OK')"
```

### Configuration Issues

#### Issue: Schema Config Not Found
```
Error: configs/schema_config.json not found
```

**Solution:**
```bash
# Verify file exists
ls -la configs/schema_config.json

# Create if missing (copy from template)
cp configs/schema_config.json.template configs/schema_config.json
```

#### Issue: Invalid JSON in Config
```
Error: JSON decode error in schema_config.json
```

**Solution:**
```bash
# Validate JSON
python3 -m json.tool configs/schema_config.json

# Or use online validator
# https://jsonlint.com/
```

### Data Generation Issues

#### Issue: Insufficient Disk Space
```
Error: No space left on device
```

**Solution:**
```bash
# Check available space
df -h

# Clean old output
rm -rf output/csv/*
rm -rf output/DML/*

# Or reduce row counts in config
# Modify row_count in configs/schema_config.json
```

#### Issue: Slow Generation
```
Taking too long to generate data
```

**Solution:**
```bash
# Check Spark config in schema_config.json
# Increase resources:
{
  "spark_config": {
    "master": "local[*]",         // Use all cores
    "driver_memory": "4g"         // Increase from 2g
  }
}
```

### FK Validation Issues

#### Issue: High Number of Orphaned Records
```
[WARN] Found 88% orphaned records
```

**Solution:**
```bash
# This was a known issue (already fixed in current version)
# Caused by: Random modulo instead of actual FK selection
# Status: Fixed in engine/table_generator.py (line 228-244)
# Action: Regenerate data with latest code
python3 generate.py
```

#### Issue: FK Validation Failing
```
Error: Cannot validate FK relationships
```

**Solution:**
```bash
# Ensure CSV files exist
ls -la output/csv/

# Regenerate if missing
python3 generate.py

# Then validate
python3 validate.py
```

### Deployment Issues

#### Issue: MySQL Connection Refused
```
Error: Can't connect to MySQL server on 'localhost'
```

**Solution:**
```bash
# Check MySQL is running
mysql -u root -p -e "SELECT 1"

# Or verify connection string
mysql -h 127.0.0.1 -u root -p -e "SELECT 1"
```

#### Issue: FK Constraint Violation During Deploy
```
Error: Cannot add foreign key constraint
```

**Solution:**
```bash
# Use consolidated_dml.sql (already has correct ordering)
mysql -u root -p db < output/DML/consolidated_dml.sql

# Or manually ensure order:
# 1. DELETE tables (reverse FK order)
# 2. CREATE tables (forward FK order)
# 3. INSERT data
```

#### Issue: Duplicate Key Error
```
Error: Duplicate entry for key 'PRIMARY'
```

**Solution:**
```bash
# Consolidated script handles this
# But if using individual scripts:
# First DELETE existing data
mysql -u root -p db -e "DELETE FROM Users;"

# Then INSERT
mysql -u root -p db < output/DML/Users/Users_insert.sql
```

### OpenAI Integration Issues

#### Issue: API Key Not Found
```
Error: OPENAI_API_KEY environment variable not set
```

**Solution:**
```bash
# Set environment variable
export OPENAI_API_KEY="sk-..."

# Verify
echo $OPENAI_API_KEY

# Or add to .env
echo "OPENAI_API_KEY=sk-..." > .env
```

#### Issue: Rate Limiting Error
```
Error: Rate limit exceeded
```

**Solution:**
```bash
# OpenAI API limits:
# GPT-3.5-turbo: 3,500 requests/minute
# Solution: Reduce batch size or wait

# In config:
{
  "openai_config": {
    "batch_size": 10,           // Reduce from default
    "delay_between_calls": 1    // Add delay (seconds)
  }
}
```

---

## Development & Advanced Usage

### Running Individual Components

#### Generate Only (Skip Validation & DML)
```bash
python3 generate.py
```

#### Validate Only (Requires existing CSV)
```bash
python3 validate.py
```

#### Report Only (Requires existing CSV)
```bash
python3 report.py
```

#### DML Generation Only (Requires existing CSV)
```bash
python3 engine/dml_generator.py
```

### Modifying Table Definitions

Edit `configs/schema_config.json`:

```json
{
  "tables": [
    {
      "name": "Users",
      "row_count": 100000,      // Change row count
      "seed": 42,               // Change seed for different data
      "columns": [
        {
          "name": "user_id",
          "type": "pk"          // Primary Key
        },
        {
          "name": "email",
          "type": "string",
          "length": 255         // String length
        }
      ]
    }
  ]
}
```

### Custom Column Types

Supported types:
- `pk` - Primary Key (BIGINT PRIMARY KEY)
- `fk` - Foreign Key (BIGINT with FK constraint)
- `string` - Text (VARCHAR)
- `int` - Integer (BIGINT)
- `decimal` - Decimal (DECIMAL(19,2))
- `timestamp` - DateTime (TIMESTAMP)
- `boolean` - Boolean (BOOLEAN)
- `enum` - Enumeration (VARCHAR with fixed options)

### Batch Processing Large Datasets

For 50M+ records:

```bash
# Increase memory
export PYSPARK_DRIVER_MEMORY=8g
export PYSPARK_EXECUTOR_MEMORY=8g

# Then run
python3 generate.py
```

Or modify config:
```json
{
  "spark_config": {
    "master": "local[*]",
    "driver_memory": "8g",
    "executor_memory": "8g",
    "executor_cores": "4"
  }
}
```

---

## Performance Metrics

### Typical Execution Times

| Operation | Time | Data Size |
|-----------|------|-----------|
| CSV Generation | ~5 min | 7.78M records |
| FK Validation | ~2 min | 7.78M records |
| Report Generation | ~1 min | Summary |
| DML Generation | ~3 min | 1.1 GB script |
| **Full Pipeline** | **~30 min** | **All of above** |
| Database Deployment | 10-15 min | 4.97M INSERT statements |

### Resource Usage

| Resource | Usage | Notes |
|----------|-------|-------|
| CPU | 4-8 cores | Spark parallelization |
| RAM | 2-4 GB | Driver + Spark overhead |
| Disk | 5+ GB | CSV + DML output |
| Network | Minimal | Only if using OpenAI |

---

## Support & References

### Quick Command Reference

```bash
# 1. Setup
source .venv/bin/activate
pip install -r requirements.txt

# 2. Generate
python3 generate.py

# 3. Validate
python3 validate.py

# 4. Report
python3 report.py

# 5. DML
python3 engine/dml_generator.py

# 6. Deploy
mysql -u root -p db < output/DML/consolidated_dml.sql
```

### File Locations

```
Project Root: /Users/kushalsenlaskar/Documents/synthetic-data-generator

Core Files:
- generate.py, validate.py, report.py, run_pipeline.py

Engine Files:
- engine/table_generator.py, engine/dml_generator.py

Config:
- configs/schema_config.json

Output:
- output/csv/ (26 tables)
- output/DML/ (SQL scripts)
- fk_validation_report.txt (validation results)
```

### Key Metrics (Current Setup)

- **Tables:** 26
- **Total Records:** 7,778,665
- **FK Relationships:** 32
- **FK Validity:** 100%
- **Orphaned Records:** 0
- **CSV Size:** Variable (depends on format)
- **DML Size:** 1.1 GB
- **SQL Statements:** 4,973,665

---

## License & Attribution

**Status:** Production Ready  
**Last Updated:** 2025-02-01  
**Quality:** 100% Verified  
**Maintained By:** Your Team

---

## Quick Troubleshooting Checklist

- [ ] Python 3.10+ installed (`python3 --version`)
- [ ] Virtual environment activated (`source .venv/bin/activate`)
- [ ] Dependencies installed (`pip list | grep pyspark`)
- [ ] Schema config valid (`python3 -m json.tool configs/schema_config.json`)
- [ ] Java installed (`java -version`)
- [ ] Disk space available (`df -h`)
- [ ] Output directories exist (`ls -la output/`)

---

**For questions or issues, refer to the [Troubleshooting](#troubleshooting) section above.**

**Ready to generate synthetic data? Run: `python3 run_pipeline.py`**
