# VeriSure DigitalQC - Inspection Excellence System

This system implements the **VeriSure "Create New Job" web form** for all 5 inspection types, connecting directly to the **VeriSure Django Server** (`https://127.0.0.1:8000/api/jobs/`), alongside a **Python ERP Simulator** that can generate and push mock jobs directly into the database.

---

## 📸 1. Supported Inspection Types & Dynamic Fields

| # | Inspection Type | Department | Dynamic Fields |
|---|---|---|---|
| 1 | **Marine Survey** | Marine Survey (ID 2, `L`) | `Vessel Name`, `Survey Type`, `Survey No`, `Survey Date End`, `Survey Location`, `Surveyor Name` |
| 2 | **Equipment Maintenance** | Equipment Maintenance (ID 3, `H`) | `Equipment Name`, `Serial No`, `Defect Description`, `Maintenance Type` |
| 3 | **Manufacturing QC** | Manufacturing QC (ID 4, `E`) | `Lot No`, `Part No`, `Part Description`, `Factory Location` |
| 4 | **Wind Turbine** | Wind Turbine (ID 5, `W`) | `Turbine ID`, `Turbine Location` |
| 5 | **Material Receipt** | Material Inspection (ID 6, `M`) | `Supplier Name *`, `Purchase Order` |

### Common Form Fields (All Types):
- `*Job No`
- `*Job Description`
- `*Inspection Agency`
- `*Inspection Type` (5 types)
- `*Inspection Start Date`
- `*Remarks`
- `*Inspection Stage`
- `*Level`

---

## 🚀 2. How to Run the Web Form

1. Ensure the VeriSure Django Server is running:
   ```bash
   cd D:\AZURE_VeriSure\VeriSure
   .\backendvenv\Scripts\activate
   python manage.py runserver_plus --cert-file cert.crt 0.0.0.0:8000
   ```

2. Start the Angular Job Creation Form:
   ```bash
   cd D:\VS_JobCreation\veri_sure_jobform\frontend
   npm start
   ```
   Open **`http://localhost:4200`** in your browser.

When you fill the form and click **Add Job**, the form automatically submits the job via the proxy to `https://127.0.0.1:8000/api/jobs/`.

---

## 🐍 3. Python ERP Simulator

To simulate ERP job generation and push directly to VeriSure:

```bash
cd D:\VS_JobCreation\veri_sure_jobform\erp_simulator

# Generate 5 jobs and push directly to VeriSure:
python erp_simulator.py --push

# Generate 3 Marine Survey jobs and push:
python erp_simulator.py --push --generate 3 --type "Marine Survey"
```

Jobs are ingested immediately and available for inspection in **VeriSureTab**.
