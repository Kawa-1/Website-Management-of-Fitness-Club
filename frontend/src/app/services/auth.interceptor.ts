import { HttpErrorResponse, HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { CookieService } from "ngx-cookie-service";
import { ToastrService } from "ngx-toastr";
import { Observable, throwError } from "rxjs";
import { catchError } from "rxjs/operators";

@Injectable()
export class AuthInterceptor implements HttpInterceptor{
    constructor(private toastr:ToastrService, private cookieService: CookieService, ){}

    intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<unknown>>{

        if(req.url=="http://localhost:5000/api/logout" || 
           req.url=="http://localhost:5000/api/start_subscription" || 
           req.url=="http://localhost:5000/api/instructors"){

            let authToken = `Bearer ${this.cookieService.get('token')}`
            
            if (authToken) {
                req = req.clone({
                    setHeaders: {
                    ['Authorization']: authToken
                    }
                });
            }

            return next.handle(req);
        }

        return next.handle(req)
            .pipe(  
                catchError((error: HttpErrorResponse) => {
                    if(req.url=="http://localhost:5000/api/register"){
                        this.toastr.error('Email already in use');
                    }
                    else if(req.url=="http://localhost:5000/api/login"){
                        this.toastr.error(error.error.message.description);
                    }
                    // else if(req.url=="http://localhost:5000/api/"){
                    //     this.toastr.error(error.error.message.description);
                    // }
                    else if(req.url=="http://localhost:5000/api/status"){
                    }
                    else{
                        this.toastr.error('There was an issue');
                    }
                    
                    return throwError(error);
                }))
    }
}
