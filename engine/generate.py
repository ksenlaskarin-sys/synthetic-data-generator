#!/usr/bin/env python3
"""
Synthetic Data Generator
Generates 26 tables with realistic data using OpenAI LLM
"""

import json
import os
import sys
from pyspark.sql import SparkSession
from engine.table_generator import generate_table, initialize_realistic_data

def main():
    # Configuration
    os.environ["PYSPARK_PIN_THREAD"] = "true"
    use_openai = os.getenv("USE_OPENAI", "false").lower() == "true"
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    
    # Validate OpenAI setup if needed
    if use_openai and not openai_api_key:
        print("ERROR: USE_OPENAI=true but OPENAI_API_KEY not set")
        print("Set your API key: export OPENAI_API_KEY='your-key-here'")
        return False
    
    # Initialize Spark
    spark = SparkSession.builder \
        .appName("InstakSynthetic") \
        .config("spark.sql.shuffle.partitions", "8") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()
    
    print("\n" + "="*80)
    print("SYNTHETIC DATA GENERATION")
    print("="*80)
    
    if use_openai:
        print(f"\nOpenAI Mode: Enabled")
        print(f"Model: GPT-3.5-turbo")
    else:
        print(f"\nFallback Mode: Using random realistic data")
    
    # Load configuration
    with open("configs/schema_config.json") as f:
        config = json.load(f)
    
    # Get output format from config (default: csv)
    output_format = config.get("output_format", "csv").lower()
    if output_format not in ["csv", "parquet", "json"]:
        print(f"ERROR: Invalid output_format: {output_format}. Supported: csv, parquet, json")
        return False
    
    # Initialize realistic data
    try:
        if use_openai:
            success = initialize_realistic_data(use_llm=True)
            if success:
                print("[OK] Initialized realistic data from OpenAI")
        else:
            initialize_realistic_data(use_llm=False)
            print("[OK] Initialized fallback data")
    except ImportError:
        print("[WARN] OpenAI support not available. Using fallback data.")
        initialize_realistic_data(use_llm=False)
    except Exception as e:
        print(f"[WARN] OpenAI initialization failed: {e}. Using fallback data.")
        initialize_realistic_data(use_llm=False)
    
    # Generate tables
    print(f"\nGenerating {len(config['tables'])} tables...")
    generated = {}
    execution_order = list(config["tables"].keys())
    
    for i, table in enumerate(execution_order, 1):
        print(f"  [{i:2d}/{len(execution_order)}] {table}...", end=" ", flush=True)
        try:
            df = generate_table(spark, config["tables"][table], generated)
            generated[table] = df
            
            row_count = df.count()
            output_path = f"output/{output_format}/{table}"
            
            if output_format == "csv":
                df.coalesce(1).write.mode("overwrite").option("header", "true").csv(output_path)
                # Clean up Spark metadata files for CSV
                import subprocess
                subprocess.run(f"find {output_path} -type f ! -name '*.csv' -delete 2>/dev/null", 
                             shell=True, capture_output=True)
            elif output_format == "parquet":
                df.coalesce(1).write.mode("overwrite").parquet(output_path)
            elif output_format == "json":
                df.coalesce(1).write.mode("overwrite").json(output_path)
                
            print(f"[OK] ({row_count:,} rows)")
        except Exception as e:
            print(f"[ERROR] {e}")
            spark.stop()
            return False
    
    spark.stop()
    
    print("\n" + "="*80)
    print("GENERATION COMPLETE")
    print("="*80)
    print(f"\nOutput directory: output/{output_format}/")
    print(f"Tables generated: {len(generated)}")
    print(f"Output format: {output_format.upper()}")
    print(f"\nNext: Run validation with: python validate.py\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
