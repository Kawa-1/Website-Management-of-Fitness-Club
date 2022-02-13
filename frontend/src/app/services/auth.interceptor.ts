import { HttpErrorResponse, HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { ToastrService } from "ngx-toastr";
import { Observable, throwError } from "rxjs";
import { catchError } from "rxjs/operators";

@Injectable()
export class AuthInterceptor implements HttpInterceptor{
    constructor(private toastr:ToastrService){}

    intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<unknown>>{

        return next.handle(req)
            .pipe(  
                catchError((error: HttpErrorResponse) => {
                    if(req.url=="http://localhost:5000/api/register"){
                        this.toastr.error('Email already in use');
                    }
                    else if(req.url=="http://localhost:5000/api/login"){
                        this.toastr.error(error.error.message);
                    }
                    else if(req.url=="http://localhost:5000/api/status"){
                    }
                    else{
                        this.toastr.error('There was an issue');
                    }
                    
                    return throwError(error);
                }))
    }
}
