import os
import sys
import json
import random
import argparse
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import requests

# Add parent directory to path so models & storage can be shared if needed
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, PROJECT_ROOT)

DEFAULT_API_URL = "http://localhost:8000/api/jobs"
DEFAULT_JSON_PATH = os.path.join(PROJECT_ROOT, "data", "erp_jobs.json")

# Realistic ERP Reference Data for Industrial Quality Inspection
AGENCIES = [
    "Bureau Veritas Industry",
    "DNV GL Quality Services",
    "TUV Rheinland Global",
    "VeriSure In-House QA",
    "Lloyd's Register EMEA",
    "SGS Industrial Inspection",
    "Intertek Quality Assurance",
]

STAGES = [
    "Stage 1",
    "Stage 2",
    "Stage 3",
    "NA",
]

LEVELS = [
    "Level 1 - Critical Safety Component",
    "Level 2 - High Precision Mechanical",
    "Level 3 - Standard Assembly Spec",
    "Level 4 - Routine Visual & Dimensional",
]

MANUFACTURING_DATA = [
    {
        "desc": "High-Pressure Hydraulic Stator Housing Inspection",
        "lot_prefix": "LOT-HYD-",
        "part_no": "PN-HST-9941",
        "part_desc": "Hardened Alloy Hydraulic Stator Casting",
        "location": "Banglore",
        "remark": "Coordinate Measuring Machine (CMM) tolerance check ±0.005mm.",
    },
    {
        "desc": "Titanium Compressor Rotor Blade Quality Check",
        "lot_prefix": "LOT-TIT-",
        "part_no": "PN-CRB-3302",
        "part_desc": "Forged Ti-6Al-4V Compressor Rotor Blade",
        "location": "Mumbai",
        "remark": "Ultrasonic non-destructive testing (NDT) for internal micro-voids.",
    },
    {
        "desc": "Automotive Transmission Planetary Gearset Audit",
        "lot_prefix": "LOT-GRS-",
        "part_no": "PN-PG-8104",
        "part_desc": "Heat-Treated Planetary Sun & Ring Gearset",
        "location": "Banglore",
        "remark": "Case hardening depth and flank tooth roughness Ra < 0.4µm.",
    },
]

MAINTENANCE_DATA = [
    {
        "desc": "5-Axis CNC Milling Center Spindle Overhaul",
        "eq_name": "DMG Mori 5-Axis Mill (MC-04)",
        "sn": "SN-DMG-54019-B",
        "defect": "Spindle harmonic vibration exceeding ISO 10816 threshold (4.2 mm/s).",
        "maint_type": "Corrective / Breakdown",
        "remark": "Replace dynamic spindle ceramic bearings and perform dynamic balancing.",
    },
    {
        "desc": "Hydraulic Press Unit 400T Cylinder Inspection",
        "eq_name": "Schuler 400-Ton Hydraulic Forming Press",
        "sn": "SN-SCH-400T-08",
        "defect": "Minor seal weeping on secondary hydraulic piston gland.",
        "maint_type": "Preventive Maintenance",
        "remark": "Hydrostatic pressure test holding 320 bar for 45 minutes.",
    },
    {
        "desc": "Robotic Spot Welding Cell Calibration & Service",
        "eq_name": "KUKA KR-210 Industrial Spot Welding Robot",
        "sn": "SN-KUKA-8821",
        "defect": "Electrode tip alignment deviation detected on axis 6.",
        "maint_type": "Condition-Based Monitoring",
        "remark": "Recalibrate TCP tool center point and replace electrode caps.",
    },
]

MARINE_DATA = [
    {
        "desc": "Bulk Carrier Hull Integrity and Bilge Piping Survey",
        "vessel": "MV Pacific Explorer",
        "survey_type": "Hull & Machinery Survey",
        "survey_no": "SRV-MAR-2026-041",
        "survey_loc": "Port of Rotterdam Drydock Berth 4",
        "surveyor": "Capt. E. Henderson, CMarEng",
        "remark": "Ultrasonic thickness measurement on forward ballast tank plating.",
    },
    {
        "desc": "LNG Tanker Cryogenic Fuel Manifold Annual Audit",
        "vessel": "LNGC Arctic Aurora",
        "survey_type": "Annual Survey",
        "survey_no": "SRV-LNG-2026-118",
        "survey_loc": "Singapore Jurong Shipyard Dock 2",
        "surveyor": "Dr. Hans-Peter Keller, FRINA",
        "remark": "Helium leak detection on vacuum insulation barrier joints.",
    },
    {
        "desc": "Offshore Supply Vessel Deck Crane Load Rating Test",
        "vessel": "OSV Viking Endurance",
        "survey_type": "Cargo Gear Inspection",
        "survey_no": "SRV-OSV-2026-089",
        "survey_loc": "Aberdeen Deepwater Marine Terminal",
        "surveyor": "A. MacIntyre, Marine Surveyor",
        "remark": "Proof load testing with 55-ton water bag ballast.",
    },
]

