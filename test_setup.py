import sys

print("--- DEEP STEP 1: ENVIRONMENT CHECK ---")
print(f"Python Version: {sys.version}\n")

try:
    import pandas as pd
    print("[SUCCESS] Pandas library successfully import thai gayi che!")
    print(f"Pandas Version: {pd.__version__}\n")
except ImportError:
    print("[ERROR] Pandas install nathi thairu. Fari pip install karo.\n")

try:
    import psycopg2
    print("[SUCCESS] Psycopg2 (PostgreSQL Connector) successfully import thai gayi che!")
except ImportError:
    print("[ERROR] Psycopg2 install nathi thairu. Fari pip install karo.\n")