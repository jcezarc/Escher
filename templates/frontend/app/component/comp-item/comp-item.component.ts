import { Component, OnInit, Input } from '@angular/core';
import { %table%Model } from '../%table%-model';

@Component({
  selector: 'app-%table%-item',
  templateUrl: './%table%-item.component.html',
  styleUrls: ['./%table%-item.component.css']
})
export class %table%ItemComponent implements OnInit {

  @Input() %table%: %table%Model

  constructor() { }

  ngOnInit() {
  }

}
