import { Component, OnInit } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { MyToken } from '../models/MyToken';
import { timer} from 'rxjs';
import { CookieService } from 'ngx-cookie-service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-your-profile',
  templateUrl: './your-profile.component.html',
  styleUrls: ['./your-profile.component.css']
})
export class YourProfileComponent implements OnInit {
  public isLoggedIn: boolean = false;
  public usersUsername:any = "";
  public user_id:any;
  public activities$: any[] = [];
  public subscriptions$: any[] = [];

  constructor(
    private auth: AuthService, 
    private cookieService: CookieService, 
    private toastr: ToastrService 
  ){}

  ngOnInit(): void {
    const token = this.cookieService.get('token');
    if (token) {
      this.auth.ensureAuthenticated(token)
      .then((user) => {
        if (user.message.status === 200) {
          this.isLoggedIn = true;
          this.usersUsername = user.user.first_name;
          this.user_id = user.user.user_id;
        }
      })
      .catch((err) => {
        this.isLoggedIn = false;
      });
    }
    else{
      this.isLoggedIn = false;
    }

    this.auth.getUserActivity().then(
      data=>{
        this.activities$ = data.activities;
      }
    )

    this.auth.getUserSubs().then(
      data=>{
        this.subscriptions$ = data.subscriptions;
      }
    )
    
  }

  signOff(id:any): void{
    this.auth.signOff(id).then(
      data=>{
        if(data.message.status === 202){
          this.toastr.success("User properly signed off the activity")
        }
      }
    )
  }

  logout(): void{
    const token = this.cookieService.get('token');
    if (token) {
      this.auth.logout(token)
      .then((data) => {
        console.log(data)
        if (data.message.status === 200) {
          this.toastr.success('Logged out successfully');
          timer(1500).subscribe(x => { this.isLoggedIn = false;})
          this.cookieService.delete('token')
        }
      });
    }
  }
}
