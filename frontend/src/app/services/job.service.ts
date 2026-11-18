import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { InspectionJob, InspectionType, ApiResponse } from '../models/job.model';

@Injectable({
  providedIn: 'root'
})
export class JobService {
  private readonly apiUrl = 'https://192.168.5.157:8000/api';
  private readonly storageKey = 'verisure_jobs_json';
  private jobsSubject = new BehaviorSubject<InspectionJob[]>([]);
  public jobs$ = this.jobsSubject.asObservable();

  constructor(private http: HttpClient) {
    this.loadInitialJobs();
  }

  /**
   * Load jobs from localStorage immediately, then refresh from backend API.
   */
  public loadInitialJobs(): void {
    const localJobs = this.getLocalJobs();
    this.jobsSubject.next(localJobs);

    this.fetchBackendJobs().subscribe(backendJobs => {
      if (backendJobs && backendJobs.length > 0) {
        // Merge without duplicates (favoring newest)
        const jobMap = new Map<string, InspectionJob>();
        [...localJobs, ...backendJobs].forEach(job => {
          if (job.jobNo) {
            jobMap.set(job.jobNo, job);
          }
        });
        const merged = Array.from(jobMap.values());
        this.saveLocalJobs(merged);
        this.jobsSubject.next(merged);
      }
    });
  }

  /**
   * Fetch saved ERP jobs from backend API.
   */
    public fetchBackendJobs(): Observable<InspectionJob[]> {
    return this.http.get<InspectionJob[]>(
      `${this.apiUrl}/jobs`
    ).pipe(
      catchError(err => {
        console.error('Backend GET error:', err);
        return of([] as InspectionJob[]);
      })
    );
  }

  /**
   * Save a job both to the backend and to localStorage.
   */
  public saveJob(job: InspectionJob): Observable<ApiResponse> {

    job.created_at = job.created_at || new Date().toISOString();
    job.source = job.source || 'VERISURE_ANGULAR17_FORM';

    // Save locally
    const currentJobs = this.jobsSubject.value;

    const updated = [
      job,
      ...currentJobs.filter(j => j.jobNo !== job.jobNo)
    ];

    this.saveLocalJobs(updated);
    this.jobsSubject.next(updated);

    // Send to FastAPI backend
    return this.http.post<ApiResponse>(
      `${this.apiUrl}/jobs`,
      job
    ).pipe(
      catchError(err => {
        console.error('Backend POST error:', err);

        return of({
          status: 'saved_locally',
          job_no: job.jobNo,
          total_jobs: updated.length
        });
      })
    );
  }

  public getLocalJobs(): InspectionJob[] {
    try {
      const stored = localStorage.getItem(this.storageKey);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  private saveLocalJobs(jobs: InspectionJob[]): void {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(jobs, null, 2));
    } catch (e) {
      console.error('Failed to write to localStorage', e);
    }
  }

  /**
   * Returns simulated ERP data for the given inspection type.
   */
  public getErpMockData(type: InspectionType): Partial<InspectionJob> {
    const today = new Date().toISOString().split('T')[0];
    const futureDate = new Date(Date.now() + 10 * 86400000).toISOString().split('T')[0];
    const randNum = Math.floor(1000 + Math.random() * 9000);

    const mocks: Record<InspectionType, Partial<InspectionJob>> = {
      'Manufacturing QC': {
        jobNo: `ERP-JOB-2026-${randNum}`,
        jobDescription: 'Automotive Transmission Planetary Gearset Audit',
        inspectionAgency: 'VeriSure In-House QA',
        inspectionType: 'Manufacturing QC',
        inspectionStartDate: today,
        remarks: 'Case hardening depth and flank tooth roughness Ra < 0.4µm.',
        inspectionStage: 'Stage 1',
        level: 'Level 1',
        lotNo: 'LOT-GRS-310',
        partNo: 'PN-PG-8104',
        partDescription: 'Heat-Treated Planetary Sun & Ring Gearset',
        factoryLocation: 'Banglore'
      },
      'Equipment Maintenance': {
        jobNo: `ERP-JOB-2026-${randNum}`,
        jobDescription: '5-Axis CNC Milling Center Spindle Overhaul',
        inspectionAgency: 'TUV Rheinland',
        inspectionType: 'Equipment Maintenance',
        inspectionStartDate: today,
        remarks: 'Harmonic vibration check on dynamic spindle bearings.',
        inspectionStage: 'Stage 2',
        level: 'Level 2',
        equipmentName: 'DMG Mori 5-Axis Mill (MC-04)',
        serialNo: 'SN-DMG-54019-B',
        defectDescription: 'Spindle harmonic vibration exceeding ISO threshold (4.2 mm/s).',
        maintenanceType: 'Repair'
      },
      'Marine Survey': {
        jobNo: `ERP-JOB-2026-${randNum}`,
        jobDescription: 'Bulk Carrier Hull Integrity and Bilge Piping Survey',
        inspectionAgency: 'Bureau Veritas',
        inspectionType: 'Marine Survey',
        inspectionStartDate: today,
        remarks: 'Ultrasonic thickness gauge testing on forward ballast plating.',
        inspectionStage: 'Stage 1',
        level: 'Level 1',
        vesselName: 'MV Pacific Explorer',
        surveyType: 'Annual Survey',
        surveyNo: `SRV-MAR-2026-0${Math.floor(10 + Math.random() * 89)}`,
        surveyDateEnd: futureDate,
        surveyLocation: 'Port of Rotterdam Drydock Berth 4',
        surveyorName: 'Capt. E. Henderson, CMarEng'
      },
      'Wind Turbine': {
        jobNo: `ERP-JOB-2026-${randNum}`,
        jobDescription: 'Offshore Wind Turbine 8MW Nacelle Diagnostic',
        inspectionAgency: 'DNV GL',
        inspectionType: 'Wind Turbine',
        inspectionStartDate: today,
        remarks: 'Borescope inspection of high-speed planetary stage bearings.',
        inspectionStage: 'Stage 2',
        level: 'Level 2',
        turbineId: `WTG-OFF-B${Math.floor(10 + Math.random() * 20)}-3`,
        turbineLocation: 'North Sea Array Sector 3 (Lat 54.21N, Long 6.44E)'
      },
      'Material Receipt': {
        jobNo: `ERP-JOB-2026-${randNum}`,
        jobDescription: 'Inbound Aerospace Titanium Ingot Ingress Inspection',
        inspectionAgency: "Lloyd's Register",
        inspectionType: 'Material Receipt',
        inspectionStartDate: today,
        remarks: 'Spectrometer composition analysis against Mill Test Certificate.',
        inspectionStage: 'Stage 3',
        level: 'Level 3',
        supplierName: 'Apex Titanium Metallurgy Corp.',
        purchaseOrder: `PO-2026-TIT-${Math.floor(10000 + Math.random() * 89999)}`
      }
    };

    return mocks[type] || {};
  }
}
