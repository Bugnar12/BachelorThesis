import { Component, OnInit } from '@angular/core';
import { GmailService } from '../../core/services/gmail.service';
import { EmailStats } from '../../shared/models/email-stats';
import { ChartData, ChartOptions } from 'chart.js';

import { CommonModule, NgIf } from '@angular/common';
import { MatCard } from '@angular/material/card';
import { BaseChartDirective } from 'ng2-charts';
import { MatIcon } from '@angular/material/icon';

@Component({
  selector: 'app-stats',
  standalone: true,
  imports: [CommonModule, NgIf, MatCard, BaseChartDirective, MatIcon],
  templateUrl: './stats.component.html',
  styleUrls: ['./stats.component.scss']
})
export class StatsComponent implements OnInit {
  stats: EmailStats | null = null;
  isLoading = true;

  pieChartData:  ChartData<'pie',  number[], string> = { labels: [], datasets: [] };
  lineChartData: ChartData<'line', number[], string> = { labels: [], datasets: [] };

  readonly pieChartType  = 'pie';
  readonly lineChartType = 'line';

  constructor(private gmailService: GmailService) {}

  ngOnInit(): void {
    this.gmailService.getEmailStats().subscribe({
      next: data => {
        this.stats = data;
        this.buildCharts();
        this.isLoading = false;
      },
      error: err => {
        console.error('Failed to load stats:', err);
        this.isLoading = false;
      }
    });
  }

  get phishingPercentage(): number {
    return this.stats?.total
      ? Math.round((this.stats.phishing / this.stats.total) * 100)
      : 0;
  }

  readonly lineChartOptions: ChartOptions<'line'> = {
    responsive: true,
    elements: {
      point: { radius: 2, hitRadius: 12, hoverRadius: 6 }   // reliable hover
    },
    interaction: { mode: 'nearest', intersect: false }
  };

  private buildCharts(): void {
    if (!this.stats) return;

    /* pie chart */
    this.pieChartData = {
      labels: Object.keys(this.stats.detection_breakdown),
      datasets: [
        {
          data: Object.values(this.stats.detection_breakdown),
          backgroundColor: ['#1e88e5', '#1565c0', '#ef5350', '#66bb6a']
        }
      ]
    };

    /* line chart */
    const labels    = this.stats.timeline.map(e => e.date);
    const totals    = this.stats.timeline.map(e => e.count);
    const phishing  = this.stats.timeline.map(e => e.phishing ?? 0);

    this.lineChartData = {
      labels,
      datasets: [
        {
          data: totals,
          label: 'Emails',
          borderColor: '#1e88e5',
          borderWidth: 2,
          fill: false,
          pointRadius: 2,
          pointHitRadius: 12,
          pointHoverRadius: 6,
          pointBackgroundColor: '#1e88e5'
        },
        {
          data: phishing,
          label: 'Phishing',
          showLine: false,
          borderWidth: 0,
          pointRadius: 5,
          pointBackgroundColor: '#e53935',
          pointHoverRadius: 7,
          pointHitRadius: 12
        }
      ]
    };
  }
}
