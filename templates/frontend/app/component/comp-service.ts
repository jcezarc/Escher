import { Http, RequestOptions, Headers, Response } from "@angular/http";
import { Injectable } from "@angular/core";
import { Observable } from "../../../node_modules/rxjs";
import { %table%Model } from "./%table%-model";
import { RespJsonFlask, BASE_PATH_SERVER } from "../app.api";
import { AuthService } from '../shared/auth-service'

const %table%_API = `${BASE_PATH_SERVER}/%API_name%/%table%`


@Injectable()
export class %table%Service{

    static current%table%: %table%Model

    static getCurr%table%(){
        if(%table%Service.current%table%){
            return %table%Service.current%table%.%title%
        }else{
            return ''
        }
    }

    constructor(private http: Http){
    }

    all%table%s():Observable<Response>{
        return this.http.get(
            %table%_API
            ,new RequestOptions({headers: AuthService.header})
        )
    }

    %table%sByTitle(text: string):Observable<Response>{
        return this.http.get(
            `${%table%_API}?%title%=${text}`
            ,new RequestOptions({headers: AuthService.header})
        )
    }

    delete(%pk_field%: string): void{
        this.http.delete(
            `${%table%_API}/${%pk_field%}`
            ,new RequestOptions({headers: AuthService.header})
        ).subscribe(
            resp => {
                const obj:RespJsonFlask = (<RespJsonFlask>resp.json())
                let data:%table%Model = (<%table%Model>obj.data)
                console.log('"%table%.Delete" = ', data)
            }
        )
    }

    save%table%(newItem: %table%Model): void{
        this.http.post(
            %table%_API,
            JSON.stringify(newItem)
            ,new RequestOptions({headers: AuthService.header})
        ).subscribe(
            resp => {
                const obj:RespJsonFlask = (<RespJsonFlask>resp.json())
                let data:%table%Model = (<%table%Model>obj.data)
                console.log('"save%table%" = ', data)
            }
        )
    }

}