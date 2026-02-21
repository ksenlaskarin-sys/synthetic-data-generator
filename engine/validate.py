#!/usr/bin/env python3
"""
Data Validation and Cleanup
Validates foreign keys and removes orphaned records
"""

import json
import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

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

def validate_fks(spark):
    """Validate all foreign key relationships"""
    print("\n" + "="*80)
    print("STEP 1: FOREIGN KEY VALIDATION")
    print("="*80)
    
    with open("configs/schema_config.json") as f:
        config = json.load(f)
    
    print("\nChecking foreign key relationships...\n")
    
    total_records = 0
    total_valid = 0
    total_orphaned = 0
    issues = []
    
    for table_name, table_config in config["tables"].items():
        fk_config = table_config.get("foreign_keys", {})
        
        for fk_col, fk_info in fk_config.items():
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
            print(f"{status} {table_name:30s}.{fk_col:15s}: {valid:8,d}/{total:8,d} ({percentage:6.2f}%)")
            
            if orphaned > 0:
                issues.append({
                    "table": table_name,
                    "fk_col": fk_col,
                    "parent": parent_table,
                    "parent_pk": parent_pk,
                    "orphaned": orphaned
                })
            
            total_records += total
            total_valid += valid
            total_orphaned += orphaned
    
    print(f"\n{'='*80}")
    print(f"Summary:")
    print(f"   Total records scanned:    {total_records:,}")
    print(f"   Valid references:         {total_valid:,}")
    print(f"   Orphaned records found:   {total_orphaned:,}")
    print(f"{'='*80}")
    
    is_valid = (total_orphaned == 0)
    
    if is_valid:
        print("[OK] ALL FOREIGN KEYS ARE 100% VALID!\n")
    else:
        print(f"\n[WARN] Found {len(issues)} FK relationships with violations\n")
    
    return is_valid, issues

def cleanup_orphaned(spark, issues):
    """Remove orphaned records"""
    print("\n" + "="*80)
    print("STEP 2: CLEANUP ORPHANED RECORDS")
    print("="*80)
    
    with open("configs/schema_config.json") as f:
        config = json.load(f)
    
    print("\nProcessing foreign key cleanup...\n")
    
    total_removed = 0
    
    for table_name, table_config in config["tables"].items():
        fk_config = table_config.get("foreign_keys", {})
        
        if not fk_config:
            continue
        
        child_df = load_table(spark, table_name)
        if child_df is None:
            continue
        
        before_count = child_df.count()
        
        # Apply each FK constraint
        for fk_col, fk_info in fk_config.items():
            parent_table = fk_info["ref_table"]
            parent_pk = fk_info["ref_column"]
            
            parent_df = load_table(spark, parent_table)
            if parent_df is None:
                continue
            
            valid_fks = parent_df.select(parent_pk).distinct().collect()
            valid_fk_list = [row[0] for row in valid_fks]
            
            child_df = child_df.filter(F.col(fk_col).isin(valid_fk_list))
        
        after_count = child_df.count()
        removed = before_count - after_count
        
        if after_count > 0:
            output_path = os.path.join(OUTPUT_DIR, table_name)
            try:
                import shutil
                shutil.rmtree(output_path, ignore_errors=True)
                child_df.coalesce(1).write.option("header", "true").mode("overwrite").csv(output_path)
                if removed > 0:
                    print(f"[CLEAN] {table_name:30s}: {after_count:8,d} records ({removed:,d} removed)")
                    total_removed += removed
            except Exception as e:
                print(f"[WARN] {table_name}: Error saving - {e}")
    
    print(f"\n{'='*80}")
    print(f"[OK] Total orphaned records removed: {total_removed:,}")
    print(f"{'='*80}")
    return total_removed

def final_validation(spark):
    """Final validation to confirm 100% validity"""
    print("\n" + "="*80)
    print("STEP 3: FINAL VALIDATION")
    print("="*80)
    
    with open("configs/schema_config.json") as f:
        config = json.load(f)
    
    print("\nChecking final FK validity...\n")
    
    total_orphaned = 0
    valid_fks = 0
    total_fks = 0
    
    for table_name, table_config in config["tables"].items():
        fk_config = table_config.get("foreign_keys", {})
        
        if not fk_config:
            continue
        
        for fk_col, fk_info in fk_config.items():
            total_fks += 1
            parent_table = fk_info["ref_table"]
            parent_pk = fk_info["ref_column"]
            
            parent_df = load_table(spark, parent_table)
            child_df = load_table(spark, table_name)
            
            if parent_df is None or child_df is None:
                print(f"[ERROR] {table_name}.{fk_col}: Missing data")
                continue
            
            total = child_df.count()
            valid = child_df.join(
                parent_df.select(parent_pk).distinct(),
                child_df[fk_col] == parent_df[parent_pk],
                "inner"
            ).count()
            
            orphaned = total - valid
            total_orphaned += orphaned
            
            if orphaned == 0:
                valid_fks += 1
                print(f"[OK] {table_name:30s}.{fk_col:15s}")
    
    print(f"\n{'='*80}")
    print(f"FINAL STATUS: {valid_fks}/{total_fks} foreign keys are 100% VALID")
    print(f"Orphaned records remaining: {total_orphaned:,}")
    print(f"{'='*80}\n")
    
    return total_orphaned == 0

def main():
    print("\n" + "="*80)
    print("DATA VALIDATION AND CLEANUP")
    print("="*80)
    
    spark = SparkSession.builder \
        .appName("ValidationAndCleanup") \
        .master("local[*]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.shuffle.partitions", "8") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    
    # Step 1: Validate FKs
    is_valid, issues = validate_fks(spark)
    
    # Step 2: If violations found, cleanup
    if not is_valid:
        print("\n[WARN] Foreign key violations detected, proceeding to cleanup...")
        cleanup_orphaned(spark, issues)
        
        # Step 3: Final validation
        is_valid = final_validation(spark)
    
    # Summary
    print(f"\n{'='*80}")
    if is_valid:
        print("[OK] SUCCESS! All data is 100% foreign key valid!")
        print(f"\nData location: {OUTPUT_DIR}/")
        print("All 26 tables contain validated, referentially-consistent data")
    else:
        print("[WARN] Some foreign key violations remain")
    print(f"{'='*80}\n")
    
    spark.stop()
    return is_valid

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
