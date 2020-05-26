import { Http, RequestOptions, Headers, Response } from "@angular/http";
import { Injectable } from "@angular/core";
import { Observable } from "../../../node_modules/rxjs";
import { %table%Model } from "./%table%-model";
import { RespJsonFlask } from "../app.api";

const %table%_API = 'localhost:5000/%API_name%/%table%'


@Injectable()
export class %table%Service{

    constructor(private http: Http){
    }

    all%table%s():Observable<Response>{
        return this.http.get(
            %table%_API
        )
    }

    %table%sByTitle(text: string):Observable<Response>{
        return this.http.get(
            `${%table%_API}?%title%=${text}`,
        )
    }

    delete(%pk_field%: string): void{
        this.http.delete(
            `${%table%_API}/${%pk_field%}`
        ).subscribe(
            resp => {
                const obj:RespJsonFlask = (<RespJsonFlask>resp.json())
                let data:%table%Model = (<%table%Model>obj.data)
                console.log('"%table%.Delete" = ', data)
            }
        )
    }

    save%table%(newItem: %table%Model): void{
        const headers: Headers = new Headers()
        headers.append('Content-Type','application/json')
        this.http.post(
            `${%table%_API}/%table%`,
            JSON.stringify(newItem),
            new RequestOptions({headers:headers})
        ).subscribe(
            resp => {
                const obj:RespJsonFlask = (<RespJsonFlask>resp.json())
                let data:%table%Model = (<%table%Model>obj.data)
                console.log('"save%table%" = ', data)
            }
        )
    }

}