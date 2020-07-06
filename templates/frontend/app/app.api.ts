export interface RespJsonFlask{
    data: any,
    timeStamp: string,
    status: string
}

export interface JWTResponse{
    access_token: string
}

export const BASE_PATH_SERVER = 'http://localhost:5000'
