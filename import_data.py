import os
import zipfile
import pandas as pd
import psycopg2

RAW_DATA_DIR = "./raw_data"
EXTRACT_DIR = "./extracted_data"

# Standard PostgreSQL server authorization layout
DB_CONFIG = {
    "dbname": "dbw_project",
    "user": "postgres",
    "password": "Samay@2003",
    "host": "127.0.0.1",
    "port": "5432"
}

if not os.path.exists(EXTRACT_DIR):
    os.makedirs(EXTRACT_DIR)

def extract_all_zips():
    print("\n--- STEP 1: Processing Source Archives ---")
    if not os.path.exists(RAW_DATA_DIR):
        print(f"[ERROR] Source directory {RAW_DATA_DIR} not found.")
        return
    for file in os.listdir(RAW_DATA_DIR):
        if file.endswith(".zip"):
            zip_path = os.path.join(RAW_DATA_DIR, file)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(EXTRACT_DIR)
    print("[SUCCESS] Extraction completed.")

def create_tables():
    print("\n--- STEP 2: Database Schema Initialization ---")
    query_regions = """
    CREATE TABLE IF NOT EXISTS regions (
        ags VARCHAR(8) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        level VARCHAR(50) NOT NULL,
        population INT DEFAULT 0
    );
    """
    query_accidents = """
    CREATE TABLE IF NOT EXISTS accidents (
        accident_id SERIAL PRIMARY KEY,
        year INT NOT NULL,
        month INT NOT NULL,
        hour INT NOT NULL,
        weekday INT NOT NULL,
        category INT NOT NULL,
        light INT,
        ist_pkw INT DEFAULT 0,
        ist_rad INT DEFAULT 0,
        ist_fuss INT DEFAULT 0,
        lon NUMERIC,
        lat NUMERIC,
        ags VARCHAR(8) REFERENCES regions(ags)
    );
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(query_regions)
    cursor.execute(query_accidents)
    conn.commit()
    cursor.close()
    conn.close()
    print("[SUCCESS] Relational structures initialized.")

def load_regional_infrastructure():
    print("\n--- STEP 3: Ingesting Federal Structural Metadata ---")
    # Integrating real open regional dataset mappings matching standard GENESIS hierarchies
    base_data = [
        ("11000000", "Berlin", "state", 3674000),
        ("14000000", "Sachsen", "state", 4058000),
        ("05000000", "Nordrhein-Westfalen", "state", 17924000),
        ("13000000", "Mecklenburg-Vorpommern", "state", 1610000),
        ("14511000", "Chemnitz, Stadt", "district", 244000),
        ("14612000", "Dresden, Stadt", "district", 563000)
    ]
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    for ags, name, level, pop in base_data:
        cursor.execute("""
            INSERT INTO regions (ags, name, level, population)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (ags) DO UPDATE SET population = EXCLUDED.population;
        """, (ags, name, level, pop))
    conn.commit()
    cursor.close()
    conn.close()
    print("[SUCCESS] Regional layers updated.")

def load_accident_data():
    print("\n--- STEP 4: Parsing Unfallatlas Records ---")
    target_dir = EXTRACT_DIR
    if "csv" in os.listdir(EXTRACT_DIR):
        target_dir = os.path.join(EXTRACT_DIR, "csv")
        
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    for file in os.listdir(target_dir):
        if file.endswith(".csv"):
            csv_path = os.path.join(target_dir, file)
            print(f"Reading target file: {file}...")
            df = pd.read_csv(csv_path, delimiter=';', encoding='iso-8859-1')
            df = df.where(pd.notnull(df), None)
            
            count = 0
            for index, row in df.iterrows():
                ul_str = str(int(row['ULAND'])).zfill(2) if row['ULAND'] is not None else "00"
                ur_str = str(int(row['UREGBEZ'])).zfill(1) if row['UREGBEZ'] is not None else "0"
                uk_str = str(int(row['UKREIS'])).zfill(2) if row['UKREIS'] is not None else "00"
                ug_str = str(int(row['UGEMEINDE'])).zfill(3) if row['UGEMEINDE'] is not None else "000"
                
                raw_ags = f"{ul_str}{ur_str}{uk_str}{ug_str}"[:8]
                
                cursor.execute("SELECT 1 FROM regions WHERE ags = %s", (raw_ags,))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO regions (ags, name, level) 
                        VALUES (%s, %s, 'municipality') ON CONFLICT DO NOTHING;
                    """, (raw_ags, f"Region_{raw_ags}"))
                
                lon_val = str(row['XGCSWGS84']).replace(',', '.') if row['XGCSWGS84'] is not None else None
                lat_val = str(row['YGCSWGS84']).replace(',', '.') if row['YGCSWGS84'] is not None else None
                
                cursor.execute("""
                    INSERT INTO accidents (year, month, hour, weekday, category, light, ist_pkw, ist_rad, ist_fuss, lon, lat, ags)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (
                    int(row['UJAHR']), int(row['UMONAT']), int(row['USTUNDE']), int(row['UWOCHENTAG']),
                    int(row['UKATEGORIE']), int(row['ULICHTVERH']) if row['ULICHTVERH'] is not None else None,
                    int(row['IstPKW']) if row['IstPKW'] is not None else 0,
                    int(row['IstRad']) if row['IstRad'] is not None else 0,
                    int(row['IstFuss']) if row['IstFuss'] is not None else 0,
                    lon_val, lat_val, raw_ags
                ))
                count += 1
                
            conn.commit()
            print(f"[SUCCESS] Ingested {count} lines from {file}.")
            
    cursor.close()
    conn.close()

if __name__ == "__main__":
    extract_all_zips()
    create_tables()
    load_regional_infrastructure()
    load_accident_data()