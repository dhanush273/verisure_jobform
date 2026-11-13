import os
import sys
import webbrowser
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(CURRENT_DIR, "frontend")
DIST_DIR = os.path.join(FRONTEND_DIR, "dist", "frontend", "browser")
DATA_DIR = os.path.join(CURRENT_DIR, "data")
ERP_FILE = os.path.join(DATA_DIR, "erp_jobs.json")
VERISURE_FILE = os.path.join(DATA_DIR, "verisure_jobs.json")

app = FastAPI(title="VeriSure DigitalQC Job Portal (Angular 17)", version="2.0.0")

# Enable CORS for Angular development server (e.g. localhost:4200)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.get("/api/erp-jobs")
async def get_erp_jobs():
    """Retrieve all simulated ERP records saved in JSON."""
    if os.path.exists(ERP_FILE):
        try:
            with open(ERP_FILE, "r", encoding="utf-8") as f:
                return JSONResponse(content=json.load(f))
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})
    return JSONResponse(content=[])


@app.post("/api/jobs")
async def save_job(request: Request):
    """Save submitted form job directly to data/erp_jobs.json."""
    try:
        job = await request.json()
        os.makedirs(DATA_DIR, exist_ok=True)
        
        erp_jobs = []
        if os.path.exists(ERP_FILE):
            try:
                with open(ERP_FILE, "r", encoding="utf-8") as f:
                    erp_jobs = json.load(f)
            except Exception:
                erp_jobs = []
        
        job_key = job.get("jobNo") or job.get("job_no")
        erp_jobs = [j for j in erp_jobs if (j.get("jobNo") or j.get("job_no")) != job_key]
        erp_jobs.insert(0, job)
        
        with open(ERP_FILE, "w", encoding="utf-8") as f:
            json.dump(erp_jobs, f, indent=2)
            
        return {"status": "success", "job_no": job_key, "total_jobs": len(erp_jobs)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# Mount Angular 17 build assets if available
if os.path.exists(DIST_DIR):
    assets_dir = os.path.join(DIST_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # Mount remaining root static files from dist
    app.mount("/static", StaticFiles(directory=DIST_DIR), name="static")


@app.get("/{full_path:path}")
async def serve_angular_app(full_path: str):
    """Serve Angular 17 client SPA, with fallback for index.html."""
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")

    if os.path.exists(DIST_DIR):
        requested_file = os.path.join(DIST_DIR, full_path)
        if full_path and os.path.isfile(requested_file):
            return FileResponse(requested_file)

        index_file = os.path.join(DIST_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)

    raise HTTPException(
        status_code=404,
        detail="Angular 17 build not found. Please run 'npm run build' inside the frontend directory."
    )


def main():
    port = int(os.environ.get("PORT", 4200))
    host = "127.0.0.1"
    url = f"http://localhost:{port}"

    print("\n" + "=" * 65)
    print("  VERISURE DIGITALQC - ANGULAR 17 PORTAL")
    print("=" * 65)
    print(f"  Portal URL:       {url}")
    print(f"  Angular Dist:     {DIST_DIR}")
    print(f"  ERP JSON File:    {ERP_FILE}")
    print("=" * 65 + "\n")

    try:
        webbrowser.open(url)
    except Exception:
        pass

    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
