import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-delete-button',
  templateUrl: './delete-button.component.html',
  styleUrls: ['./delete-button.component.css']
})
export class DeleteButtonComponent implements OnInit {

  @Output() delete = new EventEmitter()


  constructor() { }

  ngOnInit() {
  }

  emitEventDelete(){
    this.delete.emit()
  }

}
