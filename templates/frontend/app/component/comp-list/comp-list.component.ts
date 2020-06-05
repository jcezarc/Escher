import { Component, OnInit } from '@angular/core';
import { %table%Model } from '../%table%-model';
import { %table%Service } from '../%table%-service';
import { Router } from '@angular/router';
import {RespJsonFlask} from '../../app.api'

@Component({
  selector: 'app-%table%-list',
  templateUrl: './%table%-list.component.html'
})
export class %table%ListComponent implements OnInit {

  items: %table%Model[] = []

  constructor(
    private %table%Svc: %table%Service,
    private router: Router
  ) { }

  ngOnInit() {
    this.router.onSameUrlNavigation = "reload"
    this.%table%Svc.all%table%s().subscribe(
      resp => {
        let obj:RespJsonFlask = (<RespJsonFlask>resp.json())
        this.items = (<%table%Model[]>obj.data)
      }
    )
  }

  filter(param: any){
    this.%table%Svc.%table%sByTitle(param.searchContent).subscribe(
      resp => {
        let obj:RespJsonFlask = (<RespJsonFlask>resp.json())
        this.items = (<%table%Model[]>obj.data)
      }
    )
  }

  add(){
    this.router.navigate(['/new-%table%'])
  }

  remove(item: %table%Model){
    if(!confirm(`Remove %table% "${item.%title%}" ?`)){
      return
    }
    this.%table%Svc.delete(item.%pk_field% as unknown as string)
    this.items.splice(this.items.indexOf(item),1)
  }

  save(item: %table%Model){
    %saveImage%
    this.%table%Svc.save%table%(item)
    this.items.push(item)
  }

  select(item: %table%Model){
    this.%table%Svc.current%table% = item
    this.router.navigate(['/new-%nesting_ref%'])
  }

}
