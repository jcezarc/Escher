import { Component, OnInit } from '@angular/core';
import { BookModel } from '../book.model';
import { BookService } from '../book.service';
import { Router } from '@angular/router';
import {RespJsonPack} from '../../app.api'

const ITEMS_PER_PAGE = 4

@Component({
  selector: 'app-book-list',
  templateUrl: './book-list.component.html'
})
export class BookListComponent implements OnInit {

  books: BookModel[]

  constructor(
    private bookSvc: BookService,
    private router: Router
  ) { }

  ngOnInit() {
    this.router.onSameUrlNavigation = "reload"
    this.bookSvc.allBooks().subscribe(
      resp => {
        let obj:RespJsonPack = (<RespJsonPack>resp.json())
        this.books = (<BookModel[]>obj.data)
      }
    )
  }

  filter(param: any){
    this.bookSvc.booksByTitle(param.searchContent).subscribe(
      resp => {
        let obj:RespJsonPack = (<RespJsonPack>resp.json())
        this.books = (<BookModel[]>obj.data)
      }
    )
  }

  add(){
    this.router.navigate(['/new-book'])
  }

  remove(item: BookModel){
    if(!confirm(`Deseja excluir o livro "${item.title}" ?`)){
      return
    }
    this.bookSvc.delete(item.book_id)
    this.books.splice(this.books.indexOf(item),1)
  }

  save(item: BookModel){
    item.imagePath = `assets/img/books/${item.book_id}.jpg`
    this.bookSvc.saveBook(item)
    this.books.push(item)
  }

}
