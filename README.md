# VeriSure DigitalQC - Inspection Excellence System

This system implements the exact **VeriSure "Create New Job" form** from your reference screenshots, featuring all symbols, words, and layouts, alongside a **Python ERP Simulator** that fills details, generates ERP jobs, and stores them in JSON.

---

## 📸 1. VeriSure "Create New Job" Form (Frontend)

The form matches the VeriSure interface pixel-for-pixel across all **5 Inspection Types**:

| # | Inspection Type | Dynamic Fields Displayed |
|---|---|---|
| 1 | **Manufacturing QC** | `Lot No`, `Part No`, `Part Description`, `Factory Location` |
| 2 | **Equipment Maintenance** | `Equipment Name`, `Serial No`, `Defect Description`, `Maintenance Type` |
| 3 | **Marine Survey** | `Vessel Name`, `Survey Type`, `Survey No`, `Survey Date End`, `Survey Location`, `Surveyor Name` |
| 4 | **Wind Turbine** | `Turbine ID`, `Turbine Location` |
| 5 | **Material Receipt** | `Supplier Name *` (red highlight validation), `Purchase Order` |

### Common Form Fields (All 5 Types):
- `*Job No` (Placeholder: `Enter job number`)
- `*Job Description` (Placeholder: `Enter job description`)
- `*Inspection Agency` (Dropdown: `Select or type to add Inspection agency`)
- `*Inspection Type` (Dropdown: 5 types)
- `*Inspection Start Date` (Calendar date picker: `Select date`)
- `*Remarks` (Placeholder: `QC Remark`)
- `*Inspection Stage` (Dropdown: `Select Inspection Stage`)
- `*Level` (Dropdown: `Select Level`)
- Button: `Add Job`

---

## 🚀 2. How to Launch the Web Form

You can run the Angular 17 frontend in two ways:

### Option A: Angular 17 Development Server (Recommended for Frontend Dev)
```bash
cd frontend
npm start
```
This runs `ng serve` with live reload at **`http://localhost:4200`** and proxies API calls (`/api`) to the backend.

### Option B: Python FastAPI App (Serves Built Angular 17 SPA on Port 4200)
Run from the `verisure_system` directory:
```bash
python run_app.py
```
This serves the compiled Angular 17 application at **`http://localhost:4200`** and provides backend JSON persistence at `/api/jobs` and `/api/erp-jobs`.

To recompile the Angular frontend after making code changes:
```bash
cd frontend
npm run build
```

---

## 🐍 3. Python ERP Simulator (Fill Details & Generate ERP)

The Python script `erp_simulator/erp_simulator.py` simulates an Enterprise Resource Planning (ERP) system (e.g. SAP S/4HANA QM / Oracle Fusion) generating inspection jobs.

### A. Auto-Generate 5 Jobs (1 for each Inspection Type):
```bash
cd verisure_system/erp_simulator
python erp_simulator.py
```
Outputs:
- Generates 5 realistic industrial jobs.
- Automatically stores them into `verisure_system/data/erp_jobs.json`.

### B. Interactive CLI Mode (Fill details manually in terminal):
```bash
python erp_simulator.py --interactive
```
Walks you through step-by-step prompts to fill details for any of the 5 inspection types.

### C. Generate Specific Type or Custom Batch:
```bash
# Generate 10 jobs:
python erp_simulator.py --generate 10

# Generate specifically for 'Marine Survey':
python erp_simulator.py --generate 3 --type "Marine Survey"
```

---

## 💾 4. Storing Data in JSON

All generated ERP jobs and form submissions are saved in structured JSON:
- **Path**: `verisure_system/data/erp_jobs.json`
- In the Web UI:
  - Fill the form and click **"Add Job"** to submit and save the job into `data/erp_jobs.json`.
  - Click **"⚡ Simulate ERP Data"** to auto-fill the form with realistic mock data for any inspection type.

---

## 🔌 5. API to Push JSON to VeriSure (Prepared for Later)
Per your note: *(“this point we will do later”)*
- The Pydantic schemas in `backend/models.py` and the `push_job_to_verisure()` method in `erp_simulator.py` are already structured and ready to connect whenever you want to activate the external endpoint.
