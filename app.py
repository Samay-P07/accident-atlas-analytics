from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = FastAPI(
    title="Data Management Project Framework",
    description="Heterogeneous Source Processing Environment - Technical University of Chemnitz",
    version="1.7"
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

class RegionResponse(BaseModel):
    ags: str
    name: str
    level: str

class AccidentMetricsResponse(BaseModel):
    scope: Dict[str, Any]
    count: int
    provenance: str
    data_available_from_year_onwards: Optional[int] = None

class EarliestYearResponse(BaseModel):
    earliest_record_detected: Optional[int]

class BicycleAccidentResponse(BaseModel):
    region: str
    year: int
    accident_type: str
    count: int
    provenance: str

class FatalDistrictsResponse(BaseModel):
    rank: int
    district_code: str
    fatal_accidents_2024: int

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def system_root_frontend():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>German Accident Data Analytics Hub</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        fontFamily: { sans: ['Inter', 'sans-serif'], mono: ['Fira Code', 'monospace'] },
                        colors: { spaceDark: '#090d16', panelGlass: '#111928', neonCyan: '#0ea5e9', neonEmerald: '#10b981' }
                    }
                }
            }
        </script>
        <script>
            async function triggerQuery(endpoint, questionTitle) {
                const modal = document.getElementById("result-modal");
                const modalTitle = document.getElementById("modal-question-title");
                const modalBody = document.getElementById("modal-json-output");
                
                modalTitle.innerText = questionTitle;
                modalBody.innerHTML = '// Fetching statistics from local database instance...';
                modal.classList.remove("hidden");
                modal.classList.add("flex");
                
                try {
                    const response = await fetch(endpoint);
                    const data = await response.json();
                    modalBody.innerHTML = JSON.stringify(data, null, 4);
                } catch (error) {
                    modalBody.innerHTML = '// Query execution fault:\\n' + error;
                }
            }
            
            function closeModal() {
                const modal = document.getElementById("result-modal");
                modal.classList.remove("flex");
                modal.classList.add("hidden");
            }
        </script>
    </head>
    <body class="bg-spaceDark text-slate-300 min-h-screen flex flex-col font-sans relative overflow-x-hidden selection:bg-neonCyan/30">
        <div class="absolute top-0 left-1/3 w-96 h-96 bg-neonCyan/10 rounded-full blur-[120px] pointer-events-none"></div>
        <div class="absolute bottom-10 right-1/4 w-80 h-80 bg-purple-600/10 rounded-full blur-[130px] pointer-events-none"></div>

        <header class="border-b border-slate-800/80 bg-panelGlass/50 backdrop-blur-xl sticky top-0 z-40">
            <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
                <div class="flex items-center space-x-3">
                    <div class="h-9 w-9 rounded-lg bg-gradient-to-tr from-neonCyan to-blue-600 flex items-center justify-center text-white text-lg shadow-md shadow-neonCyan/20">📊</div>
                    <div><span class="font-bold text-base text-white tracking-tight">Accident Atlas Analytics</span></div>
                </div>
                <div class="flex items-center space-x-4 bg-slate-950 px-4 py-2 rounded-xl border border-slate-800 text-[11px] font-mono">
                    <span class="h-1.5 w-1.5 rounded-full bg-neonEmerald shadow-[0_0_8px_#10b981]"></span>
                    <a href="/docs" target="_blank" class="text-neonCyan hover:underline font-bold">👉 OPEN SWAGGER DOCS</a>
                </div>
            </div>
        </header>

        <main class="flex-grow max-w-7xl mx-auto px-6 py-8 w-full flex flex-col justify-between">
            <div class="bg-panelGlass/40 backdrop-blur-md p-6 rounded-2xl border border-slate-800 shadow-xl mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <span class="text-[10px] font-mono text-neonCyan font-bold tracking-widest uppercase bg-sky-950/40 px-2 py-0.5 rounded border border-sky-800/30">Project Portal</span>
                    <h1 class="text-xl font-extrabold text-white tracking-tight mt-1">Open Data Integration for Traffic Safety</h1>
                </div>
                <div class="text-left sm:text-right text-xs text-slate-400 font-mono border-l-2 sm:border-l-0 sm:border-r-2 border-slate-700 pl-3 sm:pl-0 sm:pr-3">
                    <div>Student: <span class="text-slate-200 font-semibold">Samay Patel</span></div>
                    <div>Course: <span class="text-slate-300">Datenbanken und Web-Techniken</span></div>
                    <div>University: <span class="text-slate-300">TU Chemnitz</span></div>
                </div>
            </div>

            <div class="flex-grow">
                <h2 class="text-xs font-bold uppercase tracking-widest text-slate-500 mb-4">Verification Queries</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                    
                    <div class="bg-panelGlass/20 border border-slate-800/80 p-5 rounded-xl flex flex-col justify-between hover:border-slate-700 transition group">
                        <div>
                            <span class="text-[10px] font-mono text-slate-500 uppercase tracking-wider block mb-2">Scenario 01</span>
                            <h3 class="text-sm font-bold text-slate-200 group-hover:text-white transition">What is the earliest accident year available in the engine?</h3>
                        </div>
                        <button onclick="triggerQuery('/metadata/earliest-year', '1. Earliest System Accident Year')" class="mt-5 w-full bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-slate-300 hover:text-white py-2 rounded-lg text-xs font-bold transition">Execute Query</button>
                    </div>

                    <div class="bg-panelGlass/20 border border-slate-800/80 p-5 rounded-xl flex flex-col justify-between hover:border-slate-700 transition group">
                        <div>
                            <span class="text-[10px] font-mono text-neonEmerald uppercase tracking-wider block mb-2">Scenario 02</span>
                            <h3 class="text-sm font-bold text-slate-200 group-hover:text-white transition">Total accidents involving personal injuries in Saxony during 2023?</h3>
                        </div>
                        <button onclick="triggerQuery('/aggregates/accidents?ags=14&year=2023', '2. Accidents in Saxony (2023)')" class="mt-5 w-full bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-slate-300 hover:text-white py-2 rounded-lg text-xs font-bold transition">Execute Query</button>
                    </div>

                    <div class="bg-panelGlass/20 border border-slate-800/80 p-5 rounded-xl flex flex-col justify-between hover:border-slate-700 transition group">
                        <div>
                            <span class="text-[10px] font-mono text-amber-400 uppercase tracking-wider block mb-2">Scenario 03</span>
                            <h3 class="text-sm font-bold text-slate-200 group-hover:text-white transition">Pedestrian-specific structural collisions recorded in Berlin (2023)?</h3>
                        </div>
                        <button onclick="triggerQuery('/aggregates/accidents?ags=11&year=2023&pedestrian_only=true', '3. Pedestrian Collisions in Berlin (2023)')" class="mt-5 w-full bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-slate-300 hover:text-white py-2 rounded-lg text-xs font-bold transition">Execute Query</button>
                    </div>

                    <div class="bg-panelGlass/20 border border-slate-800/80 p-5 rounded-xl flex flex-col justify-between hover:border-slate-700 transition group">
                        <div>
                            <span class="text-[10px] font-mono text-indigo-400 uppercase tracking-wider block mb-2">Scenario 04</span>
                            <h3 class="text-sm font-bold text-slate-200 group-hover:text-white transition">From which timeline year onwards is data available for North Rhine-Westphalia?</h3>
                        </div>
                        <button onclick="triggerQuery('/aggregates/accidents?ags=05', '4. NRW Ingestion Start Boundary')" class="mt-5 w-full bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-slate-300 hover:text-white py-2 rounded-lg text-xs font-bold transition">Execute Query</button>
                    </div>

                    <div class="bg-panelGlass/20 border border-slate-800/80 p-5 rounded-xl flex flex-col justify-between hover:border-slate-700 transition group">
                        <div>
                            <span class="text-[10px] font-mono text-rose-400 uppercase tracking-wider block mb-2">Scenario 05</span>
                            <h3 class="text-sm font-bold text-slate-200 group-hover:text-white transition">From which timeline year onwards is data available for Mecklenburg-Vorpommern?</h3>
                        </div>
                        <button onclick="triggerQuery('/aggregates/accidents?ags=13', '5. Mecklenburg-Vorpommern Boundary')" class="mt-5 w-full bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-slate-300 hover:text-white py-2 rounded-lg text-xs font-bold transition">Execute Query</button>
                    </div>

                    <div class="bg-panelGlass/20 border border-slate-800/80 p-5 rounded-xl flex flex-col justify-between hover:border-slate-700 transition group">
                        <div>
                            <span class="text-[10px] font-mono text-neonEmerald uppercase tracking-wider block mb-2">Bonus Scenario A</span>
                            <h3 class="text-sm font-bold text-slate-200 group-hover:text-white transition">How many bicycle accidents occurred in Dresden in 2024?</h3>
                        </div>
                        <button onclick="triggerQuery('/custom/dresden-bicycle-2024', 'Bonus A: Bicycle Accidents in Dresden (2024)')" class="mt-5 w-full bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-slate-300 hover:text-white py-2 rounded-lg text-xs font-bold transition">Execute Query</button>
                    </div>

                    <div class="bg-panelGlass/20 border border-slate-800/80 p-5 rounded-xl flex flex-col justify-between hover:border-slate-700 transition group">
                        <div>
                            <span class="text-[10px] font-mono text-neonCyan uppercase tracking-wider block mb-2">Bonus Scenario B</span>
                            <h3 class="text-sm font-bold text-slate-200 group-hover:text-white transition">Which 5 districts recorded the highest number of fatal accidents in 2024?</h3>
                        </div>
                        <button onclick="triggerQuery('/custom/top-fatal-districts-2024', 'Bonus B: Top 5 Fatal Accident Districts (2024)')" class="mt-5 w-full bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-slate-300 hover:text-white py-2 rounded-lg text-xs font-bold transition">Execute Query</button>
                    </div>

                </div>
            </div>
        </main>

        <div id="result-modal" class="hidden fixed inset-0 z-50 bg-spaceDark/80 backdrop-blur-sm items-center justify-center p-4 transition-all">
            <div class="bg-panelGlass border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden transform scale-100 transition-all">
                <div class="flex items-center justify-between border-b border-slate-800/60 px-6 py-4 bg-slate-900/40">
                    <div class="flex items-center space-x-2">
                        <span class="h-2 w-2 rounded-full bg-neonCyan animate-ping"></span>
                        <h2 id="modal-question-title" class="text-sm font-bold text-white tracking-tight">Database Query Result</h2>
                    </div>
                    <button onclick="closeModal()" class="text-slate-500 hover:text-white transition font-mono text-base">&times;</button>
                </div>
                <div class="p-6 bg-slate-950/80 font-mono text-xs overflow-y-auto flex-grow leading-relaxed text-emerald-400 whitespace-pre-wrap">
                    <pre id="modal-json-output"></pre>
                </div>
                <div class="border-t border-slate-800/60 px-6 py-3 flex justify-end bg-slate-950/40">
                    <button onclick="closeModal()" class="bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold px-4 py-1.5 rounded-lg border border-slate-700 transition">Close</button>
                </div>
            </div>
        </div>

        <footer class="border-t border-slate-900 bg-slate-950/40 py-4 text-center text-[11px] text-slate-600 font-mono">
            Data Source: Statistisches Bundesamt (Destatis) / Unfallatlas | Academic Term Project Submission
        </footer>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/custom/dresden-bicycle-2024", response_model=BicycleAccidentResponse, tags=["Grader Bonus Queries"])
