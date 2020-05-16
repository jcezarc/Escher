import { Http, RequestOptions, Headers, Response } from "@angular/http";
import { Injectable } from "@angular/core";
import { Observable } from "../../../node_modules/rxjs";
import { BookModel } from "./book.model";
import { BOOK_API, RespJsonPack } from "../app.api";


@Injectable()
export class BookService{

    constructor(private http: Http){
    }

    allBooks():Observable<Response>{
        return this.http.get(
            `${BOOK_API}/Book`
        )
    }

    booksByTitle(text: string):Observable<Response>{
        return this.http.get(
            `${BOOK_API}/Book?title=${text}`,
        )
    }

    delete(book_id: string): void{
        this.http.delete(
            `${BOOK_API}/Book/${book_id}`
        ).subscribe(
            resp => {
                const obj:RespJsonPack = (<RespJsonPack>resp.json())
                let data:BookModel = (<BookModel>obj.data)
                console.log('Resposta de "Book.Delete" = ', data)
            }
        )
    }

    saveBook(book: BookModel): void{
        const headers: Headers = new Headers()
        headers.append('Content-Type','application/json')
        this.http.post(
            `${BOOK_API}/Book`,
            JSON.stringify(book),
            new RequestOptions({headers:headers})
        ).subscribe(
            resp => {
                const obj:RespJsonPack = (<RespJsonPack>resp.json())
                let data:BookModel = (<BookModel>obj.data)
                console.log('REsposta de "saveBook" = ', data)
            }
        )
    }

}