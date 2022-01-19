import { ToastrService } from 'ngx-toastr';
import { Component, OnInit } from '@angular/core';
// import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css'],
})

export class RegisterComponent implements OnInit{ 
  constructor( 
    private toastr: ToastrService, 
    // private auth: AuthService 
  ) {}
 
  isDisabled = true;
  passwordPattern= "";

  ngOnInit(){}

  clicked(email:string, firstName:string, lastName:string, username:string, password:string, repeatPassword: string){
    var formData: any = new FormData();

    formData.append("email", email);
    formData.append("firstName", firstName);
    formData.append("lastName", lastName);
    formData.append("username", username);
    formData.append("password", password);
    formData.append("repeatPassword", repeatPassword);

    // this.auth.register(formData)
    // .subscribe(
    //   data => {
    //       this.toastr.success('Registered successfully');
    //   });

    formData.delete("email");
    formData.delete("firstName");
    formData.delete("lastName");
    formData.delete("username");
    formData.delete("password");
    formData.delete("repeatPassword");
  }

  getPassword(s:string){
    this.passwordPattern = s;
  }

  getMsgFromBaby() {
    this.isDisabled = false;
  }
}
