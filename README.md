# 🚦 Accident Atlas Analytics — Heterogeneous Data Processing

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

An end-to-end data engineering pipeline and RESTful web analytics portal developed for the **Datenbanken und Web-Techniken** course at **Chemnitz University of Technology (TU Chemnitz)**.

---

## 🚀 Project Overview

This project integrates official German open-data sources into a unified PostgreSQL schema to perform geospatial and statistical analysis on road traffic accidents. It demonstrates a complete data lifecycle: from raw `.zip` extraction and dynamic ETL mapping to a high-performance **FastAPI** backend serving a responsive **Tailwind CSS** frontend.

### Core Technologies
* **Data Engineering (ETL):** Python, Pandas, Python `zipfile` (Automated extraction & CSV parsing)
* **Database:** PostgreSQL (Relational schema with `psycopg2` driver)
* **Backend API:** FastAPI with Pydantic models for strict data validation
* **Frontend:** Interactive HTML/TailwindCSS UI rendered directly via FastAPI `HTMLResponse`

---

## 🏗️ System Architecture & Data Flow

```text
1. RAW DATA LAYER             2. ETL PIPELINE (import_data.py)       3. DATABASE & API (app.py)
┌──────────────────┐         ┌────────────────────────────────┐      ┌─────────────────────────┐
│ Unfallatlas .zip │ ──EXT──►│ Parse CSVs & Handle Missing    │ ───► │ PostgreSQL (dbw_project)│
│ Destatis .zip    │ ──EXT──►│ Dynamic 5/8-digit AGS Mapping  │ ───► │ 3 Tables: regions,      │
└──────────────────┘         └────────────────────────────────┘      │ accidents, provenance   │
                                                                     └────────────┬────────────┘
                                                                                  │ (SQL Queries)
┌────────────────────────────────────────────────────────┐           ┌────────────▼────────────┐
│ 💻 CLIENT UI (Tailwind CSS Dashboard on localhost:8000)│ ◄──────── │ FastAPI REST Endpoints  │
└────────────────────────────────────────────────────────┘   (JSON)  └─────────────────────────┘


📂 Data Sources & ProvenanceSource DatasetDescriptionLevel of GranularityLicenseUnfallatlas (OpenGeoData)Official German road traffic accident records including vehicle types, light conditions, and exact coordinates.Point-level (GPS)DL-DE/BY-2.0Destatis (GENESIS)Regional administrative boundaries and population metrics dynamically mapped to AGS codes.MunicipalityDL-DE/BY-2.0📊 Verification Queries & Analytical ScenariosThe engine provides real-time API endpoints to answer specific traffic safety scenarios. Below are the 7 core questions implemented in the project alongside their execution routes and expected output metrics:IDAnalytical QuestionAPI Endpoint TriggerResult / Output Format01What is the earliest accident year available in the engine?GET /metadata/earliest-year{"earliest_record_detected": <Year>}02Total accidents involving personal injuries in Saxony during 2023?GET /aggregates/accidents?ags=14&year=2023Aggregate Count & Data Provenance03Pedestrian-specific structural collisions recorded in Berlin (2023)?GET /aggregates/accidents?ags=11&year=2023&pedestrian_only=trueAggregate Count & Data Provenance04From which timeline year onwards is data available for North Rhine-Westphalia?GET /aggregates/accidents?ags=05Start Boundary Year (e.g., 2019)05From which timeline year onwards is data available for Mecklenburg-Vorpommern?GET /aggregates/accidents?ags=13Start Boundary YearBonus AHow many bicycle accidents occurred in Dresden in 2024?GET /custom/dresden-bicycle-2024Exact Count for AGS 14612%Bonus BWhich 5 districts recorded the highest number of fatal accidents in 2024?GET /custom/top-fatal-districts-2024Ranked JSON Array of Top 5 Districts⚙️ Setup & Local Execution1. Database ConfigurationEnsure PostgreSQL is running locally (127.0.0.1:5432). Create a .env file based on the template above.2. Install DependenciesBashpip install -r requirements.txt
3. Run the ETL PipelinePlace your raw .zip datasets in a ./raw_data folder, then execute the data ingestion script:Bashpython import_data.py
4. Launch the Web Portal & APIBashpython -m uvicorn app:app --reload --env-file .env
Dashboard / UI: Navigate to http://127.0.0.1:8000Swagger API Docs: Navigate to http://127.0.0.1:8000/docsAuthor: Samay Patel© 2026 Samay Patel. All Rights Reserved. | TU Chemnitz