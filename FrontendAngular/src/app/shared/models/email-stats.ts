import {TimelineEntry} from './timeline-entry';

export interface EmailStats {
  total: number;
  phishing: number;
  legitimate: number;
  detection_breakdown: Record<string, number>;
  timeline: TimelineEntry[];
}
