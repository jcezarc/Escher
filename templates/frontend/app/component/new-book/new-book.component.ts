import { Component, OnInit } from '@angular/core';
import { BookModel } from '../book.model';
import { BookService } from '../book.service';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-new-book',
  templateUrl: './new-book.component.html'
})
export class NewBookComponent implements OnInit {

  bookForm: FormGroup

  constructor(
    private bookSvc: BookService,
    private formBuilder: FormBuilder,
    private router: Router
  ) { }

  ngOnInit() {
    this.router.onSameUrlNavigation = "reload"
    this.bookForm = this.formBuilder.group({
      book_id: this.formBuilder.control('',[Validators.required]),
      title: this.formBuilder.control('',[Validators.required]),
      author: this.formBuilder.control('',[Validators.required]),
      about: this.formBuilder.control('',[Validators.required])
    })
  }

}
