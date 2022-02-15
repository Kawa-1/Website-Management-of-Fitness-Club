import { ToastrService } from 'ngx-toastr';
import { Component } from '@angular/core';
import { CookieService } from 'ngx-cookie-service';
import { User } from '../models/User';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  constructor( 
    private auth: AuthService, 
    private cookieService: CookieService, 
    private toastr: ToastrService  
  ) {}

  user: User = new User();

  onLogin(email:string, password:string): void {
    this.user.email = email;
    this.user.password = password;

    this.auth.login(this.user)
    .then((user) => {
      console.log(user)
      this.cookieService.set('token', user.token);
      this.toastr.success('Logged in succesfully');
    });

    // var formData: any = new FormData();

    // formData.append("email", email);
    // formData.append("password", password);

    // this.user.email = email;
    // this.user.password = password;

    // this.auth.login(formData)
    // .subscribe(
    //   data => {
    //     console.log(data)
    //   // this.cookieService.set('token', user.token);
    //   // this.toastr.success('Logged in succesfully');
    // });
  }

  clicked(email:string, password:string){
    this.onLogin(email, password);
  }
}