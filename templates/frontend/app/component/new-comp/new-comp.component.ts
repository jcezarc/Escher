import { Component, OnInit } from '@angular/core';
import { %table%Model } from '../%table%-model';
import { %table%Service } from '../%table%-service';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
%new-nested_import%

@Component({
  selector: 'app-new-%table%',
  templateUrl: './new-%table%.component.html'
})
export class New%table%Component implements OnInit {

  %table%Form: FormGroup

  constructor(
    private %table%Svc: %table%Service,
    private formBuilder: FormBuilder,
    private router: Router
  ) { }

  ngOnInit() {
    this.router.onSameUrlNavigation = "reload"
    this.%table%Form = this.formBuilder.group({
%new-field_list%
%new-nested%
    })
  }

}
