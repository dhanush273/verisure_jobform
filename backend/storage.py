import json
import os
import threading
from typing import List, Dict, Any, Optional

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
VERISURE_STORAGE_FILE = os.path.join(DATA_DIR, "verisure_jobs.json")
ERP_STORAGE_FILE = os.path.join(DATA_DIR, "erp_jobs.json")

_lock = threading.Lock()


def _ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(VERISURE_STORAGE_FILE):
        with open(VERISURE_STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)
    if not os.path.exists(ERP_STORAGE_FILE):
        with open(ERP_STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)


def get_all_verisure_jobs() -> List[Dict[str, Any]]:
    """Retrieve all jobs stored in VeriSure system."""
    _ensure_data_files()
    with _lock:
        try:
            with open(VERISURE_STORAGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []


def save_verisure_job(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Append or update a job in VeriSure's persistent JSON store.
    Matches existing by job_no if already present.
    """
    _ensure_data_files()
    with _lock:
        try:
            with open(VERISURE_STORAGE_FILE, "r", encoding="utf-8") as f:
                jobs = json.load(f)
        except Exception:
            jobs = []

        # Check if job_no exists
        existing_idx = next(
            (i for i, j in enumerate(jobs) if j.get("job_no") == job_data.get("job_no")),
            None,
        )

        if existing_idx is not None:
            jobs[existing_idx] = {**jobs[existing_idx], **job_data}
        else:
            jobs.insert(0, job_data)  # newest first

        with open(VERISURE_STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=2)

        return job_data


def get_all_erp_jobs() -> List[Dict[str, Any]]:
    """Retrieve all simulated ERP records."""
    _ensure_data_files()
    with _lock:
        try:
            with open(ERP_STORAGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []


def save_erp_jobs(new_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Store generated ERP jobs into the erp_jobs.json file."""
    _ensure_data_files()
    with _lock:
        try:
            with open(ERP_STORAGE_FILE, "r", encoding="utf-8") as f:
                jobs = json.load(f)
        except Exception:
            jobs = []

        job_nos = {j.get("job_no") for j in new_jobs}
        # Keep non-duplicates
        jobs = [j for j in jobs if j.get("job_no") not in job_nos]
        jobs = new_jobs + jobs

        with open(ERP_STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=2)

        return jobs
