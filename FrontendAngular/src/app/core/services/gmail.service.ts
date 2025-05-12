import {HttpClient, HttpParams} from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Email } from '../../shared/models/email';

@Injectable({ providedIn: 'root' })
export class GmailService {
  private baseUrl = 'http://localhost:5000';

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

}
