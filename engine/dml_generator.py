#!/usr/bin/env python3
"""
DML Generator
Generates INSERT statements from CSV data for all tables
Creates both individual and consolidated DML files
"""

import json
import os
import sys
import csv
from pathlib import Path

# Configuration
OUTPUT_DIR = "output/csv"
DML_OUTPUT_DIR = "output/DML"
SCHEMA_CONFIG_FILE = "configs/schema_config.json"

# Database Configuration
SCHEMA_NAME = "SalesLT"  # Schema for all tables
USE_QUOTES = True  # Use square brackets [] for SQL Server, backticks `` for MySQL/PostgreSQL
# Set USE_QUOTES = True for SQL Server (uses [schema].[table])
# Set USE_QUOTES = False for MySQL/PostgreSQL (uses `schema`.`table`)

# Table execution order (respecting FK dependencies)
TABLE_ORDER = [
    "Users",
    "Categories",
    "Warehouses",
    "Delivery_Partners",
    "Products",
    "Carts",
    "Cart_Items",
    "Orders",
    "Order_Items",
    "Inventory",
    "Payments",
    "Refunds",
    "Deliveries",
    "Promotions",
    "Reviews",
    "Search_Logs",
    "App_Usage_Logs",
    "Subscriptions",
    "Finance_Orders_Revenue",
    "Finance_Payments_Settlement",
    "Finance_Refunds_Cost",
    "Finance_Delivery_Costs",
    "Finance_Operational_Expenses",
    "Finance_Partner_Payouts",
    "Finance_Employee_Salary",
    "Finance_Profit_Loss_Summary"
]

def quote_identifier(name):
    """Quote an identifier (table/column name) based on database type"""
    if USE_QUOTES:
        # SQL Server uses square brackets
        return f"[{name}]"
    else:
        # MySQL/PostgreSQL use backticks
        return f"`{name}`"

def quote_schema_table(table_name):
    """Quote schema.table reference"""
    if USE_QUOTES:
        # SQL Server format: [schema].[table]
        return f"[{SCHEMA_NAME}].[{table_name}]"
    else:
        # MySQL/PostgreSQL format: `schema`.`table`
        return f"`{SCHEMA_NAME}`.`{table_name}`"

def load_config():
    """Load schema configuration"""
    try:
        with open(SCHEMA_CONFIG_FILE) as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load config: {e}")
        return None

def get_table_columns(config, table_name):
    """Get columns for a table from config"""
    if table_name not in config["tables"]:
        return None
    return config["tables"][table_name].get("columns", {})

def format_value(value, col_type):
    """Format value for SQL INSERT statement"""
    if value is None or value == "":
        return "NULL"
    
    col_type_lower = col_type.lower() if isinstance(col_type, str) else str(col_type).lower()
    
    if "int" in col_type_lower or "long" in col_type_lower or "pk" in col_type_lower or "fk" in col_type_lower:
        return str(value)
    elif "boolean" in col_type_lower or "bool" in col_type_lower:
        return "1" if str(value).lower() in ["true", "1", "yes"] else "0"
    elif "decimal" in col_type_lower or "float" in col_type_lower or "double" in col_type_lower:
        return str(value)
    else:
        # String type - escape single quotes
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"

def get_csv_files(table_name):
    """Find CSV file for a table"""
    table_dir = os.path.join(OUTPUT_DIR, table_name)
    if not os.path.exists(table_dir):
        return None
    
    # Find .csv files
    for file in os.listdir(table_dir):
        if file.endswith(".csv"):
            return os.path.join(table_dir, file)
    return None

def generate_insert_statements(config, table_name):
    """Generate INSERT statements for a table from CSV data"""
    csv_file = get_csv_files(table_name)
    if not csv_file:
        print(f"[WARN] No CSV file found for {table_name}")
        return []
    
    columns_config = get_table_columns(config, table_name)
    if not columns_config:
        print(f"[WARN] No column config found for {table_name}")
        return []
    
    insert_statements = []
    
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            row_count = 0
            
            for row in reader:
                # Build INSERT statement
                column_names = list(row.keys())
                values = []
                
                for col in column_names:
                    value = row[col]
                    col_type = columns_config.get(col, {})
                    if isinstance(col_type, dict):
                        col_type = col_type.get("type", "string")
                    
                    formatted_value = format_value(value, col_type)
                    values.append(formatted_value)
                
                # Create INSERT statement
                columns_str = ", ".join(quote_identifier(col) for col in column_names)
                values_str = ", ".join(values)
                insert_stmt = f"INSERT INTO {quote_schema_table(table_name)} ({columns_str}) VALUES ({values_str});"
                insert_statements.append(insert_stmt)
                row_count += 1
            
            return insert_statements, row_count
    
    except Exception as e:
        print(f"[ERROR] Failed to generate INSERT for {table_name}: {e}")
        return [], 0

