import { Component } from '@angular/core';
import {MatToolbar} from '@angular/material/toolbar';
import {MatAnchor, MatIconButton} from '@angular/material/button';
import {Router, RouterLink} from '@angular/router';
import {MatIcon} from '@angular/material/icon';
import {AuthService} from '../../../core/services/auth.service';

@Component({
  selector: 'app-navbar',
  imports: [
    MatToolbar,
    MatAnchor,
    RouterLink,
    MatIcon,
    MatIconButton
  ],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.scss'
})
export class NavbarComponent {
  constructor(private auth: AuthService, private router: Router) {
  }

  /** clears JWTs and returns to landing page */
  logout(): void {
    this.auth.logout();                  // removes tokens from localStorage
    this.router.navigate(['/']);         // send user to login / landing
  }
}