TURBINE_DATA = [
    {
        "desc": "Offshore Wind Turbine 8MW Nacelle Gearbox Diagnostic",
        "turbine_id": "WTG-OFF-B14",
        "location": "North Sea Array Sector 3 (Lat 54.21N, Long 6.44E)",
        "remark": "Borescope inspection of high-speed planetary stage bearings.",
    },
    {
        "desc": "Onshore 4.2MW Wind Turbine Rotor Blade Pitch Audit",
        "turbine_id": "WTG-LND-C08",
        "location": "Tehachapi Wind Resource Area, California",
        "remark": "Drone thermographic scan of blade leading edge erosion shields.",
    },
    {
        "desc": "Coastal Turbine Yaw Drive Mechanism & Brake Inspection",
        "turbine_id": "WTG-CST-A22",
        "location": "Baltic Coastal Wind Farm Block 4",
        "remark": "Torque check on yaw ring foundation bolts and hydraulic caliper check.",
    },
]

MATERIAL_DATA = [
    {
        "desc": "Inbound Aerospace Grade Titanium Ingot Ingress Inspection",
        "supplier": "Apex Titanium Metallurgy Corp.",
        "po": "PO-2026-TIT-88301",
        "remark": "Verify chemical spectrometer composition analysis against Mill Test Certificate (MTC 3.1).",
    },
    {
        "desc": "High-Tensile Fasteners Grade 12.9 Receipt Verification",
        "supplier": "Bollhoff Fastening Systems GmbH",
        "po": "PO-2026-FST-44120",
        "remark": "Random Rockwell C hardness test on 50 samples per ASTM F606.",
    },
    {
        "desc": "Composite Carbon Fiber Prepreg Roll Ingress QC",
        "supplier": "Toray Advanced Materials Inc.",
        "po": "PO-2026-CMP-90955",
        "remark": "Check cold-chain temperature logger loggers and resin matrix tackiness.",
    },
]


def generate_simulated_erp_job(
    inspection_type: Optional[str] = None, job_seq: Optional[int] = None
) -> Dict[str, Any]:
    
    types = [
        "Manufacturing QC",
        "Equipment Maintenance",
        "Marine Survey",
        "Wind Turbine",
        "Material Receipt",
    ]

    selected_type = inspection_type if inspection_type in types else random.choice(types)
    seq = job_seq or random.randint(1000, 9999)
    today = datetime.now()
    start_date = (today + timedelta(days=random.randint(0, 5))).strftime("%Y-%m-%d")

    base_job = {
        "job_no": f"ERP-JOB-{datetime.now().year}-{seq}",
        "job_description": "",
        "inspection_agency": random.choice(AGENCIES),
        "inspection_type": selected_type,
        "inspection_start_date": start_date,
        "remarks": "",
        "inspection_stage": random.choice(STAGES),
        "level": random.choice(LEVELS),
        "source": "ERP_SIMULATOR",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "QUEUED",
    }

    if selected_type == "Manufacturing QC":
        sample = random.choice(MANUFACTURING_DATA)
        base_job.update(
            {
                "job_description": sample["desc"],
                "remarks": sample["remark"],
                "lot_no": f"{sample['lot_prefix']}{random.randint(100, 999)}",
                "part_no": sample["part_no"],
                "part_description": sample["part_desc"],
                "factory_location": sample["location"],
            }
        )

    elif selected_type == "Equipment Maintenance":
        sample = random.choice(MAINTENANCE_DATA)
        base_job.update(
            {
                "job_description": sample["desc"],
                "remarks": sample["remark"],
                "equipment_name": sample["eq_name"],
                "serial_no": sample["sn"],
                "defect_description": sample["defect"],
                "maintenance_type": sample["maint_type"],
            }
        )

    elif selected_type == "Marine Survey":
        sample = random.choice(MARINE_DATA)
        end_date = (today + timedelta(days=random.randint(7, 20))).strftime("%Y-%m-%d")
        base_job.update(
            {
                "job_description": sample["desc"],
                "remarks": sample["remark"],
                "vessel_name": sample["vessel"],
                "survey_type": sample["survey_type"],
                "survey_no": f"{sample['survey_no']}-{random.randint(10, 99)}",
                "survey_date_end": end_date,
                "survey_location": sample["survey_loc"],
                "surveyor_name": sample["surveyor"],
            }
        )

    elif selected_type == "Wind Turbine":
        sample = random.choice(TURBINE_DATA)
        base_job.update(
            {
                "job_description": sample["desc"],
                "remarks": sample["remark"],
                "turbine_id": f"{sample['turbine_id']}-{random.randint(1, 9)}",
                "turbine_location": sample["location"],
            }
        )

    elif selected_type == "Material Receipt":
        sample = random.choice(MATERIAL_DATA)
        base_job.update(
            {
                "job_description": sample["desc"],
                "remarks": sample["remark"],
                "supplier_name": sample["supplier"],
                "purchase_order": sample["po"],
            }
        )

    return base_job