def create_individual_dml_files(config):
    """Create individual DML files for each table with execution order prefixes"""
    print("\nGenerating ordered DML files...")
    print("-" * 80)
    
    total_files = 0
    total_statements = 0
    
    for file_order, table_name in enumerate(TABLE_ORDER, start=1):
        insert_stmts, row_count = generate_insert_statements(config, table_name)
        
        if not insert_stmts:
            continue
        
        # Create filename with execution order
        # Format: {file_order_execution}_{tableName}.sql
        dml_filename = f"{file_order:02d}_{table_name}.sql"
        dml_file = os.path.join(DML_OUTPUT_DIR, dml_filename)
        
        try:
            with open(dml_file, 'w') as f:
                f.write(f"-- File Order: {file_order}\n")
                f.write(f"-- Table: {table_name}\n")
                f.write(f"-- INSERT statements for {table_name}\n")
                f.write(f"-- Generated: {row_count} rows\n")
                f.write(f"-- Execute in order: {file_order:02d}_{table_name}.sql\n\n")
                for stmt in insert_stmts:
                    f.write(stmt + "\n")
            
            print(f"[OK] {file_order:02d}_{table_name:35s} -> {row_count:8,d} rows")
            total_files += 1
            total_statements += row_count
        
        except Exception as e:
            print(f"[ERROR] Failed to write DML for {dml_filename}: {e}")
    
    print("-" * 80)
    print(f"[OK] Generated {total_files} ordered DML files with {total_statements:,d} total statements\n")
    return total_files, total_statements

def get_drop_statements(config):
    """Generate DELETE TABLE statements (reversed order for FK dependencies)"""
    drop_statements = []
    
    # Reverse order for drop
    for table_name in reversed(TABLE_ORDER):
        if table_name in config["tables"]:
            drop_statements.append(f"DELETE FROM {quote_schema_table(table_name)};\n")
    
    return drop_statements

def get_create_table_statements(config):
    """Generate CREATE TABLE statements in correct order"""
    create_statements = []
    
    for table_name in TABLE_ORDER:
        if table_name not in config["tables"]:
            continue
        
        table_config = config["tables"][table_name]
        columns_config = table_config.get("columns", {})
        primary_key = table_config.get("primary_key")
        
        # Start CREATE statement with schema
        create_stmt = f"CREATE TABLE {quote_schema_table(table_name)} (\n"
        column_defs = []
        
        # Add columns
        for col_name, col_config in columns_config.items():
            if isinstance(col_config, dict):
                col_type = col_config.get("type", "string")
            else:
                col_type = col_config
            
            # Map types to SQL types
            sql_type = map_type_to_sql(col_type)
            
            if col_name == primary_key:
                col_def = f"  {quote_identifier(col_name)} {sql_type} PRIMARY KEY"
            else:
                col_def = f"  {quote_identifier(col_name)} {sql_type}"
            
            column_defs.append(col_def)
        
        # Add FK constraints
        fk_config = table_config.get("foreign_keys", {})
        for fk_col, fk_info in fk_config.items():
            ref_table = fk_info.get("ref_table")
            ref_column = fk_info.get("ref_column")
            if ref_table and ref_column:
                fk_constraint = f"  FOREIGN KEY ({quote_identifier(fk_col)}) REFERENCES {quote_schema_table(ref_table)}({quote_identifier(ref_column)})"
                column_defs.append(fk_constraint)
        
        create_stmt += ",\n".join(column_defs) + "\n);\n\n"
        create_statements.append((table_name, create_stmt))
    
    return create_statements

def map_type_to_sql(data_type):
    """Map schema type to SQL type"""
    data_type_lower = str(data_type).lower()
    
    if "pk" in data_type_lower or "fk" in data_type_lower:
        return "BIGINT"
    elif "int" in data_type_lower:
        return "BIGINT"
    elif "long" in data_type_lower:
        return "BIGINT"
    elif "decimal" in data_type_lower:
        return "DECIMAL(19,2)"
    elif "float" in data_type_lower or "double" in data_type_lower:
        return "DOUBLE"
    elif "boolean" in data_type_lower or "bool" in data_type_lower:
        return "BOOLEAN"
    elif "timestamp" in data_type_lower or "datetime" in data_type_lower:
        return "TIMESTAMP"
    elif "date" in data_type_lower:
        return "DATE"
    elif "email" in data_type_lower:
        return "VARCHAR(255)"
    elif "phone" in data_type_lower:
        return "VARCHAR(20)"
    elif "enum" in data_type_lower:
        return "VARCHAR(100)"
    else:
        return "VARCHAR(255)"

