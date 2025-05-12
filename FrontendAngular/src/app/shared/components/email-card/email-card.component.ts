import { Component, Input } from '@angular/core';
import { Email } from '../../models/email';
import {DatePipe, NgClass, SlicePipe} from '@angular/common';

@Component({
  selector: 'app-email-card',
  templateUrl: './email-card.component.html',
  imports: [
    NgClass,
    SlicePipe,
    DatePipe
  ],
  styleUrls: ['./email-card.component.css']
})
export class EmailCardComponent {
  @Input() email!: Email;
}
