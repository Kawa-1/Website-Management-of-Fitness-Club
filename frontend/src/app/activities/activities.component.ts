import { BodyDate } from './../models/BodyDate';
import { Component, HostListener, OnInit, ViewChild } from '@angular/core';
import { BsDatepickerDirective } from 'ngx-bootstrap/datepicker';
import { AuthService } from '../services/auth.service';
import { FormGroup, FormControl, Validators} from '@angular/forms'; 
import { CookieService } from 'ngx-cookie-service';
import { ToastrService } from 'ngx-toastr';
import { DatePipe } from '@angular/common';
import { BodyId } from '../models/BodyId';

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
  public datePickSearch = new Date();
  public minDate = new Date();
  public maxDate = new Date();
  public instructors$: any = [];
  public facilities$: any = [];
  public activities$: any = [];
  public allActvities$: any =[];
  public user_id: any;
  public usersUsername: any = "";
  public price_id: any;
  public hours$: any = [];
  public minutes$ = [0, 15, 30, 45];
      
  // form1 = new FormGroup({  
  //   instructor: new FormControl('', Validators.required)  
  // }); 

  form1 = new FormGroup({  
    activity: new FormControl('', Validators.required)  
  });

  form2 = new FormGroup({  
    facility: new FormControl('', Validators.required)  
  });

  form3 = new FormGroup({  
    hour: new FormControl('', Validators.required)  
  });

  form4 = new FormGroup({  
    minute: new FormControl('', Validators.required)  
  });

  constructor(
    private auth: AuthService,
    private cookieService: CookieService, 
    private toastr: ToastrService,
    private datepipe: DatePipe,
  ){
  }

  ngOnInit(): void {
    this.maxDate.setDate( this.maxDate.getDate() + 90 );

    for (let i = 13; i < 22; i++) {
      this.hours$.push(i)
    }

    const token = this.cookieService.get('token');
    if (token){
      this.auth.ensureAuthenticated(token)
      .then((user) => {
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

    this.auth.getActivities()
    .then((data)=>{
      this.allActvities$ = data.activities;
    })
  }

  search(): void{
    let latest_date =this.datepipe.transform(this.datePickSearch, 'yyyy-MM-dd');

    this.auth.getDateActivities(latest_date)
    .then((data)=>{
      this.allActvities$ = data.activities;
    })
  }


  openAdd(): void{
    this.openForm = false;

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
    if(this.form1.value.activity != "" && this.form2.value.facility != ""  && this.form3.value.hour != "" && this.form4.value.minute != ""){
      var array1 = this.form1.value.activity.split('.');
      var type_of_service_id: number = +array1[0];

      var array2 = this.form2.value.facility.split('.');
      var facility_id: number = +array2[0];

      var formData: any = new FormData();

      this.datePick.setHours(this.form3.value.hour, this.form4.value.minute)
      let latest_date =this.datepipe.transform(this.datePick, 'yyyy-MM-dd HH-mm');

      formData.append("date", latest_date);
      formData.append("type_of_service_id", type_of_service_id);
      formData.append("facility_id", facility_id);

      this.auth.addActivity(formData).subscribe(
        data => {
          this.toastr.success('Added activity');
        }
      );

      formData.delete("date");
      formData.delete("type_of_service_id");
      formData.delete("facility_id");
    }
  }
  
  signUp(id: any):void {
    let bodyId = new BodyId();
    bodyId.id = id;
    this.auth.signUpActivity(bodyId).then(
      data=>{
        if(data.message.status === 201){
          this.toastr.success("Here you would proceed to buy")
        }
        else{
          this.toastr.error(data.message.description)
        }
      }
    )
    this.auth.getActivities()
    .then((data)=>{
      this.allActvities$ = data.activities;
    })
  }

  useSub(id:any, date:any):void {
    let bodyDate = new BodyDate
    bodyDate.date = date.substring(0,10);
    let bodyId = new BodyId();
    bodyId.id = id;
    this.auth.checkIfSubbed(bodyDate).then(
      data=>{
        if(data.message.description ==='Valid subscriptions returned'){
          this.auth.signUpActivity(bodyId).then(
            data=>{
              if(data.message.status === 201){
                this.toastr.success("Succesfully signed on with subscription")
              }
              else{
                this.toastr.error(data.message.description)
              }
          })
        }
        else{
          this.toastr.error("Buy a subscription first")
        }
      }
    )
  }

  goBack(): void {
    this.openForm = true;
  }
}
