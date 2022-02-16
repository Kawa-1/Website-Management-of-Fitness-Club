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
  public usersUsername:any = "elo";
  public myToken: MyToken = new MyToken();
  public user_id:any;


  constructor(
    private auth: AuthService, 
    private cookieService: CookieService, 
    private toastr: ToastrService 
  ){}

  ngOnInit(): void {
    const token = this.cookieService.get('token');
    console.log(token)
    if (token) {
      this.auth.ensureAuthenticated(token)
      .then((user) => {
        if (user.status === 'success') {
          this.isLoggedIn = true;
          this.usersUsername = user.data.username;
          this.user_id = user.data.user_id;
        }
      })
      .catch((err) => {
        this.isLoggedIn = false;
      });
    }
    else{
      this.isLoggedIn = false;
    }
  }

  logout(){
    this.myToken.token = this.cookieService.get('token');
    if (this.myToken) {
      this.auth.logout(this.myToken)
      .then((data) => {
        if (data.status === 'success') {
          this.toastr.success('Logged out successfully');
          timer(1500).subscribe(x => { this.isLoggedIn = false;})
          this.cookieService.delete('token')
        }
      });
    }
  }
}
