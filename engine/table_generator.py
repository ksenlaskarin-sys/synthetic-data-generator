from pyspark.sql import functions as F
from pyspark.sql import Window
import json
import os
import re
from typing import List, Dict, Optional

# OpenAI client (imported when needed)
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# Global data pool for realistic values
REALISTIC_DATA = {
    "user_names": [],
    "product_names": {},  # by category
    "brands": {},  # by category
    "descriptions": {},  # by category
    "addresses": {},  # by city
    "warehouse_names": {},  # by city
    "delivery_partner_names": [],
}

class OpenAIDataGenerator:
    """Generate realistic data using OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI data generator"""
        if not HAS_OPENAI:
            raise ImportError("OpenAI package required. Install: pip install openai")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-3.5-turbo"
    
    def _call_openai(self, prompt: str) -> str:
        """Make a call to OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data generation expert. Generate realistic, diverse synthetic data for e-commerce systems. Always return data as valid JSON unless otherwise specified. Keep responses concise."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠ OpenAI API error: {e}")
            raise
    
    def generate_user_names(self, count: int = 500) -> List[str]:
        """Generate realistic user names"""
        prompt = f"""Generate {count} realistic Indian and international names for e-commerce users.
Return as a JSON array with exactly {count} names. Format: {{"names": ["name1", "name2", ...]}}
Include a mix of Indian names (Hindi, Tamil, Telugu, Marathi, etc) and Western names.
Keep names between 2-4 words."""
        
        response = self._call_openai(prompt)
        try:
            data = json.loads(response)
            return data.get("names", [])[:count]
        except:
            return self._extract_list_from_response(response, count)
    
    def generate_product_names(self, category: str, count: int = 100) -> List[str]:
        """Generate realistic product names for a category"""
        prompt = f"""Generate {count} realistic product names for the '{category}' category in an e-commerce store.
Make them diverse and realistic. Return as JSON: {{"products": ["product1", "product2", ...]}}"""
        
        response = self._call_openai(prompt)
        try:
            data = json.loads(response)
            return data.get("products", [])[:count]
        except:
            return self._extract_list_from_response(response, count)
    
    def generate_brand_names(self, category: str, count: int = 50) -> List[str]:
        """Generate realistic brand names for a category"""
        prompt = f"""Generate {count} realistic brand names for the '{category}' product category.
Mix real-world sounding brands with creative names. Return as JSON: {{"brands": ["brand1", "brand2", ...]}}"""
        
        response = self._call_openai(prompt)
        try:
            data = json.loads(response)
            return data.get("brands", [])[:count]
        except:
            return self._extract_list_from_response(response, count)
    
    def generate_product_descriptions(self, category: str, count: int = 50) -> List[str]:
        """Generate realistic product descriptions"""
        prompt = f"""Generate {count} product descriptions for '{category}' products.
Each 1-2 sentences, highlighting features. Return as JSON: {{"descriptions": ["desc1", "desc2", ...]}}"""
        
        response = self._call_openai(prompt)
        try:
            data = json.loads(response)
            return data.get("descriptions", [])[:count]
        except:
            return self._extract_list_from_response(response, count)
    
    def generate_addresses(self, city: str, count: int = 200) -> List[str]:
        """Generate realistic addresses for a city"""
        prompt = f"""Generate {count} realistic residential addresses in {city}, India.
Include street names, building numbers, and realistic locality names.
Return as JSON: {{"addresses": ["address1", "address2", ...]}}"""
        
        response = self._call_openai(prompt)
        try:
            data = json.loads(response)
            return data.get("addresses", [])[:count]
        except:
            return self._extract_list_from_response(response, count)
    
    def generate_warehouse_names(self, city: str, count: int = 5) -> List[str]:
        """Generate realistic warehouse names for a city"""
        prompt = f"""Generate {count} realistic warehouse/fulfillment center names for {city}, India.
