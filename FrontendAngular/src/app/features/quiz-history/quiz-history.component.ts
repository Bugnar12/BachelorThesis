import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule, DatePipe, NgForOf, NgIf } from '@angular/common';
import { MatCard, MatCardTitle } from '@angular/material/card';
import { MatIcon } from '@angular/material/icon';
import { HeaderComponent } from '../../shared/components/header/header.component';
import {QuizAttempt} from '../../shared/models/quiz-attempt';
import {MatExpansionPanel, MatExpansionPanelHeader, MatExpansionPanelTitle} from '@angular/material/expansion';
import {MatDivider} from '@angular/material/divider';

@Component({
  selector: 'app-quiz-history',
  standalone: true,
  imports: [
    CommonModule,
    DatePipe,
    NgForOf,
    NgIf,
    MatCard,
    MatIcon,
    HeaderComponent,
    MatExpansionPanel,
    MatExpansionPanelTitle,
    MatDivider,
    MatExpansionPanelHeader
  ],
  templateUrl: './quiz-history.component.html',
  styleUrls: ['./quiz-history.component.scss']
})
export class QuizHistoryComponent implements OnInit {
  attempts: QuizAttempt[] = [];
  loading = true;
  showSessionExpiredMessage = false;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.http.get<QuizAttempt[]>('https://bachelorthesis-production-8acf.up.railway.app/quiz/history').subscribe({
      next: (data) => {
        this.attempts = data;
        this.loading = false;
      },
      error: (err) => {
        this.loading = false;
        if (err.status === 401) {
          this.showSessionExpiredMessage = true;
        }
        console.error('Failed to load quiz history:', err);
      }
    });
  }
}