def save_jobs_to_json(jobs: List[Dict[str, Any]], filepath: str = DEFAULT_JSON_PATH) -> str:
    """Save the list of ERP simulated jobs to a JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    existing: List[Dict[str, Any]] = []
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []

    # Merge avoiding duplicates by job_no
    new_job_nos = {j.get("job_no") for j in jobs}
    merged = [j for j in existing if j.get("job_no") not in new_job_nos]
    merged = jobs + merged

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)

    return filepath


def push_job_to_verisure(job_data: Dict[str, Any], api_url: str = DEFAULT_API_URL) -> Dict[str, Any]:
    """
    Sends an HTTP POST request to the VeriSure API with the JSON payload.
    """
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    try:
        response = requests.post(api_url, json=job_data, headers=headers, timeout=10)
        return {
            "success": response.status_code in (200, 201),
            "status_code": response.status_code,
            "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "status_code": 0,
            "error": f"Cannot connect to VeriSure API at {api_url}. Is the server running?",
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": 500,
            "error": str(e),
        }


def run_interactive_form() -> Dict[str, Any]:
    """
    Interactive command-line prompt allowing a user or operator to fill
    detail to generate an ERP job record manually.
    """
    print("\n" + "=" * 60)
    print("  VERISURE ERP JOB GENERATOR - INTERACTIVE CONSOLE")
    print("=" * 60)

    print("\nSelect Inspection Type (Total 5 Available):")
    print("  [1] Manufacturing QC")
    print("  [2] Equipment Maintenance")
    print("  [3] Marine Survey")
    print("  [4] Wind Turbine")
    print("  [5] Material Receipt")

    choice = input("\nEnter choice (1-5) [default: 1]: ").strip() or "1"
    type_map = {
        "1": "Manufacturing QC",
        "2": "Equipment Maintenance",
        "3": "Marine Survey",
        "4": "Wind Turbine",
        "5": "Material Receipt",
    }
    insp_type = type_map.get(choice, "Manufacturing QC")

    job_no = input(f"Enter Job No [ERP-JOB-{random.randint(1000, 9999)}]: ").strip() or f"ERP-JOB-{random.randint(1000, 9999)}"
    job_desc = input("Enter Job Description: ").strip() or f"ERP Standard Inspection - {insp_type}"
    agency = input(f"Enter Inspection Agency [{AGENCIES[0]}]: ").strip() or AGENCIES[0]
    start_date = input(f"Enter Start Date (YYYY-MM-DD) [{datetime.now().strftime('%Y-%m-%d')}]: ").strip() or datetime.now().strftime("%Y-%m-%d")
    remarks = input("Enter Remarks: ").strip() or "Standard ERP Quality Inspection Requirement."
    stage = input(f"Enter Inspection Stage [{STAGES[1]}]: ").strip() or STAGES[1]
    level = input(f"Enter Level [{LEVELS[0]}]: ").strip() or LEVELS[0]

    job = {
        "job_no": job_no,
        "job_description": job_desc,
        "inspection_agency": agency,
        "inspection_type": insp_type,
        "inspection_start_date": start_date,
        "remarks": remarks,
        "inspection_stage": stage,
        "level": level,
        "source": "ERP_INTERACTIVE_CLI",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "QUEUED",
    }

    if insp_type == "Manufacturing QC":
        job["lot_no"] = input("Enter Lot No [LOT-A101]: ").strip() or "LOT-A101"
        job["part_no"] = input("Enter Part No [PN-5011]: ").strip() or "PN-5011"
        job["part_description"] = input("Enter Part Description [Precision Stamped Plate]: ").strip() or "Precision Stamped Plate"
        job["factory_location"] = input("Enter Factory Location [Banglore]: ").strip() or "Banglore"

    elif insp_type == "Equipment Maintenance":
        job["equipment_name"] = input("Enter Equipment Name [CNC Lathe A]: ").strip() or "CNC Lathe A"
        job["serial_no"] = input("Enter Serial No [SN-9902]: ").strip() or "SN-9902"
        job["defect_description"] = input("Enter Defect Description [Oil Seal Leakage]: ").strip() or "Oil Seal Leakage"
        job["maintenance_type"] = input("Enter Maintenance Type [Corrective / Breakdown]: ").strip() or "Corrective / Breakdown"

    elif insp_type == "Marine Survey":
        job["vessel_name"] = input("Enter Vessel Name [MV Atlantic Queen]: ").strip() or "MV Atlantic Queen"
        job["survey_type"] = input("Enter Survey Type [Hull & Machinery]: ").strip() or "Hull & Machinery"
        job["survey_no"] = input("Enter Survey No [SRV-2026-90]: ").strip() or "SRV-2026-90"
        job["survey_date_end"] = input(f"Enter Survey End Date [{datetime.now().strftime('%Y-%m-%d')}]: ").strip() or datetime.now().strftime("%Y-%m-%d")
        job["survey_location"] = input("Enter Survey Location [Drydock Berth 2]: ").strip() or "Drydock Berth 2"
        job["surveyor_name"] = input("Enter Surveyor Name [Capt. Smith]: ").strip() or "Capt. Smith"

    elif insp_type == "Wind Turbine":
        job["turbine_id"] = input("Enter Turbine ID [WTG-04]: ").strip() or "WTG-04"
        job["turbine_location"] = input("Enter Turbine Location [North Sector Farm]: ").strip() or "North Sector Farm"

    elif insp_type == "Material Receipt":
        job["supplier_name"] = input("Enter Supplier Name * [Acme Steel Supplies]: ").strip() or "Acme Steel Supplies"
        job["purchase_order"] = input("Enter Purchase Order [PO-99120]: ").strip() or "PO-99120"

    return job


def main():
    parser = argparse.ArgumentParser(description="ERP Job Generator and VeriSure API Pusher")
    parser.add_argument("--generate", type=int, default=0, help="Number of synthetic ERP jobs to auto-generate (e.g. 5 for all 5 types)")
    parser.add_argument("--type", type=str, choices=[
        "Manufacturing QC", "Equipment Maintenance", "Marine Survey", "Wind Turbine", "Material Receipt"
    ], help="Generate for a specific inspection type")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive CLI prompt to fill details")
    parser.add_argument("--output", type=str, default=DEFAULT_JSON_PATH, help="Target JSON file path")
    parser.add_argument("--push", action="store_true", help="Push generated JSON jobs to VeriSure API")
    parser.add_argument("--api-url", type=str, default=DEFAULT_API_URL, help="VeriSure API endpoint URL")

    args = parser.parse_args()

    jobs_to_process: List[Dict[str, Any]] = []

    if args.interactive:
        job = run_interactive_form()
        jobs_to_process.append(job)
    elif args.generate > 0:
        types = [
            "Manufacturing QC",
            "Equipment Maintenance",
            "Marine Survey",
            "Wind Turbine",
            "Material Receipt",
        ]
        count = args.generate
        for i in range(count):
            t = args.type if args.type else types[i % len(types)]
            job = generate_simulated_erp_job(inspection_type=t, job_seq=1001 + i)
            jobs_to_process.append(job)
    else:
        # Default behavior if run with no args: generate 5 jobs (1 for each of the 5 inspection types)
        print("No flags specified. Generating 5 ERP jobs (1 for each of the 5 Inspection Types)...")
        types = [
            "Manufacturing QC",
            "Equipment Maintenance",
            "Marine Survey",
            "Wind Turbine",
            "Material Receipt",
        ]
        for i, t in enumerate(types):
            job = generate_simulated_erp_job(inspection_type=t, job_seq=2001 + i)
            jobs_to_process.append(job)

    # 1. Save data to JSON
    saved_path = save_jobs_to_json(jobs_to_process, args.output)
    print(f"\n[SUCCESS] Generated {len(jobs_to_process)} ERP Job(s).")
    print(f"[STORED]  Data saved to JSON: {os.path.abspath(saved_path)}")

    # Display sample preview
    print("\n--- Sample Generated ERP Payload (JSON) ---")
    print(json.dumps(jobs_to_process[0], indent=2))

    # 2. Push to VeriSure if requested or if user specifies
    if args.push:
        print(f"\n[PUSHING] Sending {len(jobs_to_process)} job(s) to VeriSure API at {args.api_url}...")
        for j in jobs_to_process:
            res = push_job_to_verisure(j, args.api_url)
            if res.get("success"):
                print(f"  [OK] Job '{j['job_no']}' pushed successfully -> VeriSure Response: {res.get('response')}")
            else:
                print(f"  [FAIL] Job '{j['job_no']}' push failed: {res.get('error') or res.get('response')}")
    else:
        print("\n[NOTE] To push directly to VeriSure, start the server and run:")
        print(f"       python erp_simulator.py --push --api-url {args.api_url}")


if __name__ == "__main__":
    main()
