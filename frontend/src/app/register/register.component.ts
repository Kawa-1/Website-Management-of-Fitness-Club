import { ToastrService } from 'ngx-toastr';
import { Component, OnInit } from '@angular/core';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css'],
})

export class RegisterComponent implements OnInit{ 
  constructor( 
    private toastr: ToastrService, 
    private auth: AuthService 
  ) {}
 
  isDisabled = true;
  passwordPattern= "";

  ngOnInit(){}

  clicked(email:string, firstName:string, lastName:string, city:string, street:string, house_nr:string, postcode:string, password:string, repeatPassword: string){
    var formData: any = new FormData();

    formData.append("email", email);
    formData.append("first_name", firstName);
    formData.append("last_name", lastName);
    formData.append("city", city);
    formData.append("street", street);
    formData.append("house_number", house_nr);
    formData.append("postcode", postcode);
    formData.append("password", password);
    formData.append("repeat_password", repeatPassword);

    this.auth.register(formData)
    .subscribe(
      data => {
          this.toastr.success('Registered successfully');
      });

    formData.delete("email");
    formData.delete("first_name");
    formData.delete("last_name");
    formData.delete("city");
    formData.delete("street");
    formData.delete("house_number");
    formData.delete("postcode");
    formData.delete("password");
    formData.delete("repeat_password");
  }

  getPassword(s:string){
    this.passwordPattern = s;
  }

  getMsgFromBaby() {
    this.isDisabled = false;
  }
}
