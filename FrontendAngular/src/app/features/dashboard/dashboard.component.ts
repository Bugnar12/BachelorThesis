import { Component, OnInit } from '@angular/core';
import { GmailService } from '../../core/services/gmail.service';
import { Email } from '../../shared/models/email';
import { HeaderComponent } from '../../shared/components/header/header.component';
import {DecimalPipe, NgClass, NgForOf, NgIf, TitleCasePipe} from '@angular/common';
import {ActivatedRoute, Router, RouterLink} from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { LoadingSpinnerComponent } from '../../shared/components/loading/loading.component';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatCard } from '@angular/material/card';
import {Prediction} from '../../shared/models/prediction';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  imports: [
    HeaderComponent,
    NgIf,
    NgForOf,
    LoadingSpinnerComponent,
    MatExpansionModule,
    MatButtonModule,
    MatIconModule,
    MatCard,
    RouterLink,
    NgClass,
    TitleCasePipe,
    DecimalPipe
  ],
  styleUrls: ['./dashboard.component.scss'],
  standalone: true
})
export class DashboardComponent implements OnInit {
  emails: Email[] = [];
  isLoading = true;
  totalEmails = 0;
  currentPage = 1;
  pageSize = 10;
  selectedEmailId: number | null = null;

  constructor(
    private gmailService: GmailService,
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      const accessToken = params['access_token'];
      const refreshToken = params['refresh_token'];

      if (accessToken) {
        this.authService.storeTokens(accessToken, refreshToken);

        this.router.navigate([], {
          queryParams: {},
          replaceUrl: true
        }).then(() => this.loadEmails());
      } else {
        this.loadEmails();
      }
    });
  }

  loadEmails(): void {
    this.isLoading = true;
    console.log('[Dashboard] Fetching emails...');

    this.gmailService.getEmails(this.currentPage, this.pageSize).subscribe({
      next: (response) => {
        console.log('[Dashboard] Emails received:', response.emails);

        this.emails = response.emails.map(email => ({
          ...email,
          url_prediction: this.tryParsePrediction(email.url_prediction),
          text_prediction: this.tryParsePrediction(email.text_prediction),
          vt_domain_result: this.tryParsePrediction(email.vt_domain_result)
        }));

        this.totalEmails = response.total;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('[Dashboard] Email fetch failed:', err);
        this.isLoading = false;
      }
    });
  }

  toggleDetail(emailId: number): void {
    this.selectedEmailId = this.selectedEmailId === emailId ? null : emailId;
  }

  onPageChange(newPage: number): void {
    if (newPage < 1 || newPage > this.getTotalPages) return;
    this.currentPage = newPage;
    this.loadEmails();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  get getTotalPages(): number {
    return Math.ceil(this.totalEmails / this.pageSize);
  }

  isPredictionObject(
    pred: any
  ): pred is { label?: string; prediction?: string; score?: number; confidence?: number } {
    return (
      pred &&
      typeof pred === 'object' &&
      ('prediction' in pred || 'label' in pred)
    );
  }

  getLabel = (p: any) => ('prediction' in p ? p.prediction : p.label);
  getScore = (p: any) => ('confidence' in p ? p.confidence : p.score);


  private tryParsePrediction(input: string | any): any {
    if (typeof input === 'string' && input.trim().startsWith('{')) {
      try {
        const parsed = JSON.parse(input);

        // Special case for VirusTotal-style prediction
        if ('prediction' in parsed && Array.isArray(parsed.prediction)) {
          return parsed.prediction[0]; // e.g., "safe"
        }

        return parsed;
      } catch {
        return input;
      }
    }

    return input;
  }

  reportFalsePositive(emailId: number): void {
    this.gmailService.reportFalsePositive(emailId).subscribe({
      next: () => {
        console.log(`[Report FP] Email #${emailId} reported as false positive`);
        alert('Thank you! We will review the flagged email.');
      },
      error: (err) => {
        console.error('[Report FP] Failed to report:', err);
        alert('Failed to send report. Please try again later.');
      }
    });
  }

}
