import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';


@Component({
  selector: 'app-search-bar',
  templateUrl: './search-bar.component.html'
})
export class SearchBarComponent implements OnInit {

  @Output() filter = new EventEmitter()
  @Output() add = new EventEmitter()

  searchForm: FormGroup

  constructor(private formBuilder: FormBuilder) { }

  ngOnInit() {
    this.searchForm = this.formBuilder.group({
      searchContent: this.formBuilder.control('')
    })
  }

  emitFilterEvent(param: any){
    this.filter.emit(param)
  }

  emitAddEvent(){
    this.add.emit('')
  }

}
