from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = FastAPI(
    title="Data Management Project Framework",
    description="Dynamic Open Data Harmonization Engine - Technical University of Chemnitz",
    version="2.0"
)

DB_CONFIG = {
    "dbname": "dbw_project",
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD", "Samay@2003"),
    "host": "127.0.0.1",
    "port": "5432"
}

def resolve_backend_stream():
    try:
        return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connectivity runtime failure: {e}")

class AccidentRateResponse(BaseModel):
    region_name: str
    ags: str
    year: int
    accident_count: int
    population: int
    rate_per_100k_inhabitants: float
    provenance: str

# Existing response validation models
class RegionResponse(BaseModel):
    ags: str
    name: str
    level: str
    population: int

class AccidentMetricsResponse(BaseModel):
    scope: Dict[str, Any]
    count: int
    provenance: str
    data_available_from_year_onwards: Optional[int] = None

# ---- NEW MULTI-DATASET NORMALIZATION ENDPOINT (SOLVES SCENARIO 2) ----
@app.get("/aggregates/accident-rate-per-100k", response_model=AccidentRateResponse, tags=["Mandatory Multi-Dataset Scenarios"])
def get_accident_rate_per_capita(ags: str = Query(..., description="Target 5 or 8-digit AGS code"), year: int = Query(..., description="Target calendar year")):
    conn = resolve_backend_stream()
    cursor = conn.cursor()
    
    # 1. Validate if region exists and fetch metadata
    cursor.execute("SELECT name, population FROM regions WHERE ags LIKE %s LIMIT 1;", (f"{ags}%",))
    region = cursor.fetchone()
    
    if not region:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail=f"Target regional key indicator code '{ags}' not registered in engine infrastructure.")
        
    if not region['population'] or region['population'] == 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail=f"Regional matrix exists but baseline population metrics are zero or uninitialized.")

    # 2. Count total accidents for that region and year
    cursor.execute("SELECT COUNT(*) as total_accidents FROM accidents WHERE year = %s AND ags LIKE %s;", (year, f"{ags}%"))
    acc_data = cursor.fetchone()
    
    # 3. Fetch Provenance from dynamic table
    cursor.execute("SELECT license_type FROM provenance WHERE dataset_name LIKE '%GENESIS%' LIMIT 1;")
    prov = cursor.fetchone()
    prov_str = prov['license_type'] if prov else "Data license Germany – attribution – version 2.0"
    
    cursor.close()
    conn.close()
    
    total_acc = acc_data['total_accidents'] if acc_data else 0
    pop = region['population']
    calculated_rate = round((total_acc / pop) * 100000, 2)
    
    return {
        "region_name": region['name'],
        "ags": ags,
        "year": year,
        "accident_count": total_acc,
        "population": pop,
        "rate_per_100k_inhabitants": calculated_rate,
        "provenance": prov_str
    }

# ---- CORE COMPLIANCE AND METADATA ROUTES WITH EXTENDED ERROR HANDLING ----
@app.get("/aggregates/accidents", response_model=AccidentMetricsResponse, tags=["Core Examiner Scenarios"])
def retrieve_accident_metrics(ags: Optional[str] = Query(None), year: Optional[int] = Query(None), pedestrian_only: bool = Query(False)):
    conn = resolve_backend_stream()
    cursor = conn.cursor()
    
    # Input Validation Guard
    if ags and len(ags) not in [2, 3, 5, 8]:
        raise HTTPException(status_code=400, detail="Invalid AGS format parameter length. Must represent State (2), District (5) or Municipality (8).")

    detected_start_year = None
    if ags and not year:
        cursor.execute("SELECT MIN(year) as start_yr FROM accidents WHERE ags LIKE %s;", (f"{ags}%",))
        db_res = cursor.fetchone()
        if db_res and db_res.get('start_yr') is not None:
            detected_start_year = db_res['start_yr']

    statement = "SELECT COUNT(*) as incident_metrics FROM accidents WHERE 1=1"
    arguments = []
    
    if year:
        statement += " AND year = %s"
        arguments.append(year)
    if ags:
        statement += " AND ags LIKE %s"
        arguments.append(f"{ags}%")
    if pedestrian_only:
        statement += " AND ist_fuss = 1"
        
    cursor.execute(statement, tuple(arguments))
    dataset = cursor.fetchone()
    
    cursor.execute("SELECT license_type FROM provenance WHERE dataset_name LIKE '%Accident%' LIMIT 1;")
    prov = cursor.fetchone()
    prov_str = prov['license_type'] if prov else "Data license Germany – attribution – version 2.0"
    
    cursor.close()
    conn.close()
    
    response_payload = {
        "scope": {"prefix": ags if ags else "Federal Border Structure", "target_period": year if year else "All Ingested Logs"},
        "count": dataset["incident_metrics"] if dataset else 0,
        "provenance": prov_str
    }
    if detected_start_year:
        response_payload["data_available_from_year_onwards"] = detected_start_year
        
    return response_payload

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def system_root_frontend():
    # Keep the frontend layout HTML same as before, but it will now seamlessly hit the modified APIs.
    # Just return the identical dashboard template string you have in app_3.py
    pass