export type InspectionType =
  | 'Manufacturing QC'
  | 'Equipment Maintenance'
  | 'Marine Survey'
  | 'Wind Turbine'
  | 'Material Receipt';

export interface InspectionJob {
  // Common Fields
  jobNo: string;
  jobDescription: string;
  inspectionAgency: string;
  inspectionType: InspectionType;
  inspectionStartDate: string;
  remarks: string;
  inspectionStage: string;
  level: string;

  // Manufacturing QC Fields
  lotNo?: string;
  partNo?: string;
  partDescription?: string;
  factoryLocation?: string;

  // Equipment Maintenance Fields
  equipmentName?: string;
  serialNo?: string;
  defectDescription?: string;
  maintenanceType?: string;

  // Marine Survey Fields
  vesselName?: string;
  surveyType?: string;
  surveyNo?: string;
  surveyDateEnd?: string;
  surveyLocation?: string;
  surveyorName?: string;

  // Wind Turbine Fields
  turbineId?: string;
  turbineLocation?: string;

  // Material Receipt Fields
  supplierName?: string;
  purchaseOrder?: string;

  // Metadata
  created_at?: string;
  source?: string;
}

export interface ApiResponse<T = any> {
  status: string;
  job_no?: string;
  total_jobs?: number;
  data?: T;
  error?: string;
}
