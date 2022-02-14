import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient, HttpErrorResponse } from '@angular/common/http';
import { User } from '../models/User';
import { Observable, throwError } from 'rxjs';
import { MyToken } from '../models/MyToken';
import { catchError, map } from 'rxjs/operators';
// import 'rxjs/add/operator/toPromise';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private path = "http://localhost:5000/api";
  private headers: HttpHeaders = new HttpHeaders({'Content-Type': 'application/json',
                                                  'Access-Control-Allow-Origin': '*'});
  constructor(
    private http: HttpClient
  ){}

  // login(user: User): Promise<any> {
  //   let url: string = this.path + "/login";
  //   return this.http.post(url, user, {headers: this.headers}).toPromise();
  // }

  login(user: User) {
    let url: string = this.path + "/login";
    return this.http.post(url, user);
  }

  ensureAuthenticated(token:any): Promise<any> {
    let url: string = this.path + "/status";
    let headers: HttpHeaders = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}` 
    });
    return this.http.get(url, {headers: headers}).toPromise();
  }

  logout(token:MyToken): Promise<any> {
    let url: string = this.path + "/logout";
    return this.http.post(url, token, {headers: this.headers}).toPromise();
  }

  register(form:FormData) {
    let url: string = this.path + "/register";
    return  this.http.post(url, form)
  }

}
