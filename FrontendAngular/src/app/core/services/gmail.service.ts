import {HttpClient, HttpParams} from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Email } from '../../shared/models/email';
import {EmailStats} from '../../shared/models/email-stats';

@Injectable({ providedIn: 'root' })
export class GmailService {
  private baseUrl = 'https://bachelorthesis-production-8acf.up.railway.app';

  constructor(private http: HttpClient) {}

  getEmails(page: number = 1, pageSize: number = 10): Observable<{ emails: Email[], total: number }> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('page_size', pageSize.toString());

    return this.http.get<{ emails: Email[], total: number}>(`${this.baseUrl}/emails/get_emails`, { params });
  }

  analyzeText(text: string): Observable<{ prediction: string }> {
    return this.http.post<{ prediction: string }>(`${this.baseUrl}/emails/predict_text`, { text });
  }

  analyzeUrl(url: string): Observable<{ prediction: string; label?: string }> {
    return this.http.post<{ prediction: string; label?: string }>(
      `${this.baseUrl}/emails/predict_url`,
      { url }
    );
  }

  reportFalsePositive(emailId: number) {
    return this.http.post(`${this.baseUrl}/emails/report-fp`, { email_id: emailId });
  }

  getEmailStats(): Observable<EmailStats> {
    return this.http.get<EmailStats>(`${this.baseUrl}/emails/stats`);
  }
}
