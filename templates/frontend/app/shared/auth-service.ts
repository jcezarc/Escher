import { Injectable } from "@angular/core";
import { Http, RequestOptions, Headers } from "@angular/http";
import { JWTResponse, BASE_PATH_SERVER } from "../app.api";

const HandShakeURL = `${BASE_PATH_SERVER}/handshake`

@Injectable()
export class AuthService{

    static header: Headers

    constructor(
        private http:Http
    ){}

    getHeaders(token: string=''): Headers{
        const Result = new Headers()
        Result.append('Content-Type','application/json')
        if(token){
            Result.append(
                'Authorization',
                `Bearer ${token}`
            )
        }
        Result.append('Access-Control-Allow-Origin','*')
        return Result
    }

    handShake(){
        const profile = {
            user: 'development',
            password: '123'
        }
        const headers: Headers = this.getHeaders()
        this.http.post(
            HandShakeURL,
            JSON.stringify(profile),
            new RequestOptions({headers:headers})
        ).subscribe(
            resp => {
                const obj:JWTResponse = (<JWTResponse> resp.json())
                AuthService.header = this.getHeaders(
                    obj.access_token
                )
            }
        )
    }
}