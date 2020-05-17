import { Component, OnInit, Input } from '@angular/core';
import { THIS_EXPR } from '@angular/compiler/src/output/output_ast';

@Component({
  selector: 'app-navigator',
  templateUrl: './navigator.component.html',
  styleUrls: ['./navigator.component.css']
})
export class NavigatorComponent implements OnInit {

  page: number = 0
  morePages: boolean
  @Input() maxItems: number = 6
  
  constructor() { }

  ngOnInit() {
  }

  incPage(){
    this.page++
  }

  decPage(){
    this.page--
  }

  view(source: any[]): any[]{
    if(!source)
      return []
    let Result: any[] = []
    const step: number = (this.page * this.maxItems)
    for (let i = step; i < source.length; i++) {      
      Result.push(source[i])
      if(Result.length == this.maxItems)
        break        
    }
    const pageCount: number = source.length / this.maxItems
    this.morePages = this.page < pageCount-1
    return Result
  }

}
