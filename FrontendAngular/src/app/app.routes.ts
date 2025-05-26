import { Routes } from '@angular/router';
import {DashboardComponent} from './features/dashboard/dashboard.component';
import {ManualAnalyzeComponent} from './features/manual-analyze/manual-analyze.component';
import {AuthGuard} from './core/guards/auth.guard';
import {QuizComponent} from './features/quiz/quiz.component';
import {QuizHistoryComponent} from './features/quiz-history/quiz-history.component';
import {StatsComponent} from './features/stats/stats.component';


export const routes: Routes = [
  { path: '', component: ManualAnalyzeComponent },
  { path: 'manual-analyze', component: ManualAnalyzeComponent },
  { path: 'dashboard', component: DashboardComponent },//  canActivate: [AuthGuard] },
  { path: 'quiz', component: QuizComponent }, //, canActivate: [AuthGuard] },
  { path: 'quiz-history', component: QuizHistoryComponent }, //, canActivate: [AuthGuard] }
  { path: 'stats', component: StatsComponent },
  { path: '**', redirectTo: '' }
];



