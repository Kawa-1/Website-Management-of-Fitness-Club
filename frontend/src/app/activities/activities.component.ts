import { Component, HostListener, OnInit, ViewChild } from '@angular/core';
import { BsDatepickerDirective } from 'ngx-bootstrap/datepicker';
import { AuthService } from '../services/auth.service';
import { FormGroup, FormControl, Validators} from '@angular/forms'; 
import { CookieService } from 'ngx-cookie-service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-activities',
  templateUrl: './activities.component.html',
  styleUrls: ['./activities.component.css']
})
export class ActivitiesComponent implements OnInit {
  @ViewChild(BsDatepickerDirective, { static: false }) datepicker?: BsDatepickerDirective;

  @HostListener('window:scroll')
  onScrollEvent() {
    this.datepicker?.hide();
  }

  public isLoggedIn: boolean = false;
  public isInstructor: boolean = false;
  public isDisabled = true;
  public openForm: boolean = true;
  public datePick = new Date();
  public minDate = new Date();
  public maxDate = new Date();
  public instructors$: any = [];
  public facilities$: any = [];
  public activities$: any = [];
  public user_id:any;
  public usersUsername:any = "";

      
  form = new FormGroup({  
    website: new FormControl('', Validators.required)  
  });  
    
  get f(){  
    return this.form.controls;  
  }  
    
  submit(){  
    console.log(this.form.value);  
  }  

  constructor(
    private auth: AuthService,
    private cookieService: CookieService, 
    private toastr: ToastrService
  ){
  }

  ngOnInit(): void {
    const token = this.cookieService.get('token');
    if (token){
      this.auth.ensureAuthenticated(token)
      .then((user) => {
        console.log(user)
        if (user.message.status === 200) {
          this.isLoggedIn = true;
          this.usersUsername = user.user.first_name;
          this.user_id = user.user.user_id;
          if (user.user.is_instructor === 1){
            this.isInstructor = true
          }
        }
      })
      .catch((err) => {
        this.openForm = true;
      });
    }
    else{
      this.openForm = true;
    }
  }

  openAdd(): void{
    this.openForm = false;

    this.maxDate.setDate( this.maxDate.getDate() + 90 );
    this.auth.getInstructors().then(
      data => {
        this.instructors$ = data.instructors;
      }
    )
    this.auth.getFacilities().then(
      data => {
        this.facilities$ = data.facilities;
      }
    )

    this.auth.getTypesActivities().then(
      data => {
        this.activities$ = data.activities;
      }
    )
  }

  addActivity(): void{
    console.log(this.datePick)
  }

  goBack(): void {
    this.openForm = true;
  }
}
