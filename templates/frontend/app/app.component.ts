import { Component, OnInit } from '@angular/core';
import { AuthService } from './shared/auth-service'

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html'
})
export class AppComponent implements OnInit {
  title = 'app';

  constructor(
    private authSvc: AuthService
  ) { }

  ngOnInit() {
    this.authSvc.handShake()
  }

}
