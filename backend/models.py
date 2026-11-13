from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, model_validator
from datetime import datetime, timezone


INSPECTION_TYPES = [
    "Manufacturing QC",
    "Equipment Maintenance",
    "Marine Survey",
    "Wind Turbine",
    "Material Receipt",
]


class BaseInspectionJob(BaseModel):
    # Common required fields across all 5 inspection types
    job_no: str = Field(..., description="Unique Job Identifier (e.g. JOB-2026-1001)")
    job_description: str = Field(..., description="Description of the inspection job")
    inspection_agency: str = Field(..., description="Agency performing inspection")
    inspection_type: Literal[
        "Manufacturing QC",
        "Equipment Maintenance",
        "Marine Survey",
        "Wind Turbine",
        "Material Receipt",
    ] = Field(..., description="One of the 5 supported inspection types")
    inspection_start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    remarks: str = Field(..., description="QC remarks or initial notes")
    inspection_stage: str = Field(..., description="Stage of the inspection")
    level: str = Field(..., description="Inspection level / criticality")

    # Dynamic fields for 'Manufacturing QC'
    lot_no: Optional[str] = None
    part_no: Optional[str] = None
    part_description: Optional[str] = None
    factory_location: Optional[str] = None

    # Dynamic fields for 'Equipment Maintenance'
    equipment_name: Optional[str] = None
    serial_no: Optional[str] = None
    defect_description: Optional[str] = None
    maintenance_type: Optional[str] = None

    # Dynamic fields for 'Marine Survey'
    vessel_name: Optional[str] = None
    survey_type: Optional[str] = None
    survey_no: Optional[str] = None
    survey_date_end: Optional[str] = None
    survey_location: Optional[str] = None
    surveyor_name: Optional[str] = None

    # Dynamic fields for 'Wind Turbine'
    turbine_id: Optional[str] = None
    turbine_location: Optional[str] = None

    # Dynamic fields for 'Material Receipt'
    supplier_name: Optional[str] = None
    purchase_order: Optional[str] = None

    # Metadata added upon ingestion
    created_at: Optional[str] = None
    source: Optional[str] = "ERP_SIMULATOR"  # or 'WEB_FORM', 'DIRECT_API'
    status: Optional[str] = "QUEUED"  # 'QUEUED', 'IN_PROGRESS', 'COMPLETED'

    @model_validator(mode="before")
    @classmethod
    def normalize_keys_and_validate(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        alias_map = {
            "Job No": "job_no",
            "jobNo": "job_no",
            "Job Description": "job_description",
            "jobDescription": "job_description",
            "Inspection Agency": "inspection_agency",
            "inspectionAgency": "inspection_agency",
            "Inspection Type": "inspection_type",
            "inspectionType": "inspection_type",
            "Inspection Start Date": "inspection_start_date",
            "inspectionStartDate": "inspection_start_date",
            "Remarks": "remarks",
            "Inspection Stage": "inspection_stage",
            "inspectionStage": "inspection_stage",
            "Level": "level",
            # Manufacturing QC
            "Lot No": "lot_no",
            "lotNo": "lot_no",
            "Part No": "part_no",
            "partNo": "part_no",
            "Part Description": "part_description",
            "partDescription": "part_description",
            "Factory Location": "factory_location",
            "factoryLocation": "factory_location",
            # Equipment Maintenance
            "Equipment Name": "equipment_name",
            "equipmentName": "equipment_name",
            "Serial No": "serial_no",
            "serialNo": "serial_no",
            "Defect Description": "defect_description",
            "defectDescription": "defect_description",
            "Maintenance Type": "maintenance_type",
            "maintenanceType": "maintenance_type",
            # Marine Survey
            "Vessel Name": "vessel_name",
            "vesselName": "vessel_name",
            "Survey Type": "survey_type",
            "surveyType": "survey_type",
            "Survey No": "survey_no",
            "surveyNo": "survey_no",
            "Survey Date End": "survey_date_end",
            "surveyDateEnd": "survey_date_end",
            "Survey Location": "survey_location",
            "surveyLocation": "survey_location",
            "Surveyor Name": "surveyor_name",
            "surveyorName": "surveyor_name",
            # Wind Turbine
            "Turbine ID": "turbine_id",
            "turbineId": "turbine_id",
            "Turbine Location": "turbine_location",
            "turbineLocation": "turbine_location",
            # Material Receipt
            "Supplier Name": "supplier_name",
            "supplierName": "supplier_name",
            "Supplier Name *": "supplier_name",
            "Purchase Order": "purchase_order",
            "purchaseOrder": "purchase_order",
        }

        normalized = {}
        for k, v in data.items():
            normalized_key = alias_map.get(k, k.lower().replace(" ", "_"))
            normalized[normalized_key] = v

        # Validation for Material Receipt
        if normalized.get("inspection_type") == "Material Receipt":
            if not normalized.get("supplier_name"):
                raise ValueError("Supplier Name is required for Material Receipt inspection type.")

        if not normalized.get("created_at"):
            normalized["created_at"] = datetime.now(timezone.utc).isoformat()

        return normalized
