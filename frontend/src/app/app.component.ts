import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { InspectionJob, InspectionType } from './models/job.model';
import { JobService } from './services/job.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit, OnDestroy {
  public title = 'VeriSure DigitalQC';
  public jobForm!: FormGroup;
  public inspectionTypes: InspectionType[] = [
    'Manufacturing QC',
    'Equipment Maintenance',
    'Marine Survey',
    'Wind Turbine',
    'Material Receipt'
  ];

  public inspectionStages = ['Stage 1', 'Stage 2', 'Stage 3', 'NA'];
  public inspectionLevels = ['Level 1', 'Level 2', 'Level 3', 'NA'];
  public factoryLocations = ['Banglore', 'Mumbai'];
  public maintenanceTypes = ['Annual Maintenance', 'Repair'];
  public marineSurveyTypes = ['Annual Survey', 'Hull Condition Monitoring'];

  // State
  public isSubmitting = false;
  public isSuccessModalOpen = false;
  public submittedJobNo = '';

  // Toast
  public toast = {
    show: false,
    message: '',
    icon: '✓'
  };
  private toastTimer: any = null;

  constructor(
    private fb: FormBuilder,
    private jobService: JobService
  ) {}

  ngOnInit(): void {
    this.initForm();
  }

  ngOnDestroy(): void {
    if (this.toastTimer) {
      clearTimeout(this.toastTimer);
    }
  }

  private initForm(): void {
    this.jobForm = this.fb.group({
      // Common mandatory fields
      jobNo: ['', Validators.required],
      jobDescription: ['', Validators.required],
      inspectionAgency: ['', Validators.required],
      inspectionType: ['Manufacturing QC' as InspectionType, Validators.required],
      inspectionStartDate: ['', Validators.required],
      remarks: ['', Validators.required],
      inspectionStage: ['', Validators.required],
      level: ['', Validators.required],

      // Manufacturing QC fields
      lotNo: [''],
      partNo: [''],
      partDescription: [''],
      factoryLocation: [''],

      // Equipment Maintenance fields
      equipmentName: [''],
      serialNo: [''],
      defectDescription: [''],
      maintenanceType: [''],

      // Marine Survey fields
      vesselName: [''],
      surveyType: [''],
      surveyNo: [''],
      surveyDateEnd: [''],
      surveyLocation: [''],
      surveyorName: [''],

      // Wind Turbine fields
      turbineId: [''],
      turbineLocation: [''],

      // Material Receipt fields
      supplierName: [''],
      purchaseOrder: ['']
    });

    this.jobForm.get('inspectionType')?.valueChanges.subscribe(type => {
      this.handleTypeChange(type);
    });
  }

  get currentInspectionType(): InspectionType {
    return this.jobForm.get('inspectionType')?.value || 'Manufacturing QC';
  }

  private handleTypeChange(type: InspectionType): void {
    const supplierControl = this.jobForm.get('supplierName');
    if (type === 'Material Receipt') {
      supplierControl?.setValidators([Validators.required]);
    } else {
      supplierControl?.clearValidators();
    }
    supplierControl?.updateValueAndValidity();
  }

  /**
   * Populate form using realistic ERP Simulated Data
   */
  public simulateErpData(): void {
    const currentType = this.currentInspectionType;
    const mock = this.jobService.getErpMockData(currentType);

    this.jobForm.patchValue(mock);
    this.showToast(`⚡ Filled simulated ERP data for '${currentType}'!`, '⚡');
  }

  /**
   * Form submission
   */
  public onSubmit(): void {
    if (this.jobForm.invalid) {
      this.jobForm.markAllAsTouched();
      this.showToast('Please fill out all mandatory fields marked with (*)', '⚠️');
      return;
    }

    const payload: InspectionJob = {
      ...this.jobForm.value,
      created_at: new Date().toISOString(),
      source: 'VERISURE_ANGULAR17_FORM'
    };

    this.isSubmitting = true;
    this.jobService.saveJob(payload).subscribe({
      next: (res) => {
        this.isSubmitting = false;
        this.submittedJobNo = payload.jobNo;
        this.isSuccessModalOpen = true;
        this.showToast(`✓ Job '${payload.jobNo}' Submitted Successfully!`, '✓');
      },
      error: (err) => {
        this.isSubmitting = false;
        console.error('Save job error', err);
        this.showToast('Job saved locally', 'ℹ️');
      }
    });
  }

  public closeSuccessModal(): void {
    this.isSuccessModalOpen = false;
  }

  public showToast(msg: string, icon: string = '✓'): void {
    if (this.toastTimer) {
      clearTimeout(this.toastTimer);
    }
    this.toast = {
      show: true,
      message: msg,
      icon
    };
    this.toastTimer = setTimeout(() => {
      this.toast.show = false;
    }, 3500);
  }
}
