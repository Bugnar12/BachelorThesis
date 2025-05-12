import { Component } from '@angular/core';
import { GmailService } from '../../core/services/gmail.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HeaderComponent } from '../../shared/components/header/header.component';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { jwtDecode } from 'jwt-decode';
import {ActivatedRoute} from '@angular/router';

@Component({
  selector: 'app-analyze',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    HeaderComponent,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule
  ],
  templateUrl: './manual-analyze.component.html',
  styleUrls: ['./manual-analyze.component.css']
})
export class ManualAnalyzeComponent {
  emailText = '';
  url = '';
  emailResult: { prediction: string } | null = null;
  urlResult: { label?: string, prediction?: string, score?: number } | null = null;
  isLoadingText = false;
  isLoadingUrl = false;
  showSessionExpiredMessage = false;

  constructor(private gmailService: GmailService, private route: ActivatedRoute) {
    this.route.queryParams.subscribe(params => {
      if (params['session_expired'] === 'true') {
        this.showSessionExpiredMessage = true;
      }
    });
  }

  analyzeText() {
    this.isLoadingText = true;
    this.gmailService.analyzeText(this.emailText).subscribe({
      next: (res: any) => {
        const raw = res?.prediction;
        const value = typeof raw === 'string' ? raw : raw?.prediction || 'Unknown';
        this.emailResult = { prediction: value };
      },
      error: () => this.emailResult = { prediction: 'Error analyzing text.' },
      complete: () => this.isLoadingText = false
    });
  }

  analyzeUrl() {
    this.isLoadingUrl = true;
    this.gmailService.analyzeUrl(this.url).subscribe({
      next: res => this.urlResult = res,
      error: () => this.urlResult = { prediction: 'Error analyzing URL.' },
      complete: () => this.isLoadingUrl = false
    });
  }

  handleLoginClick(): void {
    const accessToken = localStorage.getItem('access_token');

    if (accessToken && !this.isTokenExpired(accessToken)) {
      window.location.href = '/dashboard';
    } else {
      window.location.href = 'http://localhost:5000/gmail/authorize';
    }
  }

  private isTokenExpired(token: string): boolean {
    try {
      const decoded: any = jwtDecode(token);
      const now = Math.floor(Date.now() / 1000);
      return decoded.exp < now;
    } catch {
      return true; // Treat invalid token as expired
    }
  }
}