Include location references and professional naming. Return as JSON: {{"warehouses": ["name1", "name2", ...]}}"""
        
        response = self._call_openai(prompt)
        try:
            data = json.loads(response)
            return data.get("warehouses", [])[:count]
        except:
            return self._extract_list_from_response(response, count)
    
    def generate_delivery_partner_names(self, count: int = 200) -> List[str]:
        """Generate realistic delivery partner names"""
        prompt = f"""Generate {count} realistic delivery/logistics partner names.
Mix of individual and company names. Return as JSON: {{"partners": ["partner1", "partner2", ...]}}"""
        
        response = self._call_openai(prompt)
        try:
            data = json.loads(response)
            return data.get("partners", [])[:count]
        except:
            return self._extract_list_from_response(response, count)
    
    def _extract_list_from_response(self, response: str, expected_count: int) -> List[str]:
        """Extract list items from a text response if JSON parsing fails"""
        items = re.findall(r'["\']([^"\']+)["\']', response)
        if items:
            return items[:expected_count]
        items = re.findall(r'^\s*\d+\.\s*(.+)$', response, re.MULTILINE)
        if items:
            return items[:expected_count]
        return []

def initialize_realistic_data(use_llm=False):
    """Initialize realistic data pool. If use_llm=True, fetches from OpenAI."""
    global REALISTIC_DATA
    
    if use_llm:
        print("Fetching realistic data from OpenAI...")
        try:
            llm_gen = OpenAIDataGenerator()
            
            # Generate user names
            REALISTIC_DATA["user_names"] = llm_gen.generate_user_names(500)
            
            # Generate categories and related data
            categories = ["Electronics", "Fashion", "Home", "Sports", "Books", 
                         "Food", "Health", "Toys", "Beauty", "Garden"]
            
            for cat in categories:
                REALISTIC_DATA["product_names"][cat] = llm_gen.generate_product_names(cat, 50)
                REALISTIC_DATA["brands"][cat] = llm_gen.generate_brand_names(cat, 25)
                REALISTIC_DATA["descriptions"][cat] = llm_gen.generate_product_descriptions(cat, 25)
            
            # Generate city data
            cities = ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai"]
            for city in cities:
                REALISTIC_DATA["addresses"][city] = llm_gen.generate_addresses(city, 100)
                REALISTIC_DATA["warehouse_names"][city] = llm_gen.generate_warehouse_names(city, 3)
            
            # Generate partner names
            REALISTIC_DATA["delivery_partner_names"] = llm_gen.generate_delivery_partner_names(100)
            
            print("✓ Realistic data loaded from OpenAI")
            return True
        except Exception as e:
            print(f"⚠ Could not load OpenAI data: {e}. Using fallback data.")
            _initialize_fallback_data()
            return False
    else:
        _initialize_fallback_data()
        return False

def _initialize_fallback_data():
    """Initialize with fallback/dummy data when LLM is not available"""
    global REALISTIC_DATA
    
    REALISTIC_DATA["user_names"] = [
        "Rajesh Kumar", "Priya Sharma", "Amit Patel", "Neha Singh", "Vikram Reddy",
        "Ananya Gupta", "Rohan Verma", "Deepika Malhotra", "Sanjay Iyer", "Pooja Desai",
        "Arun Kumar", "Sneha Nair", "Akshay Joshi", "Divya Pillai", "Nikhil Bhat",
        "Isha Kapoor", "Varun Singh", "Kavya Menon", "Adil Khan", "Sana Ahmed"
    ] + [f"User_{i}" for i in range(480)]
    
    categories = ["Electronics", "Fashion", "Home", "Sports", "Books", "Food", "Health", "Toys", "Beauty", "Garden"]
    for cat in categories:
        REALISTIC_DATA["product_names"][cat] = [f"{cat}_Product_{i}" for i in range(100)]
        REALISTIC_DATA["brands"][cat] = [f"Brand_{i}" for i in range(50)]
        REALISTIC_DATA["descriptions"][cat] = [f"Great {cat} product with excellent quality" for i in range(50)]
    
    cities = ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai"]
    for city in cities:
        REALISTIC_DATA["addresses"][city] = [f"{i} {city} Street, {city}" for i in range(200)]
        REALISTIC_DATA["warehouse_names"][city] = [f"Warehouse_{city}_{i}" for i in range(5)]
    
    REALISTIC_DATA["delivery_partner_names"] = [f"Delivery_Partner_{i}" for i in range(200)]

def generate_table(spark, table_spec, generated_tables, realistic_pool=None):
    df = spark.range(table_spec["row_count"]).drop("id")

    # Foreign keys - select actual parent IDs to ensure 100% validity
    for fk_col, fk in table_spec.get("foreign_keys", {}).items():
        parent_df = generated_tables[fk["ref_table"]]
        parent_pk_col = fk["ref_column"]
        
        # Get all valid parent PKs as list
        parent_pks = parent_df.select(parent_pk_col).rdd.map(lambda r: r[0]).collect()
        
        if parent_pks:  # Only if parent has records
            import random
            # Create column with random selection from actual parent PKs
            def select_random_pk(x):
                return random.choice(parent_pks)
            
            from pyspark.sql.types import LongType
            random_pk_udf = F.udf(select_random_pk, LongType())
            df = df.withColumn(fk_col, random_pk_udf(F.monotonically_increasing_id()))

    # Columns
    for col_name, meta in table_spec["columns"].items():
        t = meta["type"]

        if t == "pk":
            df = df.withColumn(col_name, F.monotonically_increasing_id())
        elif t == "string":
            # Use realistic data if available
            if col_name == "name" and "user_names" in table_spec.get("_data_sources", {}):
                data_source = table_spec["_data_sources"]["name"]
                if data_source in REALISTIC_DATA and REALISTIC_DATA[data_source]:
                    values = REALISTIC_DATA[data_source]
                    # Create array of values and select randomly
                    df = df.withColumn(col_name, F.element_at(F.array(*[F.lit(v) for v in values]), (F.rand() * F.lit(len(values))).cast("int") + 1))
            elif col_name == "brand" and "brand" in table_spec.get("_data_sources", {}):
                # Get brands from category
                try:
                    df = df.withColumn(col_name, F.lit("TBD"))  # Placeholder
                except:
                    df = df.withColumn(col_name, F.concat(F.lit(col_name+"_"), F.monotonically_increasing_id()))
            else:
                df = df.withColumn(col_name, F.concat(F.lit(col_name+"_"), F.monotonically_increasing_id()))
        elif t == "email":
            df = df.withColumn(col_name, F.concat(F.lit("user_"), F.monotonically_increasing_id(), F.lit("@example.com")))
        elif t == "phone":
            df = df.withColumn(col_name, F.format_string("9%09d", F.monotonically_increasing_id()))
        elif t == "enum":
            values = meta["values"]
            df = df.withColumn(col_name, F.expr(f"element_at(array({','.join(map(repr,values))}), int(rand()*{len(values)})+1)"))
        elif t == "decimal":
            df = df.withColumn(col_name, F.round(F.rand()*(meta["max"]-meta["min"])+meta["min"],2))
        elif t == "boolean":
            df = df.withColumn(col_name, F.rand() < meta.get("probability",0.5))
        elif t == "timestamp":
            df = df.withColumn(col_name, F.current_timestamp() - F.expr(f"INTERVAL '{meta['range_days']}' DAY"))
        elif t == "int":
            min_val = meta.get("min", 0)
            max_val = meta.get("max", 1000)
            # Use F.expr to avoid type issues with newer PySpark
            df = df.withColumn(col_name, F.expr(f"cast(rand() * {max_val - min_val} + {min_val} as int)"))

    return df