def create_consolidated_dml(config):
    """Create consolidated DML script with DELETE, CREATE, and INSERT statements"""
    print("\nGenerating consolidated DML script...")
    print("-" * 80)
    
    consolidated_file = os.path.join(DML_OUTPUT_DIR, "consolidated_dml.sql")
    
    try:
        with open(consolidated_file, 'w') as f:
            # Header
            f.write("-- ============================================================================\n")
            f.write("-- CONSOLIDATED DML SCRIPT\n")
            f.write("-- ============================================================================\n")
            f.write("-- This script includes:\n")
            f.write("-- 1. CREATE SCHEMA (if needed)\n")
            f.write("-- 2. DELETE statements (in reverse order for FK dependencies)\n")
            f.write("-- 3. CREATE TABLE statements (in correct order)\n")
            f.write("-- 4. INSERT statements (with data from CSV files)\n")
            f.write("--\n")
            f.write("-- Execute this script in one shot for complete data setup\n")
            f.write("-- ============================================================================\n\n")
            
            # STEP 0: Create Schema
            if USE_QUOTES:
                # SQL Server syntax
                f.write(f"-- STEP 0: CREATE SCHEMA (if not exists)\n")
                f.write(f"-- ============================================================================\n\n")
                f.write(f"IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = '{SCHEMA_NAME}')\n")
                f.write(f"    CREATE SCHEMA {quote_identifier(SCHEMA_NAME)};\n\n")
            else:
                # MySQL/PostgreSQL syntax
                f.write(f"-- STEP 0: CREATE SCHEMA (if not exists)\n")
                f.write(f"-- ============================================================================\n\n")
                f.write(f"CREATE SCHEMA IF NOT EXISTS {quote_identifier(SCHEMA_NAME)};\n\n")
            
            # STEP 1: DELETE statements
            f.write("-- STEP 1: DELETE existing data (in reverse order for FK constraints)\n")
            f.write("-- ============================================================================\n\n")
            
            delete_stmts = get_drop_statements(config)
            for stmt in delete_stmts:
                f.write(stmt)
            
            f.write("\n")
            
            # STEP 2: CREATE TABLE statements
            f.write("-- STEP 2: CREATE TABLE statements (in correct FK order)\n")
            f.write("-- ============================================================================\n\n")
            
            create_stmts = get_create_table_statements(config)
            for table_name, create_stmt in create_stmts:
                f.write(create_stmt)
            
            f.write("\n")
            
            # STEP 3: INSERT statements
            f.write("-- STEP 3: INSERT statements (with validated data)\n")
            f.write("-- ============================================================================\n\n")
            
            total_inserts = 0
            for table_name in TABLE_ORDER:
                insert_stmts, row_count = generate_insert_statements(config, table_name)
                
                if insert_stmts:
                    f.write(f"-- {table_name} ({row_count} rows)\n")
                    for stmt in insert_stmts:
                        f.write(stmt + "\n")
                    f.write("\n")
                    total_inserts += row_count
            
            # Footer
            f.write("-- ============================================================================\n")
            f.write("-- SCRIPT COMPLETE\n")
            f.write("-- ============================================================================\n")
            f.write(f"-- Total rows inserted: {total_inserts:,}\n")
            f.write(f"-- Total tables: {len(TABLE_ORDER)}\n")
            f.write(f"-- Schema: {SCHEMA_NAME}\n")
            f.write("-- ============================================================================\n")
        
        print(f"[OK] Consolidated DML created: {consolidated_file}")
        print(f"     Total INSERT statements: {total_inserts:,}")
        print(f"     Schema: {SCHEMA_NAME}")
        print("-" * 80)
        
        return True
    
    except Exception as e:
        print(f"[ERROR] Failed to create consolidated DML: {e}")
        return False

def main():
    # Validate paths
    if not os.path.exists(SCHEMA_CONFIG_FILE):
        print(f"[ERROR] Schema config not found: {SCHEMA_CONFIG_FILE}")
        return False
    
    if not os.path.exists(OUTPUT_DIR):
        print(f"[ERROR] Output directory not found: {OUTPUT_DIR}")
        return False
    
    # Load configuration
    config = load_config()
    if not config:
        return False
    
    # Create DML output directory
    os.makedirs(DML_OUTPUT_DIR, exist_ok=True)
    
    print("\n" + "="*80)
    print("DML GENERATION")
    print("="*80)
    
    # Generate individual DML files
    individual_files, total_statements = create_individual_dml_files(config)
    
    # Generate consolidated DML script
    success = create_consolidated_dml(config)
    
    if success:
        print("\n" + "="*80)
        print("[OK] DML GENERATION COMPLETE")
        print("="*80)
        print(f"\nOutput locations:")
        print(f"  Ordered DML files: {DML_OUTPUT_DIR}/")
        print(f"    Format: NN_TableName.sql (01_Users.sql, 02_Categories.sql, etc.)")
        print(f"    Files execute in numerical order (01, 02, 03, etc.)")
        print(f"    Based on PK-FK dependency relationships")
        print(f"  Consolidated DML: {os.path.join(DML_OUTPUT_DIR, 'consolidated_dml.sql')}")
        print(f"\nGenerated:")
        print(f"  Total ordered DML files: {individual_files}")
        print(f"  Total INSERT statements: {total_statements:,}")
        print(f"\nNext: Execute files in order (01_*.sql, 02_*.sql, etc.) or use consolidated_dml.sql\n")
        return True
    
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
