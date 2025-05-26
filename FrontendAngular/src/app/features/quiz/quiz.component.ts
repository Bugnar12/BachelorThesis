import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { QuizQuestion } from '../../shared/models/quiz-question';
import { MatCard, MatCardTitle } from '@angular/material/card';
import { MatRadioButton, MatRadioGroup } from '@angular/material/radio';
import { CommonModule, NgForOf, NgIf } from '@angular/common';
import { MatButton } from '@angular/material/button';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { MatIcon } from '@angular/material/icon';
import { HeaderComponent } from '../../shared/components/header/header.component';

@Component({
  selector: 'app-quiz',
  templateUrl: './quiz.component.html',
  standalone: true,
  imports: [
    MatCardTitle,
    MatRadioGroup,
    MatRadioButton,
    NgIf,
    NgForOf,
    MatButton,
    FormsModule,
    CommonModule,
    MatCard,
    MatIcon,
    HeaderComponent
  ],
  styleUrls: ['./quiz.component.scss']
})
export class QuizComponent implements OnInit {
  questions: QuizQuestion[] = [];
  selectedAnswers: { [id: number]: string } = {};
  loading = true;
  submitted = false;
  showSessionExpiredMessage = false;
  score: number = 0;
  total: number = 0;

  constructor(private http: HttpClient, private route: ActivatedRoute) {
    this.route.queryParams.subscribe(params => {
      if (params['session_expired'] === 'true') {
        this.showSessionExpiredMessage = true;
      }
    });
  }

  ngOnInit(): void {
    this.http.get<QuizQuestion[]>('http://localhost:5000/quiz/questions').subscribe({
      next: (data) => {
        this.questions = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load quiz questions', err);
        this.loading = false;
      }
    });
  }

  selectAnswer(questionId: number, option: string) {
    this.selectedAnswers[questionId] = option;
  }

  submitQuiz() {
    this.submitted = true;

    const answersPayload = this.questions.map(q => ({
      question_id: q.id,
      selected_option: this.selectedAnswers[q.id]
    }));

    this.http.post('http://localhost:5000/quiz/submit', { answers: answersPayload }).subscribe({
      next: (res: any) => {
        console.log('Quiz submitted successfully', res);
        this.score = res.score;
        this.total = res.total;
      },
      error: (err) => {
        console.error('Failed to submit quiz:', err);
      }
    });
  }
}
