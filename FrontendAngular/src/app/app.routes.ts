import { Routes } from '@angular/router';
import {DashboardComponent} from './features/dashboard/dashboard.component';
import {ManualAnalyzeComponent} from './features/manual-analyze/manual-analyze.component';
import {AuthGuard} from './core/guards/auth.guard';


export const routes: Routes = [
  { path: '', component: ManualAnalyzeComponent },
  { path: 'manual-analyze', component: ManualAnalyzeComponent },
  { path: 'dashboard', component: DashboardComponent },// canActivate: [AuthGuard] },
  { path: '**', redirectTo: '' }
];

