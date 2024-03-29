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

  login(user: User): Promise<any> {
    let url: string = this.path + "/login";
    return this.http.post(url, user).toPromise();
  }

  // login(user: User) {
  //   let url: string = this.path + "/login";
  //   return this.http.post(url, user);
  // }

  ensureAuthenticated(token:any): Promise<any> {
    let url: string = this.path + "/status";
    let headers: HttpHeaders = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}` 
    });
    return this.http.get(url, {headers: headers}).toPromise();
  }

  logout(token:any): Promise<any> {
    let url: string = this.path + "/logout";
    let headers: HttpHeaders = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}` 
    });
    return this.http.post(url, {headers: headers}).toPromise();
  }

  register(form:FormData) {
    let url: string = this.path + "/register";
    return this.http.post(url, form)
  }

  getInstructors(): Promise<any>{
    let url: string = this.path + "/instructors";
    return this.http.get(url).toPromise();
  }

  getFacilities(): Promise<any>{
    let url: string = this.path + "/facilities";
    return this.http.get(url).toPromise();
  }

  getTypesActivities(): Promise<any>{
    let url: string = this.path + "/activity_services";
    return this.http.get(url).toPromise();
  }

  getTypesSubscriptions(): Promise<any>{
    let url: string = this.path + "/subscription_services";
    return this.http.get(url).toPromise();
  }

  getActivities(): Promise<any>{
    let url: string = this.path + "/activity_api/?since_today=1";
    return this.http.get(url).toPromise();
  }

  getDateActivities(date:any): Promise<any>{
    let url: string = this.path + `/activity_api/${date}`;
    return this.http.get(url).toPromise();
  }

  getPrice(service_id: any): Promise<any>{
    let url: string = this.path + `/price_on_service/${service_id}`;
    return this.http.get(url).toPromise();
  }

  startSubscription(sub: any): Promise<any>{
    let url: string = this.path + `/start_subscription`;
    return this.http.post(url, sub).toPromise();
  }

  addActivity(form:FormData) {
    let url: string = this.path + "/instructors";
    return this.http.put(url, form)
  }

  signUpActivity(id:any): Promise<any> {
    let url: string = this.path + "/user_activity";
    return this.http.post(url, id).toPromise();
  }

  checkIfSubbed(date: any): Promise<any> {
    let url: string = this.path + "/user_valid_subscriptions";
    return this.http.post(url, date).toPromise();
  }

  getUserActivity(): Promise<any> {
    let url: string = this.path + "/user_activity";
    return this.http.get(url).toPromise();
  }
  
  signOff(id:any): Promise<any> {
    let url: string = this.path + `/user_activity/${id}`;
    return this.http.delete(url).toPromise();
  }

  getUserSubs(): Promise<any> {
    let url: string = this.path + "/user_subscriptions";
    return this.http.get(url).toPromise();
  }
}