def get_dresden_bicycle_accidents():
    conn = resolve_backend_stream()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as bicycle_accidents FROM accidents WHERE year = 2024 AND ags LIKE '14612%' AND ist_rad = 1;")
    res = cursor.fetchone()
    cursor.close()
    conn.close()
    return {
        "region": "Dresden (Stadt)",
        "year": 2024,
        "accident_type": "Bicycle Accidents (IstRad = 1)",
        "count": res["bicycle_accidents"] if res else 0,
        "provenance": "Data license Germany – attribution – version 2.0"
    }

@app.get("/custom/top-fatal-districts-2024", response_model=List[FatalDistrictsResponse], tags=["Grader Bonus Queries"])
def get_top_fatal_districts_2024():
    conn = resolve_backend_stream()
    cursor = conn.cursor()
    query = """
        SELECT SUBSTRING(ags FROM 1 FOR 5) as dist_code, COUNT(*) as fatal_count
        FROM accidents 
        WHERE year = 2024 AND category = 1
        GROUP BY dist_code
        ORDER BY fatal_count DESC
        LIMIT 5;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    result = []
    for i, row in enumerate(rows):
        result.append({
            "rank": i + 1,
            "district_code": row.get("dist_code") or row.get("district_code") or "Unknown",
            "fatal_accidents_2024": row["fatal_count"]
        })
    return result

@app.get("/regions", response_model=List[RegionResponse], tags=["Metadata Infrastructure"])
def extract_regional_layer(level: Optional[str] = Query(None)):
    conn = resolve_backend_stream()
    cursor = conn.cursor()
    if level:
        cursor.execute("SELECT ags, name, level FROM regions WHERE level = %s;", (level,))
    else:
        cursor.execute("SELECT ags, name, level FROM regions;")
    payload = cursor.fetchall()
    cursor.close()
    conn.close()
    return payload

@app.get("/aggregates/accidents", response_model=AccidentMetricsResponse, tags=["Core Examiner Scenarios"])
def retrieve_accident_metrics(
    ags: Optional[str] = Query(None), 
    year: Optional[int] = Query(None), 
    pedestrian_only: bool = Query(False)
):
    conn = resolve_backend_stream()
    cursor = conn.cursor()
    
    if ags and len(ags) not in [2, 3, 5, 8]:
        raise HTTPException(status_code=400, detail="Invalid AGS format parameter length.")

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
    
    try:
        cursor.execute("SELECT license_type FROM provenance WHERE dataset_name LIKE '%Accident%' LIMIT 1;")
        prov = cursor.fetchone()
        prov_str = prov['license_type'] if (prov and prov.get('license_type')) else "Data license Germany – attribution – version 2.0"
    except Exception:
        prov_str = "Data license Germany – attribution – version 2.0"
    
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

@app.get("/metadata/earliest-year", response_model=EarliestYearResponse, tags=["Metadata Infrastructure"])
def fetch_system_bounds():
    conn = resolve_backend_stream()
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(year) as timeline_start FROM accidents;")
    boundary = cursor.fetchone()
    cursor.close()
    conn.close()
    return {"earliest_record_detected": boundary["timeline_start"] if boundary else None}