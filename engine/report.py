#!/usr/bin/env python3
"""
Data Reporting and Statistics
Generates comprehensive reports on generated data
"""

import json
import os
import sys
from pyspark.sql import SparkSession

# Load output format from config
with open("configs/schema_config.json") as f:
    schema_config = json.load(f)
OUTPUT_FORMAT = schema_config.get("output_format", "csv").lower()
OUTPUT_DIR = f"output/{OUTPUT_FORMAT}"

def load_table(spark, table_name):
    """Load a table based on configured output format"""
    path = os.path.join(OUTPUT_DIR, table_name)
    try:
        if OUTPUT_FORMAT == "csv":
            return spark.read.option("header", "true").option("inferSchema", "true").csv(path)
        elif OUTPUT_FORMAT == "parquet":
            return spark.read.parquet(path)
        elif OUTPUT_FORMAT == "json":
            return spark.read.json(path)
    except:
        return None

def table_statistics(spark):
    """Display statistics for all tables"""
    print("\n" + "="*80)
    print("TABLE STATISTICS")
    print("="*80)
    
    with open("configs/schema_config.json") as f:
        config = json.load(f)
    
    print(f"\n{'Table Name':<30} {'Row Count':>15} {'Columns':>10}")
    print("-" * 80)
    
    total_rows = 0
    total_cols = 0
    
    for table_name in sorted(config["tables"].keys()):
        df = load_table(spark, table_name)
        if df is None:
            print(f"{table_name:<30} {'MISSING':>15}")
            continue
        
        row_count = df.count()
        col_count = len(df.columns)
        
        print(f"{table_name:<30} {row_count:>15,d} {col_count:>10}")
        
        total_rows += row_count
        total_cols += col_count
    
    print("-" * 80)
    print(f"{'TOTAL':<30} {total_rows:>15,d} {total_cols:>10}")
    print()

def column_details(spark, table_name):
    """Show details for a specific table"""
    df = load_table(spark, table_name)
    if df is None:
        print(f"[ERROR] Table '{table_name}' not found")
        return
    
    print(f"\n{'='*80}")
    print(f"TABLE: {table_name}")
    print(f"{'='*80}")
    
    print(f"\nColumns ({len(df.columns)} total):")
    print(f"\n{'Column Name':<30} {'Data Type':<15} {'Nullable':>10}")
    print("-" * 80)
    
    for field in df.schema.fields:
        nullable = "Yes" if field.nullable else "No"
        print(f"{field.name:<30} {str(field.dataType):<15} {nullable:>10}")
    
    print(f"\nRow count: {df.count():,}")
    
    # Sample data
    print(f"\nSample data (first 5 rows):")
    df.limit(5).show(truncate=False)

def foreign_key_report(spark):
    """Detailed FK relationships report"""
    print("\n" + "="*80)
    print("FOREIGN KEY RELATIONSHIPS")
    print("="*80)
    
    with open("configs/schema_config.json") as f:
        config = json.load(f)
    
    fk_count = 0
    print()
    
    for table_name, table_config in sorted(config["tables"].items()):
        fk_config = table_config.get("foreign_keys", {})
        
        if not fk_config:
            continue
        
        for fk_col, fk_info in fk_config.items():
            fk_count += 1
            parent_table = fk_info["ref_table"]
            parent_pk = fk_info["ref_column"]
            
            parent_df = load_table(spark, parent_table)
            child_df = load_table(spark, table_name)
            
            if parent_df is None or child_df is None:
                continue
            
            total = child_df.count()
            valid = child_df.join(
                parent_df.select(parent_pk).distinct(),
                child_df[fk_col] == parent_df[parent_pk],
                "inner"
            ).count()
            
            orphaned = total - valid
            percentage = (valid / total * 100) if total > 0 else 0
            
            status = "[OK]" if orphaned == 0 else "[FAIL]"
            
            print(f"{status} {table_name:30s}.{fk_col:15s} → {parent_table:30s}.{parent_pk:15s}")
            print(f"    Valid: {valid:,d}/{total:,d} ({percentage:.1f}%)  Orphaned: {orphaned:,d}")
    
    print(f"\nTotal FK relationships: {fk_count}")
    print()

def data_quality_report(spark):
    """Data quality and validation report"""
    print("\n" + "="*80)
    print("DATA QUALITY REPORT")
    print("="*80)
    
    with open("configs/schema_config.json") as f:
        config = json.load(f)
    
    total_records = 0
    total_valid = 0
    total_fks = 0
    
    for table_name, table_config in config["tables"].items():
        fk_config = table_config.get("foreign_keys", {})
        
        for fk_col, fk_info in fk_config.items():
            total_fks += 1
            parent_table = fk_info["ref_table"]
            parent_pk = fk_info["ref_column"]
            
            parent_df = load_table(spark, parent_table)
            child_df = load_table(spark, table_name)
            
            if parent_df is None or child_df is None:
                continue
            
            total = child_df.count()
            valid = child_df.join(
                parent_df.select(parent_pk).distinct(),
                child_df[fk_col] == parent_df[parent_pk],
                "inner"
            ).count()
            
            total_records += total
            total_valid += valid
    
    invalid_records = total_records - total_valid
    percentage_valid = (total_valid / total_records * 100) if total_records > 0 else 0
    
    print(f"\nReferential Integrity Check:")
    print(f"   Total FK references:      {total_records:,}")
    print(f"   Valid references:         {total_valid:,}")
    print(f"   Invalid references:       {invalid_records:,}")
    print(f"   Validity percentage:      {percentage_valid:.2f}%")
    
    if invalid_records == 0:
        print(f"\n[OK] Perfect referential integrity: 100% of records have valid parent references")
    else:
        print(f"\n[WARN] Referential integrity issues detected: {percentage_valid:.2f}% valid")
    
    print()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Data reporting and statistics")
    parser.add_argument("--stats", action="store_true", help="Show table statistics")
    parser.add_argument("--table", type=str, help="Show details for specific table")
    parser.add_argument("--fk", action="store_true", help="Show FK relationships")
    parser.add_argument("--quality", action="store_true", help="Show data quality report")
    parser.add_argument("--all", action="store_true", help="Show all reports")
    
    args = parser.parse_args()
    
    # If no args, show all
    if not any([args.stats, args.table, args.fk, args.quality, args.all]):
        args.all = True
    
    spark = SparkSession.builder \
        .appName("DataReporting") \
        .master("local[*]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.shuffle.partitions", "8") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    
    print("\n" + "="*80)
    print("DATA REPORTING AND STATISTICS")
    print("="*80)
    
    if args.table:
        column_details(spark, args.table)
    elif args.stats or args.all:
        table_statistics(spark)
    
    if args.fk or args.all:
        foreign_key_report(spark)
    
    if args.quality or args.all:
        data_quality_report(spark)
    
    spark.stop()
    print()

if __name__ == "__main__":
    main()
